import os, sys, re, pandas as pd, numpy as np, tldextract, datetime, json, joblib, re
from os.path import splitext
from urllib.parse import urlparse
from .compare import Compare
from ..exceptions import *

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


#TODO: ADD FIELD LAST DIRECTORY NUMBER OF WORDS -- DONE


class ModelData:
  """
  Instantiate a model data for training classifier
    @params:       data        -     type of data to be loaded for training. Accepts values "article" and "section"
  """
  def __init__(self, data: str=None):
    if not data:
      raise modelError("No data to generate. e.g. 'articles', 'sections' ")

    # if data not in ["article", "section"] or not isinstance(data, str):
    #   raise modelError("Invalid model data")

    self.data = data
    self.clf = None
    self.path = None
    self.url = None
  
    #---------- CLASSIFIER MODEL ----------#
    try:
      if self.data == "article":
        self.clf = joblib.load(f'{ROOT_DIR}/sav/articlemodel.sav')
      else:
        self.clf = joblib.load(f'{ROOT_DIR}/sav/sectionmodel.sav')
    except FileNotFoundError:
      pass

    #---------- LOAD INCLUSIONS ----------#
    with open(f"{ROOT_DIR}/dataset/inclusions.json", "r") as json_file:
      read_file = str(json_file.read())
      _inclusions = json.loads(read_file)
      self.inclusions = _inclusions['includes']

    #---------- LOAD EXCLUSIONS ----------#
    with open(f"{ROOT_DIR}/dataset/exclusions.json", "r") as json_file:
      read_file = str(json_file.read())
      _exclusions = json.loads(read_file)
      self.exclusions = _exclusions['excludes']

    #---------- LOAD DATASET ----------#
    if self.data == "article": 
      self.df = pd.read_csv(f"{ROOT_DIR}/dataset/articles.csv")
    else:
      self.df = pd.read_csv(f"{ROOT_DIR}/dataset/sections.csv")

    self.df = self.df.sample(frac=1).reset_index(drop=True)
    self.featureSet = pd.DataFrame(columns=('path', 'path length', 'include', 'exclude', 'double slash count', 'dot count', 'sub directory count', 'last dir num words', 'length of query', 'type'))

  #---------- METHODS ----------#
  def check_exclusions(self, path: str) -> int:
    for pattern in self.exclusions:
      if re.search(pattern, path):
        return 1
      else:
        continue

    return 0

  def check_inclusions(self, path: str) -> int:
    for pattern in self.inclusions:
      if re.search(pattern, path):
        if self.check_exclusions(path):
          continue
        return 1
      else:
        continue
    
    return 0

  def countSubDir(self, path):
    if str(path).endswith('/'):
      path = re.sub(r"\/$", "", path)
    return path.count('/')

  def countDoubleSlash(self, path):
    return path.count('//')

  def countDots(self, path):
    return path.count('.')

  def numWords(self, path):
    if any([not path, path == '', path == "/"]):
      return 0
  
    #remove last slash if exists
    path = re.sub(r"\/$", "", path)

    #split path to array
    filtered_path = list(filter(None, path.split("/")))

    #get last dir and count words
    last_dir = filtered_path[-1]

    SEPARATORS = ["-", "_"]

    for separator in SEPARATORS:
      last_dir = last_dir.replace(separator, " ")
    
    result = list(filter(None, last_dir.split()))

    return len(result)
    

  def extract_features(self, url: str, category: str, log: bool=False) -> list:
    """
    Extracts url features
      @params: url   -   url to parse features
      @params: category   -  category of the url ['section/article', 'others']
    """
    
    result = []
    url = str(url)
    
    #add the url to feature set
    # result.append(url)
    
    #parse the URL and extract the domain information
    parsed_url = urlparse(url)
    ext = tldextract.extract(url)

    if not parsed_url.path:
      path = re.sub(r"^https?:", "", url)
    else:
      path = parsed_url.path
    
    #add the path to feature set
    result.append(path)
    
    #length of path    
    result.append(len(path))

    #check for inclusions
    result.append(self.check_inclusions(path))

    #check if in exclusions
    result.append(self.check_exclusions(path))

    #checking count of double slash    
    result.append(self.countDoubleSlash(path))

    #checking count of dot   
    result.append(self.countDots(path))
    
    #Count number of subdir    
    result.append(self.countSubDir(path))

    #Count last dir word count
    result.append(self.numWords(path))
    
    #count number of queries    
    result.append(len(parsed_url.query))

    result.append(str(category))
    return result