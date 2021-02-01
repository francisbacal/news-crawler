from pprint import pprint
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from ..exceptions import ArticleCrawlerError, commonError
from api import ArticleLinks, Website

import newscrawler as crawler, os, math, api, datetime

log = crawler.init_log('ArticleCrawler')

def get_articles(url: str, src_links: type(crawler.pageLinks)=None) -> list:
  """
  Get all article links in a url
  """
  log.debug(f"Getting articles from {url}")
  if not url or url == '':
    raise crawler.commonError("No url to crawl")

  try:
    if src_links:
      links = src_links
    else:
      source = crawler.Source(url)
      links = crawler.pageLinks(source.page, source.r_url)

    log.debug('Source parsed')
    articles = links.getArticleLinks()
    
  except crawler.commonError as e:
    log.error(e, exc_info=True)
    return []

  except crawler.sourceError as e:
    log.error(e)
    print(e)
    raise
  
  except Exception as e:
    log.error(e, exc_info=True)
    raise
  
  return articles

#---------- DYNAMIC METHOD ----------#

def sele_crawl(website: dict):
  """
  Article links extractor method
    @params:  website       -   Website dictionary with sections to be crawled
    @params:  browser       -   seledriver (selenium instance) browser   
  """
  log.debug(f"{sele_crawl.__name__} called")
  # EXTRACT DATA FROM WEBSITE DICT
  sections = website['main_sections']

  # DEFINE ARTICLES LIST
  data = website
  articles = []

  # DETERMINE NUMBER OF SPLIT
  section_size = len(sections)
  max_tabs = 10 if section_size > 10 else section_size
  ratio = section_size / max_tabs

  num_split = 2 if ratio == 1 else math.ceil(ratio)

  #SPLIT SECTIONS
  splitted_sections = crawler.list_split(sections, num_split)


  # ITERATE SECTIONS AND APPEND AS NEW TAB IN BROWSER
  for splitted in splitted_sections:

    # DEFINE SELENIUM INSTANCE USING SELEDRIVER MODULE
    seledriver = crawler.Seledriver()
    browser = seledriver.browser

    for section in splitted:
      browser.execute_script("window.open('"+section+"')")

    handle_size = len(browser.window_handles)
    wait = seledriver.wait(browser, 30)

    for _ in range(handle_size):
      browser.switch_to.window(browser.window_handles[-1])
      try:
        # WAIT UNTIL PAGE IS LOADED
        wait.until(lambda browser: browser.execute_script('return document.readyState') == 'complete')

        # GET SOURCE PAGE AND URL
        source = browser.page_source
        url = browser.current_url
        
        # GET ARTICLE LINKS
        links = crawler.pageLinks(source, url)
        parsed_links = links.getArticleLinks()
        
        # EXTEND PARSED ARTICLE LINKS TO ARTICLES AND FILTER DUPLICATES
        articles.extend(parsed_links)
        articles = list(OrderedDict.fromkeys(articles))

      except Exception as e:
        log.error(e, exc_info=True)
        print(e)
        pass
      finally:
        browser.close()
      
  browser.quit()

  # RETURN DATA
  data['articles'] = articles

  return data

def sele_crawl_init(websites: list):
  """
  Init selenium process to crawl articles
    @params:  websites      -   list of websites to be processed
  """

  # DEFINE DATA TO RETURN
  data = []
  
  with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(sele_crawl, website) for website in websites]

    for future in as_completed(futures):
      try:
        future.result()
      except Exception as e:
        log.error(f"Selenium Failed with message: {e}", exc_info=True)
        print(e)
        raise
      else:
        data.append(future.result())
  
  return data
    
#---------- STATIC METHOD ----------#

def article_crawl(website: dict):
    """
    Get all articles in website section
        @params:    section         -   dict object of website section from database to be crawled.
    """
    if not isinstance(website, dict):
        raise crawler.commonError("Invalid parameter type for website")

    # GET ITEMS FROM WEBSITE PARAMETER RETURN IF NO SECTIONS
    url = website['website_url']
    website_id = website['_id']
    sections = website['main_sections']

    #RAISE ERROR IF NO SECTIONS
    if not sections or not isinstance(sections, list):
      raise ArticleCrawlerError(f"No Section for website {url}")

    # CREATE ARTICLES LIST AND DATA TO RETURN
    articles = []
    data = {
        "website_id": website_id,
        "website_url": url,
        "main_sections": sections,
        "articles": articles,
        "error": False
    }


    # GET LINKS FOR EACH SECTION
    for section in sections:
      try:
          links = get_articles(section)
          articles.extend(links)
          articles = list(OrderedDict.fromkeys(articles)) #filter duplicates
      except crawler.sourceError:
          data['error'] = True
          break
      except Exception as e:
          log.error(e, exc_info=True)
          raise
    
    # DATA TO RETURN
    data['articles'] = articles
    
    return data

