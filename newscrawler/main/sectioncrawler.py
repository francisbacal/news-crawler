from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website
from newscrawler import Seledriver
from api import *
from datetime import datetime
from newscrawler.model.compare import Compare

import newscrawler as crawler, os, math, time

log = init_log('MultiSection')
websiteAPI = Website()


def get_sections(url: str) -> list:
    """
    Main function to get section links
    """
    log.debug(f"Getting Sections for {url}")
    try:
        source = crawler.Source(url)
        links = crawler.pageLinks(source.page, source.r_url)
        sections = links.getSectionLinks()
        
    except crawler.commonError as e:
        log.error(e, exc_info=True)
        return []

    except crawler.sourceError:
        raise

    except Exception as e:
        log.error(e, exc_info=True)
        raise
    
    return sections


#---------- STATIC METHODS ----------#

iter_sections = []
def crawl_sections(url: str, repeat: int=2, iteration: int=1):
    """
    Recursive function to get all section links
        @params:    url         -       site url to crawl
        @params:    reapeat     -       no. of recursive times [default = 2]
    """
    log.debug(f"Crawling Recursively {url}")

    current_iteration = iteration
    try:
        sections = get_sections(url)
    except crawler.sourceError:
        return iter_sections
    except Exception as e:
        log.error(e, exc_info=True)
        pass

    REPEAT = repeat

    try:
        if all([sections, isinstance(sections, list), current_iteration < REPEAT]):
            current_iteration += 1
            for section in sections:
                if section not in iter_sections:
                    iter_sections.append(section)
                    log.debug(f"crawling section {section}")
                    crawl_sections(section, iteration=current_iteration)
    except Exception as e:
        raise

    result = iter_sections
    return result

def section_threading(url_dict: dict, sele=False):
    """
    Method to invoke ThreadPoolExecutor to recursively crawl sections concurrently
    """
    ## TODO: Add selenium thread process for error pages

    if not isinstance(url_dict, dict):
        raise crawler.commonError("Input must be a dict")

    
    _sections = url_dict['home_sections']
    sections = _sections

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(crawl_sections, section, iteration=2) for section in _sections]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                raise
            else:
                result_sections = future.result()
                sections = sections + result_sections

    
    sections = list(OrderedDict.fromkeys(sections))

    data = {
        "website_id": url_dict['website_id'],
        "sections": sections
    }
    return data

def get_home(website: dict) -> dict:
    """
    Get all sections in home page
        @params:    website         -   dict object of website from database to be crawled.
    """
    # Get item from dict
    url = website['url']
    website_id = website['_id']

    # data variable to push to results
    result = {
        "website_id": website_id,
        "home_sections": None,
        "error": False
    }

    log.debug(f"get_home method called for {url}")
    # Get sections
    try:
        sections = get_sections(url)
        result['home_sections'] = sections
    except crawler.sourceError:
        result['error'] = True
    except Exception as e:
        print(e)
        raise

    return result

def crawl_home(websites: list) -> dict:
    """
    Crawl sections in home page by using ThreadPoolExecutor
        @params:    websites            -   a list of splitted websites from section_crawl_init
    """

    home_sections = []
    for_selenium = []

    log.debug(f"Crawling Home Pages...")
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_home, website) for website in websites]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(e)
            else:
                result = future.result()
                if result['error']:
                    for_selenium.append(result)
                else:
                    home_sections.append(result)

    
    data = {
        "sections": home_sections,
        "for_selenium": for_selenium
    }

    return data


#---------- SELENIUM METHODS ----------#

def sele_crawl_home(websites: list):
    """
    Crawl home page of news website using selenium
    """

    seledriver = Seledriver(headless=False)
    browser = seledriver.browser

    results = []
    data = {
        "website_id": None,
        "url": None,
        "sections": []
    }

    for website in websites:
        url = website['url']
        data['website_id'] = website['_id']
        data['url'] = url

        #append data to result
        results.append(data)

        # Open New Tab and visit url
        browser.execute_script("window.open('"+url+"')")

    # for _ in range(len(browser.window_handles)):
    for result in results:
        wait = seledriver.wait(browser, 30)
        for x in range(len(browser.window_handles)):
            browser.switch_to.window(browser.window_handles[x])
            print(browser.current_url, result['url'])
            if browser.current_url == result['url']:
                print('FOUND HANDLE')
                try:
                    # browser.switch_to.window(browser.window_handles[-1])
                    wait.until(lambda browser: browser.execute_script('return document.readyState') == 'complete')
                    # browser.switch_to.window(handle)

                    source = browser.page_source
                    url = browser.current_url
                    links = crawler.pageLinks(source, url)
                    sections = links.getSectionLinks()
                except Exception as e:
                    print(e)
                finally:
                    browser.close()
                    break
        
    browser.quit()

