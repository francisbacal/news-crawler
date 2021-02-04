from newscrawler import init_log, Options, extend_opt
from ..exceptions import articleLinksAPIError, DuplicateValue
from bson import json_util
from pprint import pprint

import requests, json, datetime

log = init_log("articleLinksAPI")


class ArticleLinks():
    def __init__(self, options=None, **kwargs):
        self.options = options or Options()
        self.options = extend_opt(self.options, kwargs)
        self.headers = {"Content-Type" : "application/json", "Authorization": self.options.token}

        if self.options.testing:
            self.url = "http://192.168.3.143:4040/mmi-endpoints/v0/article-test/"
        else:
            self.url = "http://192.168.3.143:4040/mmi-endpoints/v0/article/"

    def default_schema(self, article_data: dict):
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
        url = f"http://192.168.3.143:4040/mmi-endpoints/v0/article-test/{_id}"

        res = requests.delete(url,headers=self.headers)

        return res.json()['data']
        
    def __raise_errors(self, response, url):
        if str(response.status_code).startswith('5'):
            if 'error' in response.json():
                if response.json()['error']['code'] == 11000:
                    raise websiteAPIError(url, 'Duplicate Value')
                else:
                    err_code = response.json()['error']['code']
                    err_name = response.json()['error']['name']
                    raise websiteAPIError(url, f"ERROR: {err_name} with code {err_code}")
            else:
                raise websiteAPIError(url, response.status_code)
        
        if str(response.status_code).startswith('4'):
            raise websiteAPIError(url, response.status_code)
    
    def check_link(self, article_url: str, **kwargs):
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
        except expression as identifier:
            pass
    
    def get(self, body={}, params={}, **kwargs):
    
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
        url = self.url
        
        if not body or not isinstance(body, dict):
            raise ValueError("Invalid body value")
        
        try:
            response = requests.post(url, data=json.dumps(body, default=json_util.default), headers=self.headers)
        
            if str(response.status_code).startswith('5'):

                if 'error' in response.json():
                    if response.json()['error']['code'] == 11000:
                        raise DuplicateValue(body['article_url'])
                    else:
                        err_code = response.json()['error']['code']
                        err_name = response.json()['error']['name']
                        err_msg = f"An error occurred while adding article: {err_name} with code {err_code}"
                    raise APIServerError(url, response.status_code, err_msg=err_msg)
                else:
                    raise APIServerError(url, response.status_code)
            
        except:
            raise

        return response.json()['data']