from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website, generate_payload
from newscrawler import Seledriver
from datetime import datetime ,timedelta
import newscrawler as crawler, os, sys

log = init_log('WebsiteUpdate')

##############
## MAIN IMPORT

from newscrawler.main import get_websites, get_website_count, classify_websites, crawl_init
from newscrawler.options import Options, extend_opt

##
##############

def extend_sys_argv(options: type(Options)=None, sys_args: list=[]):
    """
    Extends sys argv to options
        @params:    
            options         -   Options class from newscrawler
            sys_args        -   sys.args list of arguments to extend to options
    """
    options = options or Options()

    if not sys_args or len(sys_args) == 1:
        return options

    try:
      for i in range(len(sys_args)):
        i += 1
        key = sys_args[i].split("=")[0]
        val = sys_args[i].split("=")[1]

        argument = {
            key: val
        }

        options = extend_opt(options, argument)
            
    except (KeyError, IndexError):
      pass


    return options

if __name__ == '__main__':
    # GET SYS ARGS AND EXTEND TO OPTIONS
    options = extend_sys_argv(options=None, sys_args=sys.argv)

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
    LIMIT = options.limit
    PARAMS = {}

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