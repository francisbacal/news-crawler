import newscrawler as crawler
from pprint import pprint

log = crawler.init_log('ArticleCrawler')

def get_articles(url: str, src_links: type(crawler.pageLinks)=None) -> list:
  """
  Get all article links in a url
  """
  log.debug(f"Getting articles from {url}")
  if not url or url == '':
    raise crawler.commonError("No url to crawl")

  try:
    if not src_links:
      links = src_links
    else:
      source = crawler.Source(url)
      links = crawler.pageLinks(source.page, source.r_url)

    log.debug('Source parsed')
    articles = links.getArticleLinks()
    
  except (crawler.commonError, crawler.sourceError) as e:
    log.error(e, exc_info=True)
    return []
  
  except Exception as e:
    log.error(e, exc_info=True)
  
  return articles