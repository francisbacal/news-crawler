from datetime import datetime, timedelta
from .datechecker import DateChecker
from ..options import *


class UpdateHelper(DateChecker):
  def __init__(self, website: dict, **kwargs):
    super().__init__()
    self.options = Options()
    self.options = extend_opt(self.options, kwargs)
    date_updated = website['date_updated']

    # CHECK SECTIONS
    try:
      sections = website['main_sections']
    except KeyError:
      sections = []

    self.date_updated = date_updated

    ## CHECK IF FOR SECTION UPDATE WHICH IS MORE THAN 2 WEEKS SINCE LAST UPDATE FROM TODAY OR NO SECTION IN DB
    two_weeks = self.less_week(self.date_updated, 2)
    is_weekend = self.is_weekend(self.today)
    
    self.for_section_update = True if any([two_weeks, not sections, is_weekend]) else False

    self.for_article_update = True if all([not self.is_today(self.date_updated), not is_weekend, not self.for_section_update]) else False