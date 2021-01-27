from .model.modeldata import ModelData
from .vars import logs
from .exceptions import helperError
from itertools import islice, chain
import pandas as pd, joblib, sklearn, random, time, logging, logging.config, os, datetime

#---------- LOG CONFIGS ----------#
class FileFilter:

    def __call__(self, log):
        if log.levelno == logging.INFO:
            return 1
        else:
            return 0

class DebugFilter:
  
  def __call__(self, log):
    if log.levelno == logging.DEBUG:
      return 1
    else:
      return 0

logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'error_formatter': {
            'format': '{asctime} - {name} - {levelname} - line {lineno} - {message}',
            'style': '{',
            'datefmt': '%d/%m/%y - %H:%M:%S',
        },
        'debug_formatter': {
            'format': '{asctime} - {name} - {levelname} - {message}',
            'style': '{',
            'datefmt': '%d/%m/%y - %H:%M:%S',
        },
    },
    'filters': {
        'file_filter': {
            '()': FileFilter,
        },
        'debug_filter': {
          '()': DebugFilter,
        }
    },
    'handlers': {
        'error_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'error_formatter',
            'level': 'ERROR',
            'filename': '/tmp/logs/newscrawler/errors.log',
        },
        'info_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'debug_formatter',
            'filters': ['file_filter'],
            'filename': '/tmp/logs/newscrawler/app.log',
        },
        'debug_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'debug_formatter',
            'filters': ['debug_filter'],
            'filename': '/tmp/logs/newscrawler/debug.log',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['error_handler','info_handler', 'debug_handler'],
    },
}

#---------- LOGS ----------#
def disable_logs():
    loggers = ['filelock', 'chardet.charserprober']

    for logger in loggers:
        logging.getLogger(logger).disabled = True

    # for name, logger in logging.Logger.manager.loggerDict.items():
    #     if name not in logs:
    #         logging.getLogger(name).disabled = True

def init_log(name):
    os.makedirs(os.path.dirname('/tmp/logs/newscrawler/'), exist_ok=True)
    logging.config.dictConfig(logging_config)
    log = logging.getLogger(name)
    disable_logs()

    for logger in logs:
        logging.getLogger(logger).disabled = False

    return log


#---------- RANDOM SLEEP ----------#
def rand_sleep(min: int=3, max: int=10):

    RANDOM_SEC = random.randint(min, max)
    DIFF = random.randint(1, 2) - random.random()

    SLEEP_TIME = RANDOM_SEC - DIFF
    time.sleep(SLEEP_TIME)

#---------- TIME CONVERT ----------#
def time_convert(start_time, end_time):
    seconds = end_time - start_time
    hours = round((seconds / 3600), 2)
    minutes = round((seconds / 60), 2)

    if hours > 1:
        return f"{hours} hrs"
    elif minutes > 1:
        return f"{minutes} mins"
    elif seconds > 0:
        return f"{seconds} secs"
    else:
        return f"0 sec"

#---------- EXECUTION TIME DECORATOR ----------#
def logtime(method):
    log = init_log('TIME-LOG')
    def log_time(*args, **kwargs):

        start_time = time.time()
        result = method(*args, **kwargs)
        end_time = time.time()

        log.debug(f"{method.__name__} finished in: {time_convert(start_time, end_time)}")

        return result
    return log_time

#---------- ERROR CATCHER ----------#
errors = {'None': None, 'list': [], 'dict': {}, 'article_error': 'Error'}
def catch(default, func, handle=lambda e: e, *args, **kwargs):
    """
    Catching errors
    @params
        default   - Required    : key values on error dict - 'None', 'list', 'dict' (String)
        func      - Required    : lambda handle (Lambda Function)
    """
    log = init_log(func.__name__)
    try:
        return func(*args, **kwargs)
        
    except Exception as e:
        log.error(e)
        return errors[default]

#---------- SPLIT LIST ----------#
def list_split(input_list: list, number_of_split: int) -> list:
    """
    Splits list into number_of_split list
    """

    if not input_list:
        return []

    new_list = iter(input_list)

    result = []
    q, r = divmod(len(input_list), number_of_split)
    
    for _ in range(r):
        result.append(list(islice(new_list, q+1)))
    for _ in range(number_of_split - r):
        result.append(list(islice(new_list, q)))

    return result

#---------- DATE CHECKER  ----------#
def is_today(date_input):
    today = datetime.datetime.today().date()

    if not isinstance(date_input, datetime.datetime):
        raise helperError("Method: is_today. Invalid date type. Must be an instance of datetime.datetime")

    
    if not today == date_input.date():
        return False

    else:
        return True


#---------- URL VERIFIER ----------#
def is_same_domain(url)
#---------- GET TYPE OF PATH METHOD ----------#
def get_path_type(path: str, clf: type(sklearn)) -> str:
    """
    Get type/category of url path. Returns a type/category of string type
        @params:      path         -     path of parsed url
    """
    category = 'section'
    modelData = ModelData(category)

    result = pd.DataFrame(columns=('path', 'path length', 'include', 'exclude', 'double slash count', 'dot count', 'sub directory count', 'last dir num words', 'length of query', 'type'))
    results = modelData.extract_features(path, category)

    #result = pd.DataFrame(columns=('path', 'path length', 'include', 'exclude', 'double slash count', 'sub directory count', 'length of query', 'type'))
    #results = extract_features(path, category)

    result.loc[0] = results
    result = result.drop(['path','type'],axis=1).values
    
    return clf.predict(result)[0]
