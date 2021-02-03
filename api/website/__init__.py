from newscrawler import init_log, Options, extend_opt, catch
from ..exceptions import websiteAPIError, DuplicateValue
from bson import json_util
from langdetect import detect
from bs4 import BeautifulSoup
from pprint import pprint
import requests,json,datetime, cloudscraper, copy

from .schema import WebsiteSchema

log = init_log("WebsiteAPI")

class Website:
  """
    Class for website API
  """
  def __init__(self, options=None, **kwargs):
    # self.url = 'http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/'
    self.url = 'http://192.168.3.143:4040/mmi-endpoints/v0/web/'
    self.options = options or Options()
    self.headers = {"Content-Type" : "application/json", "Authorization": self.options.token}

  def __raise_errors(self, response, url):
    if str(response.status_code).startswith('5'):
      if 'error' in response.json():
        try:
          if response.json()['error']['code'] == 11000:
            raise websiteAPIError(url, 'Duplicate Value')
          else:
            err_code = response.json()['error']['code']
            err_name = response.json()['error']['name']
            raise websiteAPIError(url, f"ERROR: {err_name} with code {err_code}")
        except KeyError:
          raise Exception(response.json()['error'])
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
  
  def get(self, body={}, params={}, **kwargs):
    
    self.options = extend_opt(self.options, kwargs)

    if self.options.raw_website:
      url = "http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/query"
    else:
      url = self.url + "custom_query"

    params['limit'] = self.options.limit

    try:
      response = requests.post(url, params=params, data=json.dumps(body, default=json_util.default), headers=self.headers)

      self.__raise_errors(response, url)

      result = response.json()['data']

      return result

    except Exception as e:
      raise websiteAPIError(url, e)

  def update(self, body: dict={}, website_id: str=None, **kwargs):
  
    # EXTEND KWARGS TO OPTIONS IF KEY EXISTS
    self.options = extend_opt(self.options, kwargs)

    if self.options.raw_website:
      url = f"http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/{website_id}"
      body['created_by'] = "Singapore Website Done"
    else:
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

    if self.options.raw_website:
      url = "http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/count"
    else:
      url = self.url + "count"

    try:
      response = requests.post(url, data=json.dumps(body, default=json_util.default), headers=self.headers)
      self.__raise_errors(response, url)

      result = response.json()['data']

      if not result:
        return None

      return result
    except Exception as e:
      raise websiteAPIError(url, f"Count error: {e}")

  def add(self, data={}, raw_id: str=None, **kwargs):

    # EXTEND KWARGS TO OPTIONS IF KEY EXISTS
    self.options = extend_opt(self.options, kwargs)

    if self.options.raw_website:
      url = "http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/query"
    else:
      url = self.url + "custom_query"

    # GET WEBSITE DETAILS FROM RAW WEBSITE
    raw_website = None

    if raw_id:

      QUERY = {
        "query": {
          "_id": raw_id
        }
      }

      raw_website = self.get(QUERY, limit=1, raw_website=True)[0]

    if raw_website and data:

      #CHECK IF EXISTING
      existing = self.__exists(raw_website)
      
      if existing:
        raise DuplicateValue("Duplicate Website in Database")
        
      else:
        body = self.__generate_add_body(data, raw_website)

    else:
      raise websiteAPIError(f"Invalid parameters passed on {self.add.__name__}")

    url = self.url
    
    try:
      response = requests.post(url, data=json.dumps(body), headers=self.headers)
    
      self.__raise_errors(response, url)

      result = response.json()['data']

      if not result:
        return None
      
      return result
   
    except:
      raise

  def __generate_add_body(self, website_data: dict={}, raw_website_data: dict={}):

    body = {
      "website_name": "",
      "website_icon_url": "",
      "website_url": "",
      "website_cost": 300,
      "website_type": "INTERNATIONAL_NEWS",
      "country": "",
      "country_code": "",
      "fqdn": "",
      "programming_language": "Python",
      "date_created": datetime.datetime.now().isoformat(),
      "date_updated": datetime.datetime.now().isoformat(),
      "created_by": "Python News Crawler",
      "updated_by": "Python News Crawler"
    }

    if website_data and raw_website_data:
      body['website_name'] = raw_website_data['name']
      body['fqdn'] = raw_website_data['fqdn']
      body['website_url'] = raw_website_data['url']
      body['country'] = raw_website_data['country']
      body['country_code'] = raw_website_data['country_code']
      body['main_sections'] = website_data['main_sections']
      body['alexa_rankings'] = raw_website_data['alexa_rankings']

    else:
      raise websiteAPIError("Error generating payload for adding")

    return body

  def __exists(self, data: dict) -> bool:
    if not data:
      raise websiteAPIError("Invalid arguments")
    
    payload = {
      "fqdn": data['fqdn']
    }
    result = self.get(body=payload, limit=1, raw_website=False)

    if result:
      return result[0]
    else:
      return False