def article_crawl_pool(websites: list):
  """
  Thread Pool Method to crawl each website section
    @params:  websites    -   List of websites to be crawled
  """

  # RESULT VARIABLE DECLARATION
  for_selenium = []
  articles_data = []

  # THREADING EXECUTOR
  with ThreadPoolExecutor() as executor:
    futures = [executor.submit(article_crawl, website) for website in websites]

    for future in as_completed(futures):
      try:
        future.result()
      except Exception as e:
        raise
      else:
        result = future.result()
        if result['error']:
            for_selenium.append(result)
        else:
            articles_data.append(result)

  # RETURN DATA
  data = {
    "for_selenium": for_selenium,
    "articles_data": articles_data
  }

  return data

#---------- SAVE METHOD ----------#
def save_thread(article_url: str, article_website_id: str):
  articleLinksAPI = ArticleLinks(testing=True)
  save_data = {
          "website": article_website_id,
          "article_url": article_url
        }

  payload = articleLinksAPI.defaul_schema(save_data)
  response = articleLinksAPI.add(payload)
  
def save_pool(article_data):
  """
  Thread Pool Executor method caller
  """
  websiteAPI = Website()
  
  for data in article_data:
    if isinstance(data['articles'], list) and data['articles']:

      #CALL THREAD POOL MAP FOR SAVING
      article_website = data['website_id']
      articles = data['articles']

      with ThreadPoolExecutor() as executor:
        futures = [executor.submit(save_thread, article, article_website) for article in articles]

        for future in as_completed(futures):
          try:
            future.result()
          except api.DuplicateValue as e:
            log.error(e, exc_info=True)
            print(e)
            continue
          except Exception as e:
            log.error(e, exc_info=True)
            raise
      
      #UPDATE WEBSITE IN DATABASE

      date_updated = datetime.datetime.today().isoformat()

      update_payload = {
        "updated_by": "Python News Crawler"
      }

      try:
        websiteAPI.update(update_payload, article_website)
      except Exception as e:
        log.error(e, exc_info=True)
        raise ArticleCrawlerError("Error updating website")
    
    else:
      try:
        websiteAPI.update(update_payload, article_website)
      except Exception as e:
        log.error(e, exc_info=True)
        raise ArticleCrawlerError("Error updating website")


def save_articles(article_data: dict):
  """
  Save the scraped articles to articles database
  """

  #SPLIT DATA LIST
  CPU_COUNT = os.cpu_count() - 1
  PROCESSES = CPU_COUNT if len(article_data) > CPU_COUNT else len(article_data)

  splitted_articles = crawler.list_split(article_data, PROCESSES)

  #CALL MULTIPROCESSING METHOD
  with ProcessPoolExecutor(max_workers=PROCESSES) as executor:
    futures = [executor.submit(save_pool, article) for article in splitted_articles]

    for future in as_completed(futures):
      try:
        future.result()
      except Exception as e:
        log.error(e, exc_info=True)
        return "Error"


#---------- INIT METHOD ----------#

@crawler.logtime
def article_crawl_init(websites: list, num_process: int):
    """
    Method to initialize article crawling using concurrent futures Pool Executor
        @params:    websites            -   a list of queried websites
        @params:    num_process         -   number of process to be used for Pool
    """

    log.debug(f'Initializing Pool Process using {num_process}/{os.cpu_count()} cores')

    # SPLIT WEBSITES INTO num_process NUMBER OF LIST
    splitted_websites = crawler.list_split(websites, num_process)


    # DECLARATION OF VARIABLES FOR RESULT
    for_selenium = []
    data = []
    
    # FIRST POOL PROCESS TO CRAWL SECTIONS FOR ARTICLES VIA REQUESTS/CLOUDSCRAPER
    with ProcessPoolExecutor(max_workers=num_process) as executor:
        futures = [executor.submit(article_crawl_pool, website) for website in splitted_websites]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                raise
            else:
                pool_result = future.result()
                result_articles = pool_result['articles_data']
                result_for_selenium = pool_result['for_selenium']
                
                # APPEND RESULTS TO RESULT VARIABLES
                for articles in result_articles:
                    articles_data = {
                        "articles": articles['articles'],
                        "website_id": articles['website_id'],
                        "url": articles['website_url']
                    }

                    data.append(articles_data)

                # APPEND RESULT FOR SELENIUM
                if result_for_selenium:
                    for res in result_for_selenium:
                        for_selenium.append(res)

    ## POOL PROCESS FOR DYNAMIC WEBSITES
    if for_selenium:

        # DEFINE NUMBER OF SELENIUM INSTANCE FOR CRAWLING. COMPUTED AS NO. OF CPU / 2
        # OR WEBSITE LIST LENGTH WHICH EVER IS LOWER

        process_count = os.cpu_count()
        num_process = math.ceil(process_count / 2)
        sele_process = num_process if len(websites) > num_process  else len(websites)
        log.debug(f'Initializing Selenium Pool Process using {sele_process}/{os.cpu_count()} cores')

        # SPLIT LIST INTO NUMBER OF PROCESS LIST
        splitted_sele_websites = crawler.list_split(websites, sele_process)
        
        # MAIN MULTIPROCESS
        with ProcessPoolExecutor(max_workers=sele_process) as executor:
            futures = [executor.submit(sele_crawl_init, website) for website in splitted_sele_websites]

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