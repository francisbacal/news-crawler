import os, sys, re, pandas as pd, numpy as np, tldextract, datetime, json, joblib, re
from os.path import splitext
from urllib.parse import urlparse
from .compare import Compare
from .articlesdata import modelData

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#TODO: ADD FIELD LAST DIRECTORY NUMBER OF WORDS

#---------- CLASSIFIER MODEL ----------#
clf = joblib.load(f'{ROOT_DIR}/sav/model.sav')

#---------- LOAD INCLUSIONS ----------#
with open(f"{ROOT_DIR}/dataset/inclusions.json", "r") as json_file:
  read_file = str(json_file.read())
  _inclusions = json.loads(read_file)
  inclusions = _inclusions['includes']

#---------- LOAD EXCLUSIONS ----------#
with open(f"{ROOT_DIR}/dataset/exclusions.json", "r") as json_file:
  read_file = str(json_file.read())
  _exclusions = json.loads(read_file)
  exclusions = _exclusions['excludes']

#---------- LOAD DATASET ----------#
df = pd.read_csv(f"{ROOT_DIR}/dataset/ws.csv")
df = df.sample(frac=1).reset_index(drop=True)

featureSet = pd.DataFrame(columns=('path', 'path length', 'include', 'exclude', 'double slash count', 'sub directory count', 'length of query', 'type'))

#---------- METHODS ----------#
def check_exclusions(path: str) -> int:
  for pattern in exclusions:
    if re.search(pattern, path):
      return 1
    else:
      continue

  return 0

def check_inclusions(path: str) -> int:
  for pattern in inclusions:
    if re.search(pattern, path):
      if check_exclusions(path):
        continue
      return 1
    else:
      continue
  
  return 0

def countSubDir(url):
    if str(url).endswith('/'):
      url = re.sub(r"\/$", "", url)
    return url.count('/')

def countDoubleSlash(url):
    return url.count('//')

def extract_features(url: str, category: str, log: bool=False) -> list:
  """
  Extracts url features
    @params: url   -   url to parse features
    @params: category   -  category of the url ['section','article', 'others']
  """
  
  result = []
  url = str(url)
  
  #add the url to feature set
  # result.append(url)
  
  #parse the URL and extract the domain information
  path = urlparse(url)
  ext = tldextract.extract(url)
  
  #add the path to feature set
  result.append(path.path)
  
  #length of path    
  result.append(len(path.path))

  #check for inclusions
  result.append(check_inclusions(path.path))

  #check if in exclusions
  result.append(check_exclusions(path.path))

  #checking presence of double slash    
  result.append(countDoubleSlash(path.path))
  
  #Count number of subdir    
  result.append(countSubDir(path.path))
  
  #count number of queries    
  result.append(len(path.query))

  result.append(str(category))
  return result