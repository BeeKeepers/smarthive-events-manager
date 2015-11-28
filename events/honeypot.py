"""
    events/honeypot

    Manager for honeypot type events
"""
import logging
import digitalocean.pywrapper as dopy

LOGGER = logging.getLogger()

class HoneypotManager(object):
    """
        Manager for honeypot type events.
    """
    def __init__(self):
        super(HoneypotManager, self).__init__()

    def manage(self, event):
        """
            Manage honeypot events
        """
        LOGGER.debug('Managing event: %s' % event)

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
        snapshot = dopy.retrieve_image_by_name('BaseH1-Snapshot', private=True)
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
