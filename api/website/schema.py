from datetime import datetime

class WebsiteSchema:
    """
    Website Schema
    """
    def __init__(self, schema: dict = {}):
        self.schema = self.__default() if not schema else schema

    def __default(self):
        return {
            "name": None,
            "url": None,
            "fqdn": None,
            "icon": None,
            "costs": 0,
            "language": "Unknown",
            "region": "Unknown",
            "country": "Unknown",
            "country_code": "NoC",
            "programming_language": "Python",
            "sections": [],
            "verified": False,
            "scrape": True,
            "created_by": "Python Global Scraper",
            "updated_by": "Python Global Scraper",
            "date_created": datetime.today().isoformat(),
            "date_updated": datetime.today().isoformat(),
            "alexa_rankings": {"global": 0, "local": 0},
        }

# {
#     "alexa_rankings": {
#         "global": 0,
#         "local": 0
#     },
#     "similar_websites": [
#         "hnzc.co.nz"
#     ],
#     "verified": false,
#     "in_website_collection": false,
#     "country": "Germany",
#     "country_code": "DEU",
#     "created_by": "System",
#     "updated_by": "System",
#     "date_created": "2021-01-20T14:59:18.212Z",
#     "date_updated": "2021-01-22T14:55:58.868Z",
#     "_id": "6008457b7e8b804af10683ce",
#     "name": "Govt",
#     "url": "http://govt.co.nz",
#     "fqdn": "govt.co.nz",
#     "__v": 0
# },
# New website schema:
#         "section_filter", -- DELETE
#         "article_filter", -- DELETE
#         "alexa_rankings",
#         "website_icon_url",
#         "website_cost",
#         "website_language",
#         "main_sections", -- DELETE
#         "sub_sections", -- DELETE
#         "website_category", -- CHECK
#         "website_type",
#         "status",
#         "region",
#         "country",
#         "country_code",
#         "needs_search_params",
#         "needs_https",
#         "needs_endslash",
#         "has_subsection",
#         "date_created",
#         "date_updated",
#         "programming_language",
#         "request_source",
#         "is_dynamic_website",
#         "is_using_selectors", -- DELETE
#         "is_using_snippets", -- DELETE
#         "code_snippet", -- DELETE
#         "created_by",
#         "updated_by",
#         "website_scraper_delay",
#         "embedded_sections", -- DELETE
#         "is_aggregator",
#         "is_to_be_scraped",
#         "website_name",
#         "website_url",
#         "fqdn",