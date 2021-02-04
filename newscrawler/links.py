from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .helpers import catch, get_path_type
from .exceptions import commonError
from .model import Compare
from .vars import EXCLUDED_SECTION_KEYS, SOCIAL_MEDIA_KEYS
from .options import *
from sklearn.datasets import clear_data_home
from pprint import pprint
from collections import OrderedDict
from chardet import detect
from datetime import datetime

import pandas as pd, tldextract, joblib, re, logging

log = logging.getLogger('LinksLog')

class pageLinks():
  """
  Get all links in a source page
  """
  def __init__(self, source: str=None, url: str=None, home_url: str=None, **kwargs):
    # clear_data_home()
    self.options = Options()
    self.options = extend_opt(self.options, kwargs)

    if not home_url: home_url = url

    self.main_url_parsed = urlparse(home_url)
    self.main_url_ext = tldextract.extract(home_url)


    if not self.options.testing:
      if not source:
        raise commonError("Unable to read source page from parameters")
      elif not isinstance(source, str):
        raise TypeError("Source must be a str")

      self.source = str(source)
      self.url = url
      self.list = []
      self.__firstSubDir = None
      self.__secondSubDir = None
      self.run()
    else:
      self.list = []
      self.__firstSubDir = None
      self.__secondSubDir = None

  def run(self):
    soup = BeautifulSoup(self.source, 'html.parser')
    try:
      title = soup.title.string
    except:
      title = None
    
    if title:
      is_en = self.__language(title)

    a_blocks = soup.find_all('a', href=True)
    ul_blocks = soup.find_all('ul')

    _result = [a['href'] for a in a_blocks]
  
    if not _result:
      raise commonError("No links parsed")
    
    # if is_en:
    self.list = self.__clean_list(_result)

    # else:
    #   raise commonError("Can not decode website text")

  def __clean_list(self, result: list):
    clean_result = []
    exclusions = ["#", "/"]
    
    #---------- VALIDATE ----------#
    for res in result:
      parsed_url = urlparse(res)
      ext = tldextract.extract(res)

      #check if @ is present at netloc
      at_regex = re.compile(r"[@]")
      has_at = at_regex.search(res)
      if has_at:
        continue

      #check if no netloc and add from source url
      
      if parsed_url.netloc == "":
        if str(res).startswith('/'):
          res = re.sub(r"^\/", "", res)

        res = f"http://{self.main_url_parsed.netloc}/{res}"

      
      # RE PARSE URL
      parsed_url = urlparse(res)
      ext = tldextract.extract(res)

      #check if link is same domain and skip if not
      if ext.domain != '':
        if ext.domain != self.main_url_ext.domain:
          continue

      #check if a social media link
      if ext.domain in SOCIAL_MEDIA_KEYS:
        continue

      #check if in exclusions
      if res in exclusions:
        continue

      #change scheme to http for all urls and remove query
      res = f"http://{parsed_url.netloc}{parsed_url.path}"

      #check if already in list
      if res not in clean_result:
        clean_result.append(res)

    return clean_result

  def getSectionLinks(self, links = []):  
    if not self.list and not links:
      raise commonError("No links list")

    clf = joblib.load('newscrawler/model/sav/sectionmodel.sav')

    if links:
      data = links
    else:
      data = self.list
    
    predictions = []
    
    for d in data:
      ext = tldextract.extract(d)
      parsed_d = urlparse(d)

      # CHECK IF SAME DOMAIN WITH HOME
      if ext.domain != self.main_url_ext.domain:
        continue

      link_type = get_path_type(d, clf)
      
      if link_type == "section":
        predictions.append(d)
        continue
      
      # USED CASE: section url with format section.domain.ext e.g. sports.inquirer.net
      if all([ext.subdomain != "www", ext.domain == self.main_url_ext.domain, parsed_d.path == ""]):
        predictions.append(d)

    ##CLEAN RESULT
    sections = list(self.__clean_sections(predictions))
    sections = list(OrderedDict.fromkeys(sections))
    
    return sections[0:10] if len(sections) > 10 else sections

  def __clean_sections(self, sections: list) -> list:

    #Instantiate compare
    data = Compare(EXCLUDED_SECTION_KEYS)

    cleaned_sections = []
    
    for section in sections:
      
      #remove trailing and leading whitespaces
      section = section.strip()

      #remove last slash if exists
      section = re.sub(r"\/$", "", section)

      #Get path or section link
      parsed_url = urlparse(section)
      ext_url = tldextract.extract(section)

      if parsed_url.scheme == '':
        section = f"http://{parsed_url.netloc}{parsed_url.path}"
      if parsed_url.query != '':
        section = f"{section}?{parsed_url.query}"

      parsed_url = urlparse(section)
      path = parsed_url.path
      
      if parsed_url.query != '':
        section = re.sub(r"\?[^?]*$", "", section)
      
      #Get subdirectories
      filter_paths = list(filter(None, path.split("/")))

      #check number of sub directory and get first two if more than 1
      if len(filter_paths) > 2:
        continue
      if len(filter_paths) > 1:
        clean_paths = filter_paths[0:2]
      else:
        clean_paths = filter_paths

      if not clean_paths:
        yield section
        continue

      elif len(clean_paths) == 2:
        self.__firstSubDir = clean_paths[0]
        self.__secondSubDir = clean_paths[1]
      else:
        self.__firstSubDir = clean_paths[0]
      
      # TODO: CHECK IF FIRST SUB-DOMAIN IS INSTANCE OF YEAR
      # AND CONTINUE IF LESS THAN 1 YEAR FROM TODAY'S YEAR
      first_sub = str(self.__firstSubDir)
      len_first_sub = len(first_sub)

      if len_first_sub == 4:
        try:
          this_year = int(datetime.today().year)
          int_first_sub = int(first_sub)

          if int_first_sub < (this_year - 1):
            continue
          elif int_first_sub > this_year:
            continue
        except ValueError:
          pass

      #check first sub directory for probability of exclusion
      SPACE_KEYS = ['_', '-']
      for key in SPACE_KEYS:
          self.__firstSubDir = self.__firstSubDir.replace(key, " ")

      eval_result = data.eval(self.__firstSubDir)
      
      THRESHOLD = 0.5
      if eval_result:
        # print(eval_result, path)
        similarity = int(eval_result[0]['similarity'].strip("%")) / 100

        #check second sub directory for probability of exclusion if first subdirectory is not excluded
        if similarity < THRESHOLD and not self.__secondSubDir:
          yield section
        else:
          continue

      
      if self.__secondSubDir:
          # print(path)
          for key in SPACE_KEYS:
            self.__secondSubDir = self.__secondSubDir.replace(key, " ")

          secondSubDir_length = len(self.__secondSubDir)

          _eval_result = data.eval(self.__secondSubDir)

          if _eval_result:
            match_word = _eval_result[0]['word']
            similarity = int(_eval_result[0]['similarity'].strip("%")) / 100
            
            #check match_word vs sub dir word length if similarity is greater than or equal to THRESHOLD
            #TODO: check for discrepancies on used cases. refactor this part to number of words

            if similarity >= THRESHOLD:
              len_ratio = len(match_word) / secondSubDir_length
              if len_ratio < 0.6:
                yield section
          else:
            yield section
      else:
        yield section

  def getArticleLinks(self, links = []):  
    if not self.list and not links:
      raise commonError("No links list")

    clf = joblib.load('newscrawler/model/sav/articlemodel.sav')

    if links:
      data = links
    else:
      data = self.list
    
    predictions = []
    for d in data:
      link_type = get_path_type(d, clf)
      
      if link_type == "article":
        predictions.append(d)

    ##CLEAN RESULT
    articles = list(self.__clean_articles(predictions))

    return articles

  def __clean_articles(self, articles: list) -> list:
    firstSubDir = None
    lastSubDir = None

    #Instantiate compare
    data = Compare(EXCLUDED_SECTION_KEYS)

    cleaned_articles = []

    for article in articles:
      
      #remove trailing and leading whitespaces
      article = article.strip()

      #remove last slash if exists
      article = re.sub(r"\/$", "", article)

      #Get path or article link
      parsed_url = urlparse(article)
      path = parsed_url.path
      
      #Get subdirectories
      filter_paths = list(filter(None, path.split("/")))

      if not filter_paths:
        continue

      #check number of sub directory if more than 1 and continue if not
      if len(filter_paths) > 1:
        clean_paths = filter_paths
        firstSubDir = clean_paths[0]
        lastSubDir = clean_paths[-1]
      else:
        firstSubDir = filter_paths[0]

      #check first sub directory for probability of exclusion
      SPACE_KEYS = ['_', '-']
      for key in SPACE_KEYS:
          firstSubDir = firstSubDir.replace(key, " ")

      eval_result = data.eval(firstSubDir)
      
      THRESHOLD = 0.5
      if eval_result:
        
        similarity = int(eval_result[0]['similarity'].strip("%")) / 100

        #check last sub directory for probability of exclusion if first subdirectory is not excluded
        if similarity < THRESHOLD and not lastSubDir:
          yield section
        else:
          continue
      
      elif lastSubDir:
      
          for key in SPACE_KEYS:
            lastSubDir = lastSubDir.replace(key, " ")

          lastSubDir_length = len(lastSubDir)

          _eval_result = data.eval(lastSubDir)

          if _eval_result:
            match_word = _eval_result[0]['word']
            similarity = int(_eval_result[0]['similarity'].strip("%")) / 100
            
            #check match_word vs sub dir word length if similarity is greater than or equal to THRESHOLD
            #TODO: check for discrepancies on used cases. refactor this part to number of words

            if similarity >= THRESHOLD:
              len_ratio = len(match_word) / lastSubDir_length
              if len_ratio < 0.6:
                yield article
          else:
            yield article
      else:
        yield article

  def __language(self, title: str):
    """
    Detect website langauge of website based on title
      @params:  url       -   Url of website to detect
    """
    # TODO: USE MORE LANGUAGE DETECTOR ALGO/LIBRARY
    # CAN TRY TO USE POLYGLOT LIBRARY
    

    #CHECK IF ENGLISH ASCII
    #CHECK LANGUAGE
    try:
      title.encode('utf-8').decode('ascii')
    except UnicodeDecodeError:
        self.lang = catch('None', lambda: detect(title))
        return False
    else:
        self.lang = catch('None', lambda: detect(title))
        return True

