import logging

logger = logging.getLogger()

class Dispatcher(object):
    """docstring for Dispatcher"""
    def __init__(self):
        super(Dispatcher, self).__init__()

    def dispatch(ch, method, properties, body):
        logger.info('Event received!')
