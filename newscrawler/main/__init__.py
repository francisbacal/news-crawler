from itertools import islice, chain
from api import Website
from newscrawler import UpdateHelper
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from concurrent.futures import ProcessPoolExecutor, as_completed

from .sectioncrawler import *

import os

def get_websites(payload: dict={}, limit: int=1) -> list:
  """
  Method to get websites from database to crawl
    @params:  payload       -   query string to database
    @params:  limit         -   max number of websites to get per call [default: 1]
  """

  # GET DATE LESS THAN 7 DAYS FROM TODAY DATE
  today = datetime.today().replace(hour=0, minute=0, second=0,microsecond=0)

  payload['query']['date_updated'] = {"$lt": today.isoformat()}

  websiteAPI = Website()
  websites = websiteAPI.get(payload, limit=limit)

  if not websites:
    raise crawler.commonError("NoneType or Empty list not allowed")

  return websites

def update_classify(website: dict):
  helper = UpdateHelper(website)

  website['for_section_update'] = helper.for_section_update

  return website

def update_init(websites: list):
  for_section_update = []
  for_article_update = []

  # CLASSIFY WEBSITES THAT NEEDED SECTION/ARTICLE ONLY UPDATE
  init_processes = os.cpu_count() - 1
  with ProcessPoolExecutor(max_workers=init_processes) as executor:
    futures = [executor.submit(update_classify, website) for website in websites]

    for future in as_completed(futures):
      result = future.result()
      if result['for_section_update']:
        for_section_update.append(result)
      else:
        for_article_update.append(result)

  # UPDATE WEBSITES FOR SECTION UPDATE FIRST
  process_count = os.cpu_count() - 1
  SECTION_PROCESSES = process_count if len(websites) > process_count  else len(websites)

  sections = section_crawl_init(for_section_update, SECTION_PROCESSES)

  # UPDATE WEBSITES IN DATABASE
  ## CODE HERE


  # GET ARTICLES FOR EACH SECTIONS



  # ADD ARTICLES IN DATABASE