@crawler.logtime
def section_crawl_init(websites: list, num_process: int):
    """
    Method to initialize section crawling using concurrent futures Pool Executor
        @params:    websites            -   a list of queried websites
        @params:    num_process         -   number of process to be used for Pool
    """

    log.debug(f'Initializing Pool Process using {num_process}/{os.cpu_count()} cores')

    # SPLIT WEBSITES INTO num_process NUMBER OF LIST
    splitted_websites = crawler.list_split(websites, num_process)

    # DECLARATION OF VARIABLES FOR RESULT
    for_selenium = []
    home_sections = []
    data = []
    
    # # FIRST POOL PROCESS TO CRAWL HOME PAGE VIA REQUESTS/CLOUDSCRAPER
    # with ProcessPoolExecutor(max_workers=num_process) as executor:
    #     futures = [executor.submit(crawl_home, website) for website in splitted_websites]

    #     for future in as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             log.error(e, exc_info=True)
    #         else:
    #             pool_result = future.result()
    #             result_sections = pool_result['sections']
    #             result_for_selenium = pool_result['for_selenium']
                
    #             # APPEND RESULT TO HOME SECTIONS
    #             for section in result_sections:
    #                 section_data = {
    #                     "home_sections": section['home_sections'],
    #                     "website_id": section['website_id']
    #                 }
    #                 home_sections.append(section_data)

    #             # APPEND RESULT FOR SELENIUM
    #             if result_for_selenium:
    #                 for res in result_for_selenium:
    #                     for_selenium.append(res)

    # # SECOND POOL PROCESS FOR CRAWLING OF SECTIONS FOR EACH HOME SECTIONS
    # log.debug(f"Initializing Second ProcessPoolExecutor")
    # with ProcessPoolExecutor(max_workers=num_process) as executor:
    #     futures = [executor.submit(section_threading, section) for section in home_sections]

    #     for future in as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             print(e)
    #             log.error(e, exc_info=True)
    #         else:
    #             data.append(future.result())
    
    # print("\n<--- SECTIONS --->")
    # print(data)
    # print("\n<--- FOR SELENIUM --->")
    # print(for_selenium)

    #FOR DYNAMIC WEBSITES
    # if for_selenium:
    process_count = os.cpu_count() - 1
    num_process = math.ceil(process_count / 2)
    sele_process = num_process if len(websites) > num_process  else len(websites)

    splitted_sele_websites = crawler.list_split(websites, sele_process)
    
    with ProcessPoolExecutor(max_workers=sele_process) as executor:
        futures = [executor.submit(sele_crawl_home, website) for website in splitted_sele_websites]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("SELENIUM PROCESS ERROR")
                log.error(e, exc_info=True)
            else:
                data.append(future.result())
    return data

        
if __name__ == '__main__':
   
    websiteAPI = Website()
    QUERY = {"country_code": "SGP"}

    FIELDS = {
        "url": 1,
        "date_updated": 1
    }

    payload = {
        "query": QUERY,
        "fields": FIELDS
    }

    websites = websiteAPI.get(payload, limit=1)
    
    date = websites[0]['date_updated']
    print(date)
    quit()

    if not websites:
        raise crawler.commonError("NoneType or Empty list not allowed")

    #declare numnber of process for article links extraction
    process_count = os.cpu_count() - 1
    NUM_PROCESS = process_count if len(websites) > process_count  else len(websites)

    #run main process method
    try:
        result = section_crawl_init(websites, NUM_PROCESS)
    except crawler.sourceError as e:
        log.debug(f"Source Error: {e}")
    except Exception as e:
        print(e)
