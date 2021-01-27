from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log, Seledriver
from newscrawler.main.sectioncrawler import section_crawl_init
from itertools import islice, chain
from collections import OrderedDict
from datetime import datetime
from dateutil.parser import isoparse
import newscrawler as crawler, os


##############
## MAIN IMPORT

from newscrawler.main import get_websites, section_crawl_init

##
##############


log = init_log('MultiSection')


if __name__ == '__main__':
    # # QUERY TO DATABASE FOR WEBSITES

    # # store to a list
    # # example data got from db
    # # data = {"_id": "600845d07e8b804af10683", "url": "http://www.example.com"}
    websites = [
        {"_id": "600845d07e8b804af10683", "url": "https://www.philstar.com/"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.rappler.com"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.pep.ph/"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.sunstar.com.ph/"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.mb.com.ph/"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.manilatimes.net/"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.inquirer.net/"},
        {"_id": "600845d07e8b804af10683", "url": "https://www.straitstimes.com"}
        ]

    QUERY = {
        "country_code": "SGP",
        "alexa_rankings.local": {"$gt": 1, "$lte": 2000}
        }

    FIELDS = {
        "url": 1,
        "date_updated": 1
    }

    PAYLOAD = {
        "query": QUERY,
        "fields": FIELDS
    }

    # websites = get_websites(PAYLOAD, limit=10000)
    # websites = [
        # {"url": "https://www.straitstimes.com", "_id": "sample_id123"},
        # {"_id": "600845d07e8b804af10683", "url": "https://www.inquirer.net/"},
        # {"url": "https://mothership.sg/", "_id": "sample_id456"},
        # {"url": "https://www.nasdaq.com/", "_id": "sample_id456"},
    # ]

    if not websites:
        raise crawler.commonError("NoneType or Empty list not allowed")

    #declare numnber of process for article links extraction
    process_count = os.cpu_count() - 1
    NUM_PROCESS = process_count if len(websites) > process_count  else len(websites)

    # RUN MAIN PROCESS METHOD
    ## TODO: ADD TO DATASET SECTION AND ARTICLE FOR STRAITSTIMES
    try:
        log.debug('Starting section crawler')
        result = section_crawl_init(websites, NUM_PROCESS)
        print("\n================== RESULTS ==================")
        pprint(result)
    except Exception as e:
        print(e)

    # UPDATE WEBSITE IN DATABASE

