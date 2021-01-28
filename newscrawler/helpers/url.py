
from urllib.parse import urlparse
import tldextract

class CleanURL:
  """
  Class for cleaned parsed and tld extracted URL
  """

  def __init__(self, url: str=''):
    self.scheme = "http"
    self.parsed_url = urlparse(url)
    self.tldext = tldextract.extract(url)
    self.__parse()

  def __parse(self):

    self.domain = self.tldext.domain
    self.subdomain = self.tldext.subdomain
    self.suffix = self.tldext.suffix

    self.netloc = self.parsed_url.netloc
    self.path = self.parsed_url.path
    self.query = self.parsed_url.query
    self.params = self.parsed_url.params

    self.url = f"{self.scheme}://{self.netloc}"

    if self.path != '':
      self.url = f"{self.url}{self.path}"

      if self.query != '':
        self.url = f"{self.url}?{self.query}"