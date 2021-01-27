from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website
from newscrawler import Seledriver

import newscrawler as crawler, os

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
        log.debug('Source Error. Trying Selenium')
        seledriver = Seledriver()
        browser = seledriver.browser
        # browser.get(url)
        browser.execute_script("window.location.replace('"+url+"');")
        wait = seledriver.wait(browser, 20)
        wait.until(lambda browser: browser.execute_script('return document.readyState') == 'complete')

        source = browser.page_source
        r_url = browser.current_url

        browser.close()
        browser.quit()

        links = crawler.pageLinks(source, r_url)
        sections = links.getSectionLinks()

    except Exception as e:
        log.error(e, exc_info=True)
        raise
    
    return sections

iter_sections = []
def crawl_sections(url: str):
    """
    Recursive function to get all section links
    """
    log.debug(f"Crawling Recursively {url}")
    sections = get_sections(url)

    try:
        if sections and isinstance(sections, list):
            for section in sections:
                if section not in iter_sections:
                    iter_sections.append(section)
                    log.debug(f"crawling section {section}")
                    crawl_sections(section)
    except Exception as e:
        print(e)

    pprint(iter_sections)
    result = iter_sections
    return result

def main_threading(url_list: list):
    
    log.debug("main_threading started")
    if not isinstance(url_list, list):
        raise TypeError('Invalid url_list type. Must be a list')

    workers = 3
    result = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        
        futures = [executor.submit(crawl_sections, url)for url in url_list]

        for future in as_completed(futures):
            try:
                future.result()
            except crawler.sourceError:
                raise
            except Exception:
                log.error('Problem with section crawler', exc_info=True)
            else:
                result.append(future.result())

    log.debug("Done main_threading")
    return list(chain.from_iterable(result))

def main_pool(url):
    initial_sections = get_sections(url)
    sections = main_threading(initial_sections)
    
    return sections
@crawler.logtime
def section_crawl_init(urls, num_process):
    print('INIT')
    log.debug(f'Section Crawler Init - Crawling {url}')
    if not isinstance(url, list):
        raise TypeError("Invalid url type passed to section crawler. Expecting list")

    url_list = crawlet.list_split(urls, num_process)

    sections = []
    with ProcessPoolExecutor(max_workers=num_process) as executor:
        futures = [executor.submit(main_pool, url) for url in url_list]

        for future in as_completed(futures):
            try:
                futures.result()
            except Exception as e:
                raise
            else:
                sections.append(futures.result())

    # initial_sections = get_sections(url)
    # sections = main_threading(initial_sections, num_process)

    log.debug(f'Section Crawler Finished')
    return list(OrderedDict.fromkeys(sections))

if __name__ == '__main__':
   

    if not urls:
        raise crawler.commonError("NoneType or Empty list not allowed")

    #declare numnber of process for article links extraction
    process_count = os.cpu_count - 1
    NUM_PROCESS = process_count if len(urls) > process_count  else len(urls)

    #run main process method
    try:
        result = section_crawl_init(urls, NUM_PROCESS)
    except crawler.sourceError as e:
        log.debug(f"Source Error: {e}")
    except Exception as e:
        print(e)

    #filter duplicates
    sections = list(OrderedDict.fromkeys(result)) 
    
    pprint(sections)
    log.debug("DONE")
