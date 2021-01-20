from newscrawler import init_log, Options, extend_opt
from ..exceptions import websiteAPIError

import requests

log = init_log("WebsiteAPI")

class Website:
  """
    Class for website API
  """
  def __init__(self, options=None, **kwargs):

    self.params = kwargs
    self.url = 'http://192.168.3.143:4040/mmi-endpoints/v0/web/'
    self.options = options or Options()
    self.headers = {"Content-Type" : "application/json", "Authorization": self.options.token}

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
    
  def get_one(self, site_id=None):
    _id = site_id

    if not _id:
      raise websiteAPIError('Parameter error: None value for site_id')
    
    url = self.url + _id

    try:
      response = requests.get(url, headers=self.headers)

      self.__raise_errors(response, url)

      result = response.json()['data'][0]

      if not result:
        return None
      
      return result
    
    except Exception as e:
      raise websiteAPIError(url, e)
  
  def get(self, body={}, **kwargs):

    url = self.url + "custom_query/"
    self.options = extend_opt(self.options, kwargs)
    params = {'limit': self.options.limit}

    try:
      response = requests.post(url, params=params, data=json.dumps(body), headers=self.headers)

      self.__raise_errors(response, url)

      result = response.json()['data']

      return result

    except Exception as e:
      raise websiteAPIError(url, e)

  def update(self, body: dict={}, website_id: str=None):
    if not body:
      raise commonError(error="No valid data to be updated")
    
    url = self.url + website_id

    body['date_updated'] = datetime.datetime.now().isoformat()

    try:
      response = requests.put(url, data=json.dumps(body), headers=self.headers)
    
      self.__raise_errors(response, url)

      result = response.json()['data']
      
      if not result:
        return None
      
      return result    
    except Exception as e:
      raise websiteAPIError(url, f'Update Error: {e}')

  def counts(self, body: dict={}, **kwargs):
    self.options = extend_opt(self.options, kwargs)
    url = self.url + "count_custom_query"

    try:
      response = requests.post(url, data=json.dumps(body, default=json_util.default), headers=self.headers)
      self.__raise_errors(response, url)

      result = response.json()['data']

      if not result:
        return None

      return result
    except Exception as e:
      raise websiteAPIError(url, f"Count error: {e}")
  
  