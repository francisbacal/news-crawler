from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pprint import pprint
from newscrawler import init_log
from itertools import islice, chain
from collections import OrderedDict
from api import Website
from newscrawler import Seledriver
import newscrawler as crawler, os

log = init_log('MultiArticle')

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