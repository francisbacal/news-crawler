from newscrawler import init_log, Options, extend_opt
from ..exceptions import articleLinksAPIError

import requests, json

log = init_log("articleLinksAPI")


class ArticleLinks():
    def __init__(self, options=None, **kwargs):
        self.options = options or Options()
        self.options = extend_opt(self.options, kwargs)
        self.headers = {"Content-Type" : "application/json", "Authorization": self.options.token}
        self.url = "http://192.168.3.143:4040/mmi-endpoints/v0/global-link/"


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
