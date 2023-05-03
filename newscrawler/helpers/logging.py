from ..vars import logs
import logging, os

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