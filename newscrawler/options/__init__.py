

class Options:
  def __init__(self):
    self.testing = False

def extend_opt(options, options_items: dict):
    """
    extend kwargs to options
    """
    for key, val in list(options_items.items()):
        if hasattr(options, key):
            setattr(options, key, val)

    return options