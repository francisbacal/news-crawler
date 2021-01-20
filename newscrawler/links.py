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

import pandas as pd, tldextract, joblib, re, logging

log = logging.getLogger('LinksLog')

class pageLinks():
  """
  Get all links in a source page
  """
  def __init__(self, source: str=None, url: str=None, **kwargs):
    clear_data_home()
    self.options = Options()
    self.options = extend_opt(self.options, kwargs)

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
    a_blocks = soup.find_all('a', href=True)

    _result = [a['href'] for a in a_blocks]
    
    if not _result:
      raise commonError("No links parsed")

    self.list = self.__clean_list(_result)

  def __clean_list(self, result: list):
    clean_result = []
    exclusions = ["#", "/"]
    main_url_ext = tldextract.extract(self.url)

    #---------- VALIDATE ----------#
    for res in result:
      parsed_url = urlparse(res)
      ext = tldextract.extract(res)
      main_url_parsed = urlparse(self.url)
      
      #check if link is same domain and skip if not
      if parsed_url.netloc:
        if parsed_url.netloc != main_url_parsed.netloc:
          continue

      #check if no domain and add from source url
      if parsed_url.netloc == "":
        
        if str(res).startswith('/'):
          res = re.sub(r"^\/", "", res)

        res = f"{main_url_parsed.scheme}://{main_url_parsed.netloc}/{res}"


      #check if a social media link
      if ext.domain in SOCIAL_MEDIA_KEYS:
        continue

      #check if in exclusions
      if res in exclusions:
        continue

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
      link_type = get_path_type(d, clf)
      
      if link_type == "section":
        predictions.append(d)

    ##CLEAN RESULT
    sections = list(self.__clean_sections(predictions))
    sections = list(OrderedDict.fromkeys(sections))
    
    return sections

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

      if len(clean_paths) == 2:
        self.__firstSubDir = clean_paths[0]
        self.__secondSubDir = clean_paths[1]
      else:
        self.__firstSubDir = clean_paths[0]

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

