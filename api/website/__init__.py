from urllib.parse import urlparse
from .api import Website
import tldextract


from .schema import WebsiteSchema
from ..exceptions import websiteAPIError, DuplicateValue
