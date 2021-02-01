from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website
from newscrawler import Seledriver
from datetime import datetime ,timedelta
import newscrawler as crawler, os

log = init_log('WebsiteUpdate')

##############
## MAIN IMPORT

from newscrawler.main import get_websites, get_website_count, classify_websites, crawl_init

##
##############

if __name__ == '__main__':

    # while True:
        ## QUERY TO DATABASE FOR WEBSITES
        date_checker = crawler.DateChecker()

        # MAIN QUERY
        MAIN_QUERY = {
            "country_code": "SGP",
            "alexa_rankings.local": {"$gte": 0, "$lte": 2000},
            "main_sections": {"$ne": []}
            }
        # PARAMS = {"fields": '{"_id":0,  "website_url":1}'}

        PARAMS = {
            "fields": '{"website_url": 1,"date_updated": 1,"main_sections": 1}'
            }

        websites = get_websites(MAIN_QUERY, PARAMS, limit=1)

        if not websites:
            raise crawler.commonError("NoneType or Empty list not allowed")

        # DECLARE NUMBER OF PROCESS FOR CRAWLING
        process_count = os.cpu_count() - 1
        NUM_PROCESS = process_count if len(websites) > process_count  else len(websites)

        # RUN MAIN PROCESS METHOD
        ## TODO: ADD TO DATASET SECTION AND ARTICLE FOR STRAITSTIMES
        try:
            log.debug('Starting crawler')
            result = crawl_init(websites)


            print("\n================== RESULTS ==================")
            pprint(result)
        except Exception as e:
            log.error(e, exc_info=True)
            print(e)