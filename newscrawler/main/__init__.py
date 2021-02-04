from itertools import islice, chain
from api import Website
from newscrawler import UpdateHelper
from datetime import datetime, timedelta
from dateutil.parser import isoparse
from concurrent.futures import ProcessPoolExecutor, as_completed

from .sectioncrawler import *
from .articlecrawler import article_crawl_init, save_articles

import os

def get_websites(payload: dict={}, params: dict={}, limit: int=1, raw_website: bool=False) -> list:
    """
    Method to get websites from database to crawl
        @params:  payload       -   query string to database
        @params:  limit         -   max number of websites to get per call [default: 1]
        @params:  params        -   parameters passed to api endpoint
        @params:  raw_wesbite   -   Pass True if needs to query from raw websites database [default: False]
    """

    # QUERY TO DB
    websiteAPI = Website()
    websites = websiteAPI.get(payload, params=params, limit=limit, raw_website=raw_website)

    if not websites:
        raise crawler.commonError("No website found from database.")


    return websites

def get_website_count(payload: dict={}, raw_website: bool=False) -> int:
    """
    Method to get website count from database
        @params:  payload       -   query string to database
        @params:  raw_website   -   Pass True if get from raw websites. [default: False]
    """

    websiteAPI = Website()
    websites = websiteAPI.counts(payload, raw_website=raw_website)

    return websites

def update_classify(website: dict):
    helper = UpdateHelper(website, raw_website=True)

    website['for_section_update'] = helper.for_section_update
    website['for_article_update'] = helper.for_article_update

    return website

def classify_websites(websites: list):

    data = []
    processes = os.cpu_count() -1
    with ThreadPoolExecutor(max_workers=processes) as executor:
        futures = [executor.submit(update_classify, website) for website in websites]

        for future in as_completed(futures):
            data.append(future.result())


    return data
        

def crawl_init(websites: list):
    log.debug("=============================================")
    log.debug("CRAWL INIT")
    log.debug("=============================================")
    

    for_section_update = []
    for_article_update = []

    # CLASSIFY WEBSITES THAT NEEDED SECTION OR ARTICLE ONLY UPDATE
    init_processes = os.cpu_count() - 1
    with ProcessPoolExecutor(max_workers=init_processes) as executor:
        futures = [executor.submit(update_classify, website) for website in websites]

        for future in as_completed(futures):
            result = future.result()
            if result['for_section_update']:
                for_section_update.append(result)
            elif result['for_article_update']:
                for_article_update.append(result)
            else:
                pass

    # DEFINE NUMBER OF PROCESS
    process_count = os.cpu_count() - 1
    NUM_PROCESSES = process_count if len(websites) > process_count  else len(websites)

    # GET SECTIONS FOR NO SECTION WEBSITES
    if for_section_update:
        section_crawl_results = section_crawl_init(for_section_update, NUM_PROCESSES)

    # GET ARTICLES FOR ARTICLE ONLY PARSING
    # if for_article_update:
    #     article_crawl_results = article_crawl_init(websites, NUM_PROCESSES)

    #     # ADD ARTICLES IN DATABASE
    #     section_save = save_articles(article_crawl_results)

    return "DONE"
