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
from .articlecrawler import get_articles

import newscrawler as crawler, os, math, time

log = init_log('MultiSection')
websiteAPI = Website()


def get_links(url: str) -> list:
    """
    Main function to get sections and articles
        @params:    url         -   website url
    """
    log.debug(f"Getting Sections for {url}")
    try:
        # GET SOURCE AND LINKS FROM URL
        source = crawler.Source(url)
        links = crawler.pageLinks(source.page, source.r_url)

        # GET SECTIONS FROM URL
        sections = links.getSectionLinks()

        # GET ARTICLES FROM URL
        log.debug(f"Getting articles for {url}")
        articles = get_articles(url, source)
        
    except crawler.commonError as e:
        log.error(e, exc_info=True)
        print(e)
        data = {"sections": [], "articles": []}
        return data

    except crawler.sourceError:
        raise

    except Exception as e:
        log.error(e, exc_info=True)
        raise
    
    # CREATE RETURN DATA
    data = {
        "sections": sections,
        "articles": articles
    }

    return data


#---------- STATIC METHODS ----------#

def crawl_sections(url: str, iter_items: dict, repeat: int=2, iteration: int=1):
    """
    Recursive function to get all section links
        @params:    url         -       site url to crawl
        @params:    reapeat     -       no. of recursive times [default = 2]
    """
    log.debug(f"Crawling {url} Recursively")

    current_iteration = iteration
    iter_sections = iter_items['iter_sections']
    iter_articles = iter_items['iter_articles']

    try:
        links = get_links(url)
        sections = links['sections']
        articles = links['articles']

        # EXTEND ARTICLES IN ITER_ARTICLES
        iter_articles.extend(articles)

        # REMOVE ARTICLE AND SECTION DUPLICATES
        iter_articles = list(OrderedDict.fromkeys(iter_articles))
        # iter_sections = list(OrderedDict.fromkeys(iter_sections))

    except crawler.sourceError:
        return iter_sections
    except Exception as e:
        log.error(e, exc_info=True)
        raise

    REPEAT = repeat
    try:
        if all([sections, isinstance(sections, list), current_iteration < REPEAT]):
            current_iteration += 1
            for section in sections:
                if section not in iter_sections:
                    # APPEND TO ITER SECTIONS
                    iter_sections.append(section)

                    # EXTENDED ITER ITEMS DECLARATION
                    iter_items_data = {
                        "iter_sections": iter_sections,
                        "iter_articles": iter_articles
                    }

                    log.debug(f"crawling section {section}")
                    crawl_result = crawl_sections(section, iter_items_data, iteration=current_iteration)

                    # EXTEND RESULTS AGAIN
                    iter_sections.extend(crawl_result['sections'])
                    iter_articles.extend(crawl_result['articles'])
    except Exception as e:
        raise

    # REMOVE ARTICLE AND SECTION DUPLICATES
    iter_articles = list(OrderedDict.fromkeys(iter_articles))
    iter_sections = list(OrderedDict.fromkeys(iter_sections))

    data = {
        "sections": iter_sections,
        "articles": iter_articles
    }

    return data

def section_threading(url_dict: dict, sele=False):
    """
    Method to invoke ThreadPoolExecutor to recursively crawl sections concurrently
    """
    ## TODO: Add selenium thread process for error pages

    if not isinstance(url_dict, dict):
        raise crawler.commonError("Input must be a dict")

    _sections = url_dict['home_sections']
    sections = _sections
    articles = []

    iter_items = {
        "iter_sections": [],
        "iter_articles": []
    }

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(crawl_sections, section, iter_items, iteration=1) for section in _sections]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                raise
            else:
                result = future.result()

                # EXTEND RESULT SECTIONS
                sections.extend(result['sections'])

                # EXTEND RESULT ARTICLES
                articles.extend(result['articles'])

    
    sections = list(OrderedDict.fromkeys(sections))
    articles = list(OrderedDict.fromkeys(articles))

    data = {
        "website_id": url_dict['website_id'],
        "url": url_dict['url'],
        "sections": sections,
        "articles": articles
    }
    return data

def get_home(website: dict) -> dict:
    """
    Get all sections in home page
        @params:    website         -   dict object of website from database to be crawled.
    """
    if not isinstance(website, dict):
        raise crawler.commonError("Invalid parameter type for website")

    # GET ITEMS FROM WEBSITE PARAMETER
    url = website['url']
    website_id = website['_id']

    # CREATE INITIAL RETURN DATA
    data = {
        "website_id": website_id,
        "url": url,
        "home_sections": None,
        "home_articles": None,
        "error": False
    }

    log.debug(f"get_home method called for {url}")

    # GET LINKS
    try:
        links = get_links(url)

        data['home_sections'] = links['sections']
        data['home_articles'] = links['articles']
    except crawler.sourceError:
        data['error'] = True
    except Exception as e:
        log.error(e, exc_info=True)
        print(e)
        raise

    return data

