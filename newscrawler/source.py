from .helpers import catch, rand_sleep
from .exceptions import sourceError
import cloudscraper, requests, json

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
    cs = cloudscraper.create_scraper()
    # rand_sleep()
    page = catch('None', lambda: cs.get(self.url, timeout=self.timeout))

    if not page:
      page = catch('None', lambda: requests.get(self.url, timeout=self.timeout))
      # page = requests.get(self.url, timeout=self.timeout)

    if not page:
      raise sourceError(self.url, "Unable to get source page")
    
    self.r_url = page.url
    self.page = page.text