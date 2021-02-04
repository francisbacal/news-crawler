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
from ..exceptions import SectionCrawlerError

import newscrawler as crawler, os, math, time

log = init_log('MultiSection')
websiteAPI = Website()

# TODO: REFACTOR CODE TO SAVE AFTER CRAWLING ONE WEBSITE


def get_links(url: str, home_url: str=None) -> list:
    """
    Main function to get sections and articles
        @params:    url         -   website url
    """
    log.debug(f"Getting Sections for {url}")
    try:
        # GET SOURCE AND LINKS FROM URL
        source = crawler.Source(url)

        #VALIDATE source.page
        source_page = crawler.catch('None', lambda: source.page)
        if not source_page:
            raise crawler.sourceError('No source parsed')

        links = crawler.pageLinks(source_page, source.r_url, home_url)
        
        # GET SECTIONS FROM URL
        sections = links.getSectionLinks()

        # GET ARTICLES FROM URL
        log.debug(f"Getting articles for {url}")
        articles = get_articles(url, links)
        
    except crawler.commonError as e:
        log.error(e, exc_info=True)
        print(e, url)
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

def crawl_sections(url: str, home_url: str, iter_items: dict, repeat: int=2, iteration: int=1):
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
        links = get_links(url, home_url)
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
                    crawl_result = crawl_sections(section, home_url, iter_items_data, iteration=current_iteration)

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
        futures = [executor.submit(crawl_sections, section, url_dict['website_url'], iter_items, iteration=1) for section in _sections]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                raise
            else:
                result = future.result()
                try:
                    # EXTEND RESULT SECTIONS
                    sections.extend(result['sections'])

                    # EXTEND RESULT ARTICLES
                    articles.extend(result['articles'])
                except TypeError:
                    pass

    
    sections = list(OrderedDict.fromkeys(sections))
    articles = list(OrderedDict.fromkeys(articles))

    data = {
        "website_id": url_dict['website_id'],
        "url": url_dict['website_url'],
        "country": url_dict['country'],
        "fqdn": url_dict['fqdn'],
        "country_code": url_dict['country_code'],
        "main_sections": sections,
        "articles": articles
    }

    return data

def get_home(website: dict, raw_website=False) -> dict:
    """
    Get all sections in home page
        @params:    website         -   dict object of website from database to be crawled.
    """
    if not isinstance(website, dict):
        raise crawler.commonError("Invalid parameter type for website")

    # GET ITEMS FROM WEBSITE PARAMETER
    if raw_website:
        url = website['url']
    else:
        url = website['website_url']

    website_id = website['_id']

    # CREATE INITIAL RETURN DATA
    data = {
        "website_id": website_id,
        "website_url": url,
        "fqdn": website['fqdn'],
        "country": website['country'],
        "country_code": website['country_code'],
        "home_sections": None,
        "home_articles": None,
        "error": False
    }

    log.debug(f"get_home method called for {url}")

    # GET LINKS
    try:
        links = get_links(url, url)

        data['home_sections'] = links['sections']
        data['home_articles'] = links['articles']
    except crawler.sourceError:
        data['error'] = True
    except Exception as e:
        log.error(e, exc_info=True)
        print(e)
        raise


    # TODO: CALL RECURSIVE CRAWLING HERE
    ## FOR NON ERROR WEBSITES

    if not data['error']:


    # return data

def section_crawl_home(websites: list) -> dict:
    """
    Crawl sections in home page by using ThreadPoolExecutor
        @params:    websites            -   a list of splitted websites from section_crawl_init
    """

    home_data = []
    for_selenium = []

    log.debug(f"Crawling Home Pages...")
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_home, website, raw_website=True) for website in websites] # query from raw website db. Remove parameter raw_website if will query on main website db

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

def sele_section_crawl_home(websites: list):
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
            "website_url": url,
            "fqdn": website['fqdn'],
            "country": website['country'],
            "country_code": website['country_code'],
            "main_sections": [],
            "articles": []
        }

        # APPEND DATA TO RESULT
        results.append(data)

        # Open New Tab and visit url
        browser.execute_script("window.open('"+url+"')")
    
    for result in results:
        print(f"Processing {result['website_url']}")
        wait = seledriver.wait(browser, 5)
        for x in range(len(browser.window_handles)):
            browser.switch_to.window(browser.window_handles[x])

            # Clean URLS
            browser_cleanurl = crawler.CleanURL(browser.current_url)
            result_cleanurl = crawler.CleanURL(result['website_url'])


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
                        result['main_sections'] = sections
                    
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


#---------- SAVE METHOD ----------#
def save_article_thread(article_url: str, article_website_id: str):
    articleLinksAPI = ArticleLinks(testing=False)
    save_data = {
            "website": article_website_id,
            "article_url": article_url
            }
    payload = articleLinksAPI.defaul_schema(save_data)
    response = articleLinksAPI.add(payload)
  
def save_pool(section_data):
    """
    Thread Pool Executor method caller
    """
    websiteAPI = Website()

    for data in section_data:

        #UPDATE OR ADD WEBSITE IN DATABASE
        date_created = datetime.today().isoformat()
        date_updated = datetime.today().isoformat()

        #SAVE / UPDATE DB
        try:
            article_website = websiteAPI.add(data, data['website_id'])
            websiteAPI.update({}, data['website_id'], raw_website=True)
        except DuplicateValue:
            website_id = websiteAPI.get({"fqdn": data['fqdn']}, limit=1, raw_website=False)[0]['_id']
            article_website = websiteAPI.update(data, website_id, raw_website=False)
            websiteAPI.update({}, data['website_id'], raw_website=True)
        except Exception as e:
            print(e)
            raise

        #CALL THREAD POOL MAP FOR SAVING
        articles = data['articles']

        if articles:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(save_article_thread, article, article_website['_id']) for article in articles]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except DuplicateValue as e:
                        log.error(e, exc_info=True)
                        print(e)
                        continue
                    except Exception as e:
                        log.error(e, exc_info=True)
                        raise

def save_section(section_data: dict):
    """
    Save the scraped articles to articles database
    """

    #SPLIT DATA LIST
    CPU_COUNT = os.cpu_count() - 1
    PROCESSES = CPU_COUNT if len(section_data) > CPU_COUNT else len(section_data)

    splitted_sections = crawler.list_split(section_data, PROCESSES)

    #CALL MULTIPROCESSING METHOD
    with ProcessPoolExecutor(max_workers=PROCESSES) as executor:
        futures = [executor.submit(save_pool, section) for section in splitted_sections]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                log.error(e, exc_info=True)
                return "Error"
    
    return "SAVED"

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
        futures = [executor.submit(section_crawl_home, website) for website in splitted_websites]

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
                        "website_url": home_data['website_url'],
                        "fqdn": home_data['fqdn'],
                        "country": home_data['country'],
                        "country_code": home_data['country_code'],
                    }

                    article_data = {
                        "home_articles": home_data['home_articles'],
                        "website_id": home_data['website_id'],
                        "website_url": home_data['website_url']
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

    ## POOL PROCESS FOR DYNAMIC WEBSITES
    if for_selenium:
        process_count = os.cpu_count() - 1
        num_process = math.ceil(process_count / 2)
        sele_process = num_process if len(websites) > num_process  else len(websites)
        log.debug(f'Initializing Selenium Pool Process using {sele_process}/{os.cpu_count()} cores')

        splitted_sele_websites = crawler.list_split(websites, sele_process)
        
        with ProcessPoolExecutor(max_workers=sele_process) as executor:
            futures = [executor.submit(sele_section_crawl_home, website) for website in splitted_sele_websites]

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