def crawl_home(websites: list) -> dict:
    """
    Crawl sections in home page by using ThreadPoolExecutor
        @params:    websites            -   a list of splitted websites from section_crawl_init
    """

    home_data = []
    for_selenium = []

    log.debug(f"Crawling Home Pages...")
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_home, website) for website in websites]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log.error(e, exc_info=True)
                pass
            else:
                result = future.result()
                if result['error']:
                    for_selenium.append(result)
                else:
                    home_data.append(result)

    
    data = {
        "home_data": home_data,
        "for_selenium": for_selenium
    }

    return data


#---------- SELENIUM/DYNAMIC METHODS ----------#

def sele_crawl_home(websites: list):
    """
    Crawl home page of news website using selenium
    """

    seledriver = Seledriver(headless=True)
    browser = seledriver.browser

    results = []

    for website in websites:
        url = website['url']
        data = {
            "website_id": website['_id'],
            "url": url,
            "sections": []
            "articles": []
        }

        #append data to result
        results.append(data)

        # Open New Tab and visit url
        browser.execute_script("window.open('"+url+"')")
    
    for result in results:
        print(f"Processing {result['url']}")
        wait = seledriver.wait(browser, 5)
        for x in range(len(browser.window_handles)):
            browser.switch_to.window(browser.window_handles[x])

            # Clean URLS
            browser_cleanurl = crawler.CleanURL(browser.current_url)
            result_cleanurl = crawler.CleanURL(result['url'])


            if browser_cleanurl.domain == result_cleanurl.domain:
                print(f"FOUND HANDLE {browser_cleanurl.url} -- {result_cleanurl.url}")
                try:
                    wait.until(lambda browser: browser.execute_script('return document.readyState') == 'complete')

                    source = browser.page_source
                    url = browser.current_url
                    links = crawler.pageLinks(source, url)
                    sections = links.getSectionLinks()
                    articles = links.getArticleLinks()

                    if sections:
                        result['sections'] = sections
                    
                    if articles:
                        result['articles'] = articles

                except Exception as e:
                    log.error(e, exc_info=True)
                    print(e)
                finally:
                    browser.close()
                    break
        
    browser.quit()
    return results


#---------- INIT METHOD ----------#
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
    articles = []

    data = []
    
    # FIRST POOL PROCESS TO CRAWL HOME PAGE VIA REQUESTS/CLOUDSCRAPER
    with ProcessPoolExecutor(max_workers=num_process) as executor:
        futures = [executor.submit(crawl_home, website) for website in splitted_websites]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log.error(e, exc_info=True)
            else:
                pool_result = future.result()
                result_home_data = pool_result['home_data']
                result_for_selenium = pool_result['for_selenium']
                
                # APPEND RESULTS TO RESULT VARIABLES
                for home_data in result_home_data:

                    section_data = {
                        "home_sections": home_data['home_sections'],
                        "website_id": home_data['website_id'],
                        "url": home_data['url']
                    }

                    article_data = {
                        "home_articles": home_data['home_articles'],
                        "website_id": home_data['website_id'],
                        "url": home_data['url']
                    }

                    home_sections.append(section_data)
                    articles.append(article_data)

                # APPEND RESULT FOR SELENIUM
                if result_for_selenium:
                    for res in result_for_selenium:
                        for_selenium.append(res)
    
    # SECOND POOL PROCESS FOR CRAWLING OF SECTIONS FOR EACH HOME SECTIONS
    log.debug(f"Initializing Second ProcessPoolExecutor")
    with ProcessPoolExecutor(max_workers=num_process) as executor:
        futures = [executor.submit(section_threading, section) for section in home_sections]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(e)
                log.error(e, exc_info=True)
            else:
                data.append(future.result())

    # # POOL PROCESS FOR DYNAMIC WEBSITES
    if for_selenium:
        process_count = os.cpu_count() - 1
        num_process = math.ceil(process_count / 2)
        sele_process = num_process if len(websites) > num_process  else len(websites)
        log.debug(f'Initializing Selenium Pool Process using {sele_process}/{os.cpu_count()} cores')

        splitted_sele_websites = crawler.list_split(websites, sele_process)
        
        with ProcessPoolExecutor(max_workers=sele_process) as executor:
            futures = [executor.submit(sele_crawl_home, website) for website in splitted_sele_websites]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    log.error(e, exc_info=True)
                else:
                    selenium_result = future.result()
                    for res in selenium_result:
                        data.append(res)

    return data