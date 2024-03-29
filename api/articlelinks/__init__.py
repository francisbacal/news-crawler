from newscrawler import init_log, Options, extend_opt
from ..exceptions import articleLinksAPIError, DuplicateValue
from bson import json_util
from pprint import pprint

import requests, json, datetime, os

log = init_log("articleLinksAPI")


class ArticleLinks():
    def __init__(self, options=None, **kwargs):
        """
        Initialize method
        """
        self.options = options or Options()
        self.options = extend_opt(self.options, kwargs)
        self.headers = {"Content-Type" : "application/json", "Authorization": self.options.token}

        if self.options.testing:
            self.url = os.environ['ARTICLE_TEST_EP']
        else:
            self.url = os.environ['ARTICLE_EP']

    def default_schema(self, article_data: dict):
        """
        Generates a payload of article for adding
            @params:
                article_data        -   dict object of article details
        """
        try:
            article_url = article_data['article_url']
            website = article_data['website']
            fqdn = article_data['fqdn']
        except KeyError:
            raise articleLinksAPIError("Invalid article_data passed")

        schema = {
            "article_status": "Queued",
            "article_url": article_url,
            "article_source_url": fqdn,
            "website": website,
            "date_created": datetime.datetime.today().isoformat(),
            "date_updated": datetime.datetime.today().isoformat(),
            "article_source_from": "Python News Crawler",
            "created_by": "Python News Crawler",
            "updated_by": "Python News Crawler",
        }

        return schema
            
    def delete_test(self, _id):
        url = f"{os.environ['ARTICLE_TEST_EP']}{_id}"

        res = requests.delete(url,headers=self.headers)

        return res.json()['data']
        
    def __raise_errors(self, response, url):
        """
        Checks for response error and raises appropriate errors
            @params:
                response        -   requests response
                url             -   Endpoint url
        """
        if str(response.status_code).startswith('5'):
            if 'error' in response.json():
                try:
                    if response.json()['error']['code'] == 11000:
                        raise articleLinksAPIError(url, 'Duplicate Value')
                    else:
                        err_code = response.json()['error']['code']
                        err_name = response.json()['error']['name']
                        raise articleLinksAPIError(url, f"ERROR: {err_name} with code {err_code}")
                except KeyError:
                    raise articleLinksAPIError(url, "Unknown")
            else:
                raise articleLinksAPIError(url, response.status_code)
        
        if str(response.status_code).startswith('4'):
            raise articleLinksAPIError(url, response.status_code)
    
    def check_link(self, article_url: str, **kwargs):
        """
        Check links for duplicate article
            @params:
                article_url         -   url of article to check
                **kwargs            -   additional arguments to extend to options
        """
        url = self.url + "custom_query/"
        self.options = extend_opt(self.options, kwargs)
        params = {"limit": self.options.limit}

        if not article_url:
            raise articleLinksAPIError(url, "None type parameter for url")
        if not isinstance(article_url, str):
            raise articleLinksAPIError(url, "Type Error for url paramaeter")

        payload = {"article_url": article_url}

        try:
            response = requests.post(url, params=params, data=json.dumps(payload), headers=self.headers)

            self.__raise_errors(response, url)

            result = response.json()['data']

            #CHECK LENGTH OF RESULT
            if len(result) > 0:
                raise DuplicateValue("Article already exists in the database")

        except Exception as e:
            raise articleLinksAPIError(url, e)
    
    def get(self, body={}, params={}, **kwargs):
        """
        Get article links from the database
            @params:
                body            -   payload query to database
                params          -   additional parameter to be sent to headers
                **kwargs        -   additional parameters to extend to options
        """
        self.options = extend_opt(self.options, kwargs)

        url = self.url + "custom_query"

        params['limit'] = self.options.limit

        try:
            response = requests.post(url, params=params, data=json.dumps(body, default=json_util.default), headers=self.headers)

            self.__raise_errors(response, url)

            result = response.json()['data']

            return result

        except Exception as e:
            raise articleLinksAPIError(url, e)
    
    def add(self, body: dict):
        """
        Add new article to the database
            @params:
                body            -   Article payload to add to database
        """
        url = self.url
        
        if not body or not isinstance(body, dict):
            raise ValueError("Invalid body value")
        
        # CHECK FOR DUPLICATES
        self.check_link(body['article_url'])
      
        try:
            response = requests.post(url, data=json.dumps(body, default=json_util.default), headers=self.headers)
            self.__raise_errors(response, url)
        except:
            raise

        return response.json()['data']