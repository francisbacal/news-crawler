from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website
from newscrawler import Seledriver
import newscrawler as crawler, os

log = init_log('MultiArticle')
websiteAPI = Website()

# def list_split(input_list: list, number_of_split: int) -> list:
#     """
#     Splits list into number_of_split list
#     """

#     if not input_list:
#         return []

#     new_list = iter(input_list)

#     result = []
#     q, r = divmod(len(input_list), number_of_split)
    
#     for _ in range(r):
#         result.append(list(islice(new_list, q+1)))
#     for _ in range(number_of_split - r):
#         result.append(list(islice(new_list, q)))

#     return result

def get_articles(url: str) -> list:
    log.debug(f"Getting articles for {url}")
    crawler.rand_sleep(3,6)
    try:
        source = crawler.Source(url)
        links = crawler.pageLinks(source.page, source.r_url)
        articles = links.getArticleLinks()
        
    except crawler.commonError as e:
        log.error(e, exc_info=True)
        print(e)
        return []
    except crawler.sourceError:
        raise
    except Exception as e:
        log.error(e, exc_info=True)
        print(e)
    
    return articles

def main_pool(url_list, func, n_thread):
    result = []
    
    with ThreadPoolExecutor(max_workers=n_thread) as e:
       
        futures = [e.submit(func, url) for url in url_list]
        
        for f in as_completed(futures):
            try:
                data = f.result()
            except crawler.sourceError:
                raise
            else:
                result.append(f.result())
    return list(chain.from_iterable(result))

@crawler.logtime
def main(url_list, func, num_process):

    #split list to NUM_PROCESS number of list
    input_list = crawler.list_split(url_list, num_process)

    #declare num of threads
    n_thread = 3
    
    result = []
    with ProcessPoolExecutor(max_workers=num_process) as executor:
        # futures = executor.map(main_pool, input_list, [func] * len(input_list), [n_thread] * len(input_list))
        futures = [executor.submit(main_pool, url, func, n_thread) for url in input_list]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception:
                raise
            else:
                result.append(future.result())

    
    return result

def pool_sele(url_list):
    #instantiate selenium driver
    seledriver = Seledriver(headless=True)
    browser = seledriver.browser

    for url in url_list:
        log.debug(f'Opening {url}')
        browser.execute_script("window.open('"+url+"')")
    
    result = []

    for _ in range(len(browser.window_handles)):
        try:
            browser.switch_to.window(browser.window_handles[-1])
            wait = seledriver.wait(browser,20)
            wait.until(lambda browser: browser.execute_script('return document.readyState') == 'complete')

            source = browser.page_source
            r_url = browser.current_url

            links = crawler.pageLinks(source, r_url)
            articles = links.getArticleLinks()
            log.debug(f"{len(articles)} articles found in {r_url}")
            result = result + articles

        except:
            pass

        finally:
            log.debug(f'Closing {url}')
            browser.close()
    
    browser.quit()
    
    return result


@crawler.logtime
def main_sele(url_list: list, num_process: int):
    #split list to NUM_PROCESS number of list
    input_list = crawler.list_split(url_list, num_process)

    result = []
    with ProcessPoolExecutor(max_workers=num_process) as executor:
        # futures = executor.map(pool_sele, input_list)
        futures = [executor.submit(pool_sele, url_list) for url_list in input_list]

        for future in as_completed(futures):
            try:
                future.result()
            except:
                print("sele error")

            result.append(future.result())

    return result

if __name__ == '__main__':
    log.debug("Multiprocessing init")
    # sections = websiteAPI.get_one("5f044bfe417ae14930b88fcb")['main_sections']
    # pprint(sections)
    # quit()
    
    sections = ['https://www.pep.ph/videos',
        'https://www.pep.ph/news',
        'https://www.pep.ph/news/local',
        'https://www.pep.ph/news/foreign',
        'https://www.pep.ph/news/kuwentong-kakaiba',
        'https://www.pep.ph/pepalerts',
        'https://www.pep.ph/pepalerts/cabinet-files',
        'https://www.pep.ph/label/scoop',
        'https://www.pep.ph/pepalerts/pep-troika',
        'https://www.pep.ph/pepalerts/labandera-chronicles',
        'https://www.pep.ph/pepalerts/fyi',
        'https://www.pep.ph/guide/',
        'https://www.pep.ph/guide/arts-and-culture',
        'https://www.pep.ph/label/review',
        'https://www.pep.ph/guide/movies',
        'https://www.pep.ph/label/exclusive',
        'https://www.pep.ph/guide/music',
        'https://www.pep.ph/guide/tv']

    #declare numnber of process for article links extraction
    NUM_PROCESS = os.cpu_count() - 1

    #run main process method
    try:
        result = main(sections, get_articles, NUM_PROCESS)
        result = list(chain.from_iterable(result))
    except crawler.sourceError:
        print('ERROR')

    try:
        result = main_sele(sections, NUM_PROCESS)
        result = list(chain.from_iterable(result))
    except:
        print("ERROR MAIN SELE")

    #filter duplicates
    pprint(result)
    articles = list(OrderedDict.fromkeys(result)) 
    
    pprint(articles)
    log.debug("Multiprocessing end")