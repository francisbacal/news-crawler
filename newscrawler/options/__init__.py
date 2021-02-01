

class Options:
  def __init__(self):
    self.raw_website = False
    self.testing = False
    self.limit = 1
    self.token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.f2X7W_6J8g6y-jKto1fMj5zq7QkOLu9WBGw5b-sHAIc"
def extend_opt(options, options_items: dict):
    """
    extend kwargs to options
    """
    for key, val in list(options_items.items()):
        if hasattr(options, key):
            setattr(options, key, val)

    return options