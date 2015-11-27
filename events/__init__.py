"""
    events/__init__.py

    Declare main event dispatcher
"""
import logging
import json
import traceback

from events.attack import AttackManager

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

        if ('event_type' not in msg) or ('event_payload' not in msg):
            LOGGER.warning('Message has not event_type or event_payload')
            return

        ## Dispatch
        try:
            if msg['event_type'] == 'event_logentry':
                AttackManager.manage(msg['event_payload'])
            else:
                LOGGER.warning('No manager for %s event type' % msg['event_type'])
        except:
            LOGGER.error(traceback.format_exc())
            return
