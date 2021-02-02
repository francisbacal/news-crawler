from api import ArticleLinks

articlesAPI = ArticleLinks(testing=True)

query = {
    "created_by": "Python News Crawler"
}

articles = articlesAPI.get(query, limit=10000)

for article in articles:
    articlesAPI.delete_test(article['_id'])