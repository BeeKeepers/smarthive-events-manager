"""
    events/trends

    Manager for trends type events
"""
import logging
from multiprocessing import Pool
from time import sleep

LOGGER = logging.getLogger()

class TrendsManager(object):
    """
        Manager for trends type events.
    """
    def __init__(self):
        super(TrendsManager, self).__init__()
        self.trends_event_payload = []
        pool = Pool(processes=1)
        pool.apply_async(self.notify_loop, [self.trends_event_payload])

    def notify_loop(self, event_payload):
        """
            Infinite loop. Notifies every minute using event_payload.
        """
        while True:
            sleep(60)
            # TODO: send event
            print event_payload
            event_payload = []

    def manage(self, event):
        """
            Manage trends event:

            1- transform event into this structure:
                {country: countrycode, port: port}
            2- update "self.trends_event_payload"

        """
        LOGGER.info('Managing event: %s' % event)
        # column1 -> time
        # column2 -> date
        # column3 -> ip
        # column4 -> port
        curated_event_info = {}
        curated_event_info['country'] = self.get_country_code(event['column3'])




    def get_country_code(self, ip):
        LOGGER.debug('Getting country code from %s...' % ip)
        pass
