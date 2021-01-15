from newscrawler.model.trainmodel import TrainData
from newscrawler import commonError
import sys
###
#   Runs a training process to generate classifier for either section or article
#
###
try:
    if sys.argv != ['']:
        argv = sys.argv
        data = str(argv[1])
    else:
        raise commonError("Invalid parameters/arguments passed on train.py - accepted values are 'article' and 'section')")
except IndexError:
    raise commonError("No parameters found while trying to run train.py")


TrainData(data)