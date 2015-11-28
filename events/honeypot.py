"""
    events/honeypot

    Manager for honeypot type events
"""
import logging
import digitalocean.pywrapper as dopy
import pika
import json

LOGGER = logging.getLogger()

# Load settings
SCRIPT_OPTIONS = json.loads(open('settings.json').read())

class HoneypotManager(object):
    """
        Manager for honeypot type events.
    """
    def __init__(self):
        super(HoneypotManager, self).__init__()

    def manage(self, event):
        """
            Manage honeypot_create events
        """
        LOGGER.debug('Managing honeypot_create event: %s' % event)

        # Event fields validation
        if 'honeys' not in event.keys() or not isinstance(event['honeys'], list) or \
            len(event['honeys']) == 0:
            LOGGER.error('No honeypots provided or empty list received')
            return
        if not event['hostname']:
            LOGGER.error('No hostname provided')
            return
        if not event['location']:
            LOGGER.error('No location provided')
            return
        if not event['sshkey']:
            LOGGER.error('No public SSH key provided')
            return

        # Snapshot retrieval
        snapshot = dopy.retrieve_image_by_name('smarthive-snapshot', private=True)
        if snapshot is None:
            LOGGER.error('Base snapshot not found')
            return

        # Commands execution during deployment
        # - Run logstash and configure it to start automatically
        # - Run selected honeypots and configure them to start automatically
        user_data = [
            "#!/bin/bash",
            "service logstash start",
            "update-rc.d -f logstash defaults"
        ]
        for honeypot in event['honeys']:
            user_data.append('service %s start' % honeypot)
            user_data.append('update-rc.d -f %s defaults' % honeypot)

        # Public SSH key upload
        ssh_params = {
            'name'          : '%s SSH key' % event['hostname'],
            'public_key'    : event['sshkey']
        }
        key = dopy.create_ssh_key(ssh_params)

        # Honeypot machine deployment
        droplet_params = {
            'name'      : event['hostname'],
            'region'    : event['location'],
            'size'      : '1gb',
            'image'     : snapshot['id'],
            'ssh_keys'  : [key['ssh_key']['id']],
            "user_data" : '\n'.join(user_data)
        }
        droplet = dopy.create_droplet(droplet_params)

        # Send honeypot_ready event
        self.send_event(droplet['droplet'])

    def send_event(self, droplet):
        """
            Manage honeypot_ready events
        """
        # Initialize AMQP connection
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=SCRIPT_OPTIONS['broker']['host'])
        )
        channel = connection.channel()

        # Declare exchange and exchange_type (defaults to smarthive, direct)
        channel.exchange_declare(exchange=SCRIPT_OPTIONS['broker']['exchange'],
            type=SCRIPT_OPTIONS['broker']['exchange_type'])

        # Data to send
        data = {
            'event_type'    : 'honeypot_ready',
            'event_payload' : {
                'hostname'  : droplet['name'],
                'ip'        : droplet['networks']['v4'][0]['ip_address']
            }
        }
        event = json.dumps(data)

        # Send event
        LOGGER.debug('Sending honeypot_ready event: %s' % event)
        channel.basic_publish(exchange=SCRIPT_OPTIONS['broker']['exchange'],
            routing_key='web',
            body=event)

        connection.close()
