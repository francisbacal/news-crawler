import pandas as pd, joblib, newscrawler as crawler, logging, time
from multiprocessing import Pool
from pprint import pprint

## Disable unwanted logs
crawler.disable_logs()

log = crawler.init_log('SectionCrawler')
logtime = crawler.logtime

def get_sections(url: str) -> list:
  """
  Main function to get section links
  """
  try:
    source = crawler.Source(url)
    links = crawler.pageLinks(source.page, source.r_url)
    sections = links.getSectionLinks()
  except (crawler.commonError, crawler.sourceError) as e:
    print(e)
    return []
  
  return sections

iter_sections = []

def crawl_sections(url: str):
  """
  Recursive function to get all section links
  """
  sections = get_sections(url)

  if sections and isinstance(sections, list):
    for section in sections:
      if section not in iter_sections: 
        iter_sections.append(section)
        log.debug(f"crawling section {section}")
        crawl_sections(section)

@logtime
def main(url):
  log.debug(f'Section Crawler Init - Crawling {url}')
  crawl_sections(url)

if __name__ == '__main__':
  url = "https://www.philstar.com/"
  # url = "https://www.rappler.com"
  # url = "https://www.cnn.com"
  
  # crawl_sections(url)
  main(url)
  pprint(iter_sections)


