class websiteAPIError(Exception):
    def __init__(self, url: str, err_msg=None):
        self.url = url
        self.message = f"Error occured on website api, {err_msg} "
        super().__init__(self.message)

class articleLinksAPIError(Exception):
    def __init__(self, url: str, err_msg=None):
        self.url = url
        self.message = f"Error occured on article links api, {err_msg} "
        super().__init__(self.message)

class DuplicateValue(Exception):
  def __init__(self, data):
    self.message = f"Duplicate data found in database: {data}"
    super().__init__(self.message)