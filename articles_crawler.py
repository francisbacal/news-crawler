import pandas as pd, joblib, newscrawler as crawler
from multiprocessing import Pool
from pprint import pprint

## Disable unwanted logs
crawler.disable_logs()

log = crawler.init_log('ArticleCrawler')
logtime = crawler.logtime


def get_articles(url: str) -> list:
  try:
    source = crawler.Source(url)
    links = crawler.pageLinks(source.page, source.r_url)
    articles = links.getArticleLinks()
  except (crawler.commonError, crawler.sourceError) as e:
    log.error(e, exc_info=True)
    return []
  
  return articles

iter_articles = []
def crawl_articles(url: str):

  articles = get_articles(url)

  if articles and isinstance(articles, list):
    for article in articles:
      if article not in iter_articles: 
        iter_articles.append(article)
        crawl_articles(article)

def main(url: str):
  crawl_articles(url)

if __name__ == '__main__':

  url = "https://www.philstar.com/"

  sections = ['http://www.philstar.com',
 'http://www.philstar.com/headlines',
 'http://www.philstar.com/pilipino-star-ngayon/probinsiya',
 'http://www.philstar.com/opinion',
 'http://www.philstar.com/nation',
 'http://www.philstar.com/world',
 'http://www.philstar.com/business',
 'http://www.philstar.com/sports',
 'http://www.philstar.com/entertainment',
 'http://www.philstar.com/lifestyle',
 'http://www.philstar.com/other-sections/news-feature',
 'http://www.philstar.com/campus',
 'http://www.philstar.com/movies',
 'http://www.philstar.com/music',
 'http://www.philstar.com/lifestyle/arts-and-culture',
 'http://www.philstar.com/lifestyle/business-life',
 'http://www.philstar.com/lifestyle/health-and-family',
 'http://www.philstar.com/lifestyle/fashion-and-beauty',
 'http://www.philstar.com/lifestyle/for-men',
 'http://www.philstar.com/lifestyle/food-and-leisure',
 'http://www.philstar.com/lifestyle/young-star',
 'http://www.philstar.com/lifestyle/ystyle',
 'http://www.philstar.com/lifestyle/shopping-guide',
 'http://www.philstar.com/lifestyle/modern-living',
 'http://www.philstar.com/lifestyle/supreme',
 'http://www.philstar.com/lifestyle/sunday-life',
 'http://www.philstar.com/lifestyle/gadgets',
 'http://www.philstar.com/lifestyle/travel-and-tourism',
 'http://www.philstar.com/lifestyle/on-the-radar',
 'http://www.philstar.com/lifestyle/pet-life',
 'http://www.philstar.com/lifestyle/allure',
 'http://www.philstar.com/business/business-as-usual',
 'http://www.philstar.com/business/banking',
 'http://www.philstar.com/business/motoring',
 'http://www.philstar.com/business/real-estate',
 'http://www.philstar.com/business/telecoms',
 'http://www.philstar.com/business/agriculture',
 'http://www.philstar.com/business/technology',
 'http://www.philstar.com/business/biz-memos',
 'http://www.philstar.com/business/science-and-environment',
 'http://www.philstar.com/other-sections/education-and-home',
 'http://www.philstar.com/other-sections/starweek-magazine',
 'http://www.philstar.com/other-sections/newsmakers',
 'http://www.philstar.com/other-sections/supplements',
 'http://www.philstar.com/other-sections/the-good-news',
 'http://www.philstar.com/other-sections/letters-to-the-editor',
 'http://www.philstar.com/the-freeman/cebu-news',
 'http://www.philstar.com/the-freeman/opinion',
 'http://www.philstar.com/the-freeman/metro-cebu',
 'http://www.philstar.com/the-freeman/region',
 'http://www.philstar.com/the-freeman/cebu-business',
 'http://www.philstar.com/the-freeman/cebu-sports',
 'http://www.philstar.com/the-freeman/cebu-lifestyle',
 'http://www.philstar.com/the-freeman/cebu-entertainment',
 'http://www.philstar.com/other-sections/daily-bread',
 'http://www.philstar.com/other-sections/word-of-the-day',
 'http://www.philstar.com/communities-of-the-future',
 'http://www.philstar.com/tags/covid-19-vaccine',
 'http://www.philstar.com/tags/rcbc']
  
  # main()
  # pprint(iter_articles)
  result = []
  for section in sections[0:5]:
    articles = get_articles(section)

    if articles:
      for article in articles:
        if article not in result:
          result.append(article)

  pprint(article)
  with open("articles_result.txt", "w") as f:
    for r in result:
      f.write(r)
      f.write('\n')