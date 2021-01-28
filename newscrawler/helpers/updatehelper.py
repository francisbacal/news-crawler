from datetime import datetime, timedelta

class UpdateHelper:
  def __init__(self, website: dict):
    date_updated = website['date_updated']
    sections = website['sections']

    self.date_updated = date_updated.date()
    
    ## DEFINE DATE TODAY:
    today = datetime.today().date()

    ## CHECK IF FOR SECTION UPDATE WHICH IS MORE THAN 7 DAYS SINCE LAST UPDATE FROM TODAY
    seven_days = today - timedelta(7)
    self.for_section_update = True if self.date_updated < seven_days else True if not sections else False