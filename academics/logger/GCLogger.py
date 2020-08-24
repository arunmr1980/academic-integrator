import logging
from academics.logger.NotificationHandler import NotificationStreamHandler

logger = logging.getLogger('academic-integrator')
hdlr = logging.FileHandler('academicintegrator.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

# errHandler = NotificationStreamHandler()
# errHandler.setLevel(logging.WARN)
# logger.addHandler(errHandler)

def info(msg):
    logger.info(msg)

def debug(msg):
    logger.debug(msg)

def warn(msg):
    logger.warn(msg)

def error(msg):
    logger.error(msg)

def exception(ex):
    logger.exception(ex)
