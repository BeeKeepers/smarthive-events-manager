"""
    events/__init__.py

    Declare main event dispatcher
"""
import logging
import json
import traceback

from events.attack import AttackManager
from events.trends import TrendsManager

LOGGER = logging.getLogger()

class Dispatcher(object):
    """docstring for Dispatcher"""
    def __init__(self):
        super(Dispatcher, self).__init__()

    def dispatch(self, channel, method, properties, body):
        """
            Send event to appropiate manager, depending on
            event_type
        """
        LOGGER.debug('Received event with body %s' % body)

        try:
            msg = json.loads(body)
        except Exception as e:
            LOGGER.warning('Wrong message format')
            return

        if ('event_type' not in msg):
            LOGGER.warning('Message has not event_type')
            return

        ## Dispatch
        trends_manager = TrendsManager()
        try:
            if msg['event_type'] == 'event_logentry': # trends log
                trends_manager.manage(msg)
            else:
                LOGGER.warning('No manager for %s event type' % msg['event_type'])
        except:
            LOGGER.error(traceback.format_exc())
            return
