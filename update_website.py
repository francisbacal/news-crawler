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
    ## QUERY TO DATABASE FOR WEBSITES
    

    date_checker = crawler.DateChecker()
    less_2_weeks = datetime.today() - timedelta(14)

    # FIRST QUERY CHECK FOR MORE THAN 2 WEEKS SINCE UPDATED
    MORE_THAN_2_WEEKS_RAW_QUERY = {
        "country": "Singapore",
        "created_by": "Singapore Website",
        "date_updated": {"$lt": less_2_weeks.isoformat()}
    }

    # QUERY TO RAW WEBSITES
    RAW_QUERY = {
        "query": {
            "country": "Singapore",
            "created_by": "Singapore Website",
            "date_updated": {"$lt": date_checker.today.isoformat()
            }
        }
    }

    # DEFINE PAYLOAD
    PAYLOAD = RAW_QUERY
    PARAMS = {}

    # CHECK FOR WEBSITES WITH LESS THAN 2 WEEKS
    # websites_2_weeks_count = get_website_count(MORE_THAN_2_WEEKS_RAW_QUERY, raw_website=True)

    websites = get_websites(PAYLOAD, PARAMS, limit=1, raw_website=True)

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

    # UPDATE WEBSITE IN DATABASE