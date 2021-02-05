class commonError(Exception):
  def __init__(self, error=None):
    self.error = error
    self.message = f"Error encountered: '{self.error}'"
    super().__init__(self.message)

class sourceError(Exception):
  def __init__(self, url: str, err_msg=None):
    self.url = url
    self.message = f"Error occured while getting page source for {self.url}, {err_msg} "
    super().__init__(self.message)

class pageLinksError(Exception):
  def __init__(self, message: str=""):
    super().__init__(message)

class modelError(Exception):
  def __init__(self, message: str):
    super().__init__(message)

class trainingError(Exception):
  def __init__(self, message: str):
    super().__init__(message)

class helperError(Exception):
  def __init__(self, message: str):
    super().__init__(message)

class ArticleCrawlerError(Exception):
  def __init__(self, message: str):
    super().__init__(message)

class SectionCrawlerError(Exception):
  def __init__(self, message: str):
    super().__init__(message)