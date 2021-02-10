from newscrawler import init_log, Options, extend_opt, catch
from ..exceptions import websiteAPIError, DuplicateValue
from bson import json_util
from langdetect import detect
from bs4 import BeautifulSoup
from pprint import pprint
import requests,json,datetime, cloudscraper, copy, tldextract

from urllib.parse import urlparse


log = init_log("WebsiteAPI")

class Website:
  """
    Class for website endpoint connections
  """
  def __init__(self, options=None, **kwargs):
    """
    Initialize method
    """
    # self.url = 'http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/'
    self.url = 'http://192.168.3.143:4040/mmi-endpoints/v0/web/'
    self.options = options or Options()
    self.headers = {"Content-Type" : "application/json", "Authorization": self.options.token}
    self.existing = False

  def __raise_errors(self, response, url):
    """
    Private method to check response for errors and raise appropriate exceptions
      @params:
          response          -   requests response object
          url               -   endpoint url
    """
    if str(response.status_code).startswith('5'):
      if 'error' in response.json():
        try:
          if response.json()['error']['code'] == 11000:
            raise DuplicateValue(url)
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
    """
    Get a single website from the database
      @params:
          site_id           -   String ID of website
    """
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
    """
    Get websites from the database
      @params:
          body          -   Payload of query to search in database
          params        -   additional parameters to attach to the headers
          **kwargs      -   additional arguments to extend to options if matched
    """
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
    """
    Update a website in the database
      @params:
          body            -   Payload of website details to update
          website_id      -   String ID of website to update
          **kwargs        -   additional arguments to extend to options if matched
    """
    # EXTEND KWARGS TO OPTIONS IF KEY EXISTS
    self.options = extend_opt(self.options, kwargs)

    if self.options.raw_website:
      url = f"http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/{website_id}"
      body['created_by'] = "Singapore Website Done"
    else:
      url = self.url + website_id

    try:
      has_date_updated_payload = True if body['date_updated'] else False
      if has_date_updated_payload:
        pass
    except KeyError:
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
    """
    Get a count of websites based on passed details
      @params:
          body            -   Payload of query to search in the database
          **kwargs        -   additional arguments to extend to options if matched
    """
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
    """
    Add website to the database
      @params:
          data            -   payload of website details to add
          raw_id          -   id of website from raw_website database if any
          **kwargs        -   additional arguments to extend to options if matched
    """
    # EXTEND KWARGS TO OPTIONS IF KEY EXISTS
    self.options = extend_opt(self.options, kwargs)

    if self.options.raw_website:
      url = "http://192.168.3.143:4040/mmi-endpoints/v0/raw-website/query"
    else:
      url = self.url + "custom_query"

    # GET WEBSITE DETAILS FROM RAW WEBSITE
    raw_website = None

    if raw_id and self.options.raw_website:

      QUERY = {
        "query": {
          "_id": raw_id
        }
      }

      raw_website = self.get(QUERY, limit=1, raw_website=True)[0]
    
    #CHECK IF EXISTING
    existing = self.__exists(data)

    if existing:
      raise DuplicateValue("Duplicate Website in Database")
    elif raw_website:
      body = self.__generate_add_body(data, raw_website)
    else:
      body = self.__generate_add_body(data)

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
    """
    Generate a website schema.
      @params:
          website_data            -   dict object containing crawled website data
          raw_website_data        -   dict object containing raw website data
    """
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

    #CHECK WEBSITE DATABASE FOR POSSIBLE DUPLICATE
    self.__check(raw_website_data['url'])
    body['fqdn'] = self.fqdn
    body['website_url'] = self.website_url
    body['website_name'] = self.name

    print("\n===================")
    pprint(body)
    print("===================")

    if website_data and raw_website_data:
      body['country'] = raw_website_data['country']
      body['country_code'] = raw_website_data['country_code']
      body['main_sections'] = website_data['main_sections']
      body['alexa_rankings'] = raw_website_data['alexa_rankings']
    
    elif website_data:
      body['country'] = raw_website_data['country']
      body['country_code'] = raw_website_data['country_code']
      body['main_sections'] = website_data['main_sections']
      body['alexa_rankings'] = raw_website_data['alexa_rankings']

    else:
      raise websiteAPIError("Error generating payload for adding")

    return body

  def __exists(self, data: dict) -> bool:
    """
    Check if website already exists in database
      @params:
        data            -   website details
    """
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

  def __check(self, website_url: str):
      """
      Cleans and checks website url
        @params:
          website_url           -   website url to be checked
      """
      if not website_url or not isinstance(website_url, str):
          raise ValueError('Invalid Parameters passed on WebsiteChecker')
      
      self.protocol = "http"
      self.__clean_url(website_url)
      
      duplicate = self.__check_duplicates()

      if duplicate:
          self.__handle_duplicate(duplicate)
          

  def __clean_url(self, url: str):
      """
      Private method to clean url of website
        @params:
          url             -   url of website to be cleaned
      """
      parsed_url = urlparse(url)
      tld_url = tldextract.extract(url)

      self.domain = tld_url.domain
      self.subdomain = tld_url.subdomain
      self.suffix = tld_url.suffix
      
      if self.subdomain == "":
        self.website_url = f"{self.protocol}://{self.domain}.{self.suffix}"
      else:
        self.website_url = f"{self.protocol}://{self.subdomain}.{self.domain}.{self.suffix}"

      if self.subdomain != "www" and self.subdomain != "":
          self.fqdn = f"{self.subdomain}.{self.domain}.{self.suffix}"
      else:
          self.fqdn = f"{self.domain}.{self.suffix}"

      self.name = self.domain.capitalize()

  def __check_duplicates(self):
      """
      Private method to check individual parameters of website for duplicates
      """
      data = {
          "_id": None,
          "parameter": None
      }

      try:
          ws = self.get({"website_name": self.name}, limit=5, raw_website=False)
          data['parameter'] = "website_name" if ws else None
          
          if not ws:
              ws = self.get(body={"fqdn": self.fqdn}, limit=5, raw_website=False)
              data['parameter'] = "fqdn" if ws else None

          if not ws:
              ws = self.get(body={"website_url": self.website_url}, limit=5, raw_website=False)
              data['parameter'] = "website_url" if ws else None

          if not ws:
              return None
          else:
              if len(ws) > 1:
                  return data
              else:
                  data['_id'] = ws[0]['_id']
                  return data
      except:
          raise

  def __handle_duplicate(self, duplicate: dict):
      """
      Private method to handle duplicates of website
        @params:
            duplicate           -   dict object of website duplicate
      """
      duplicate_website = self.get_one(duplicate['_id'])

      # CHECK FQDN
      if duplicate_website['fqdn'] == self.fqdn:
          return False
      
      # CHECK NAME
      if duplicate['parameter'] == "website_name":
          if self.subdomain != "www" and self.subdomain != "":
              self.name = f"{self.subdomain.capitalize()} {self.domain.capitalize()}"
          else:
              self.name = f"{self.domain.capitalize()} {self.suffix}"
      
      # CHECK DUPLICATE AGAIN
      duplicate = self.__check_duplicates()

      if duplicate: self.existing = True