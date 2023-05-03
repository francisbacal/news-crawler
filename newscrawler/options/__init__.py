import os

class Options:
  def __init__(self):
    self.raw_website = False
    self.testing = False
    self.limit = 1
    self.token = f"Bearer {os.environ['API_TOKEN']}"
    self.country = "Philippines"

def extend_opt(options, options_items: dict):
    """
    Extend kwargs to options
      @params:  options       -   Options class
      @params:  options_items -   Items to extend to options if key matches an option in Options class
    """
    for key, val in list(options_items.items()):
        if hasattr(options, key):
            setattr(options, key, val)

    return options