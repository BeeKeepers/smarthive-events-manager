"""
    events/attack

    Manager for attack type events
"""
import logging

LOGGER = logging.getLogger()

class AttackManager(object):
    """
        Manager for attack type events.
    """
    def __init__(self):
        super(AttackManager, self).__init__()

    def manage(self, event):
        """
            Manage attack event
        """
        LOGGER.info('Managing event: %s' % event)
