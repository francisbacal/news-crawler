from .helpers import catch, rand_sleep
from .exceptions import sourceError
from .seledriver import Seledriver
import cloudscraper, requests, json, logging

log = logging.getLogger("SourceLog")

class Source:
  """
  Get the page source of given URL
  """
  def __init__(self, url: str, timeout=60):

    if not isinstance(url, str):
      raise TypeError(f"URL must be str not {type(url)}")

    self.url = url
    self.r_url = url
    self.timeout = timeout
    self.page = None
    self.run()
  
  def run(self):
    log.debug("Getting Source")
    # raise sourceError(self.url, "TEST FOR SELENIUM")
    cs = cloudscraper.create_scraper()
    rand_sleep(2,5)
    get_request = catch('None', lambda: cs.get(self.url, timeout=self.timeout))
    page = catch('None', lambda: get_request.text)

    if not page:
      log.debug("Cloudscraper failed. Trying Requests")
      get_request = self.request(self.url)
      page = catch('None', lambda: get_request.text)
    
    # if not page:
    #   log.debug("Requests failed. Trying Selenium")
    #   seledriver = Seledriver()
    #   browser = seledriver.browser
    #   browser.get(self.url)
    #   page = browser.page_source

    #   browser.close()
    #   browser.quit()

    if not page:
      raise sourceError(self.url, "Unable to get source page")
    
    self.r_url = get_request.url
    self.page = page

  def request(self, url):
    try:
      response = requests.get(self.url, timeout=self.timeout)
    
      error = any([
            str(response.status_code).startswith('5'),
            str(response.status_code).startswith('4')
          ])

      if error:
        raise sourceError('Error Getting Source')
      else:
        return response
    
    except sourceError:
      raise

    except:
      return None

      