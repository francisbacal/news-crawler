from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website, generate_payload
from newscrawler import Seledriver
from datetime import datetime ,timedelta
import newscrawler as crawler, os

log = init_log('WebsiteUpdate')

##############
## MAIN IMPORT

from newscrawler.main import get_websites, get_website_count, classify_websites, crawl_init
from newscrawler.options import Options

##
##############

if __name__ == '__main__':
    # INSTANTIATE OPTIONS
    options = Options()

    ## QUERY TO DATABASE FOR WEBSITES
    date_checker = crawler.DateChecker()
    less_2_weeks = datetime.today() - timedelta(14)

    # FIRST QUERY CHECK FOR MORE THAN 2 WEEKS SINCE UPDATED
    MORE_THAN_2_WEEKS_RAW_QUERY = {
        "country": options.country,
        "date_updated": {"$lt": less_2_weeks.isoformat()}
    }

    # DEFINE PARAMETERS FOR GETTING WEBSITES
    PAYLOAD = generate_payload(options.country)
    LIMIT = 1
    PARAMS = {}

    PAYLOAD = {
        "_id": "601bbb887e8b804af144ea6e"
    }

    while True:
        websites = get_websites(PAYLOAD, PARAMS, limit=LIMIT, raw_website=False)
        
        if not websites:
            raise crawler.commonError("No website/s to update")
        
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

        break