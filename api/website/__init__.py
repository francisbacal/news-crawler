from urllib.parse import urlparse
from .api import Website
from ..exceptions import PayloadError
import tldextract


from .schema import WebsiteSchema
from ..exceptions import websiteAPIError, DuplicateValue
from newscrawler import DateChecker, country_names


def generate_payload(countries=[], raw_website: bool=False) -> dict:
    """
    Generate a payload of websites
        @params:    country         -   Country name. Accepts string or list of strings
        @params:    raw_website     -   Pass True if to query in raw website DB. [Default: False]
    """
    date_checker = DateChecker()
    
    if not isinstance(countries, list) and not isinstance(countries, str):
        raise PayloadError('Invalid countries type. Must be a list')

    if isinstance(countries, str):
        countries = [countries]

    COUNTRIES = [country.lower().capitalize() for country in countries if country.lower().capitalize() in country_names]

    # QUERY TO RAW WEBSITES
    if raw_website:
        PAYLOAD = {
            "query": {
                "country": {"$in": COUNTRIES},
                "date_updated": {"$lt": date_checker.today.isoformat()}
                }
            }

    # QUERY TO MAIN DB
    else:
        PAYLOAD = {
            "country": {"$in": COUNTRIES},
            "date_updated": {"$lt": date_checker.today.isoformat()}
        }

    # VALIDATE IF EMPTY LIST
    if not COUNTRIES:
        del PAYLOAD['country']

    return PAYLOAD