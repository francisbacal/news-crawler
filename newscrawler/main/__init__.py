from itertools import islice, chain
from api import Website
from newscrawler.helpers import is_today
from datetime import datetime, timedelta
from dateutil.parser import isoparse

from .sectioncrawler import *

def get_websites(payload={}, limit=1, last_update=7):
  """
  Method to get websites from database to crawl
    @params:  payload       -   query string to database
    @params:  limit         -   max number of websites to get per call [default: 1]
    @params:  last_update   -   max days of last update prior to today date [default: 7]
  """

  # GET DATE LESS THAN 7 DAYS
  today = datetime.today().replace(hour=0, minute=0, second=0,microsecond=0) - timedelta(last_update)

  payload['query']['date_updated'] = {"$lt": today.isoformat()}

  websiteAPI = Website()
  websites = websiteAPI.get(payload, limit=limit)

  if not websites:
    raise crawler.commonError("NoneType or Empty list not allowed")

  return websites
