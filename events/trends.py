"""
    events/trends

    Manager for trends type events
"""
import logging
import re
import json
import pygeoip
import pika
import threading
from multiprocessing import Pool
from time import sleep
#from main import CHANNEL

LOGGER = logging.getLogger()

class TrendsManager(object):
    """
        Manager for trends type events.
    """
    def __init__(self):
        super(TrendsManager, self).__init__()
        self.trends_event_payload = []
	self.countries = {}
        self.countries_short = self.getCountries('./conversion_paises')
	self.lock = threading.Lock()
	threading.Timer(10.0, self.send_data).start()
	
        #pool = Pool(processes=1)
        #pool.apply_async(self.notify_loop, [self.trends_event_payload])

    def send_data(self):
	self.lock.acquire()
	try:
		attack_event = []
		SCRIPT_OPTIONS = json.loads(open('settings.json').read())
		CONNECTION = pika.BlockingConnection(
		    pika.ConnectionParameters(host=SCRIPT_OPTIONS['broker']['host'])
		)
		CHANNEL = CONNECTION.channel()
                
		for country in self.countries.keys():
			attack_event.append([country, self.countries[country]])
		if len(attack_event) > 0:
			CHANNEL.basic_publish(exchange='smarthive', routing_key='web', body=json.dumps({'event_type':'trend_attack', 'event_payload': attack_event}))
			LOGGER.debug('Envio')
			LOGGER.debug(str(self.countries))
	finally:
		t=threading.Timer(10.0, self.send_data)
		self.countries = {}
		t.daemon = True
		t.start()
		self.lock.release()

    def notify_loop(self, event_payload):
        """
            Infinite loop. Notifies every minute using event_payload.
        """
        while True:
            sleep(60)
            LOGGER.debug(str(event_payload))
            event_payload = []

    def manage(self, event):
        """
            Manage trends event:

            1- transform event into this structure:
                {country: countrycode, port: port, num_events: number of times seen countrycode}
            2- update "self.trends_event_payload"

        """
        LOGGER.info('Managing event: %s' % event)
        # column1 -> time
        # column2 -> date
        # column3 -> ip
        # column4 -> port
        curated_event_info = {}
	country_short = self.get_country_code(event['column3'])
        curated_event_info['country'] = country_short #self.get_country_code(event['column3'])
	curated_event_info['port'] = event['column4']
	self.lock.acquire()
	try:
		LOGGER.debug(str(country_short))
		if country_short != '':
			if country_short in self.countries:
				self.countries[country_short] += 1
			else:
				self.countries[country_short] = 1
	finally:
		LOGGER.debug('recepcion')
		LOGGER.debug(str(self.countries))
		self.lock.release()

    def is_valid_ip(self, ip):
        r = '^(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))\.(\d|[1-9]\d|1\d\d|2([0-4]\d|5[0-5]))$'
        ips = re.findall(r, ip)
        if len(ips) > 0:
                return True
        return False

    def getCountries(self, fich):
        data = {}
        with open(fich) as d_file:
                data = json.load(d_file)
        return data

    def get_country_code(self, ip):
        if not self.is_valid_ip(ip):
                return ''
        gi4 = pygeoip.GeoIP('/usr/local/share/geoip/GeoIP.dat', pygeoip.MEMORY_CACHE)
        ip = ip
        code = gi4.country_code_by_addr(ip)
        name = gi4.country_name_by_addr(ip)
        paises = self.countries_short

        res = ''
        if code in paises.keys():
                res = paises[code]

        return res

