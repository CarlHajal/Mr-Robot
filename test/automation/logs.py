#SETUP LOGS
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler

from automation.encoder import log as encoder_log
from automation.sensor import log as sensor_log
from automation.estop import log as estop_log
from automation.actuators import log as act_log

rootLogHandler = RotatingFileHandler('root.log', maxBytes=1*1024*1024, backupCount=5)
rootLogFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rootLogHandler.setFormatter(rootLogFormatter)

    

def createLogger(name):
    log = logging.getLogger(name)
    handler = RotatingFileHandler('logs/'+name+'.log', maxBytes=0.5*1024*1024, backupCount=2)
    formatter = logging.Formatter('%(asctime)s,%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.addHandler(rootLogHandler)
    return log

def initializeSystemLoggers():

    loggers = [encoder_log, sensor_log, estop_log, act_log]
    handler = RotatingFileHandler('root.log', maxBytes=1*1024*1024, backupCount=5)

    for _logger in loggers:
        _logger.setLevel(logging.DEBUG)
        _logger.addHandler(rootLogHandler)
