#!/usr/bin/env python

"""
    digitalocean/pywrapper.py
    DigitalOcean API Python wrapper
"""
import requests
import json
import os
import time
import logging
import sys

LOGGER = logging.getLogger()

# Load settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAR_DIR = os.path.join(BASE_DIR, os.pardir)
SETTINGS_FILE = os.path.join(PAR_DIR, 'settings.json')
SCRIPT_OPTIONS = json.loads(open(SETTINGS_FILE).read())

# DigitalOcean parameters
ENDPOINT = 'https://api.digitalocean.com/v2'

if 'digitalocean' in SCRIPT_OPTIONS.keys() and \
    'token' in SCRIPT_OPTIONS['digitalocean'].keys():
    TOKEN = SCRIPT_OPTIONS['digitalocean']['token']
else:
    LOGGER.error('No DigitalOcean token provided')
    sys.exit(1)

HEADERS = {
    'Authorization' : 'Bearer %s' % TOKEN,
    'Content-Type'  : 'application/json'
}

# DigitalOcean functions
def print_droplet(droplet):
    if 'droplet' in droplet.keys():
        droplet = droplet['droplet']
    msg_format = '[%s] name: %s, created_at: %s, region_name: %s, status: %s'
    LOGGER.info(msg_format % (
        droplet['id'],
        droplet['name'],
        droplet['created_at'],
        droplet['region']['name'],
        droplet['status']
    ))

def print_droplets(droplets):
    for d in droplets['droplets']:
        print_droplet(d)

def print_droplet_v4_networks(droplet):
    if 'droplet' in droplet.keys():
        droplet = droplet['droplet']
    msg_format = 'type: %s, ip_address: %s, netmask: %s, gateway: %s'
    for n in droplet['networks']['v4']:
        LOGGER.info(msg_format % (
            n['type'],
            n['ip_address'],
            n['netmask'],
            n['gateway']
        ))

def print_image(image):
    msg_format = '[%s] type: %s, distribution: %s, name: %s, slug: %s, created_at: %s'
    LOGGER.info(msg_format % (
        image['id'],
        image['type'],
        image['distribution'],
        image['name'],
        image['slug'],
        image['created_at']
    ))

def print_images(images):
    for i in images['images']:
        print_image(i)

def print_ssh_key(key):
    if 'ssh_key' in key.keys():
        key = key['ssh_key']
    msg_format = '[%s] name: %s, fingerprint: %s'
    LOGGER.info(msg_format % (
        key['id'],
        key['name'],
        key['fingerprint']
    ))

def print_ssh_keys(keys):
    for k in keys['ssh_keys']:
        print_ssh_key(k)

def list_actions():
    r = requests.get('%s/actions' % ENDPOINT, headers=HEADERS)
    return r.json()

def list_droplets():
    r = requests.get('%s/droplets' % ENDPOINT, headers=HEADERS)
    return r.json()

def list_images(private=False):
    url = '%s/images' % ENDPOINT
    if private:
        url += '?private=true'
    r = requests.get(url, headers=HEADERS)
    return r.json()

def list_regions():
    r = requests.get('%s/regions' % ENDPOINT, headers=HEADERS)
    return r.json()

def list_ssh_keys():
    r = requests.get('%s/account/keys' % ENDPOINT, headers=HEADERS)
    return r.json()

def retrieve_droplet(droplet_id):
    r = requests.get('%s/droplets/%s' % (ENDPOINT, droplet_id), headers=HEADERS)
    return r.json()

def is_active(droplet):
    return droplet['droplet']['status'] == 'active'

def is_completed(action):
    return action['action']['status'] == 'completed'

def create_droplet(params):
    r = requests.post('%s/droplets' % ENDPOINT, data=json.dumps(params), headers=HEADERS)
    droplet = r.json()
    droplet_id = droplet['droplet']['id']
    while not is_active(droplet):
        LOGGER.debug('Creating droplet...')
        time.sleep(5)
        droplet = retrieve_droplet(droplet_id)
    LOGGER.debug('Droplet %s ready' % droplet_id)
    return droplet

def execute_droplet_action(droplet_id, params):
    r = requests.post('%s/droplets/%s/actions' % (ENDPOINT, droplet_id), data=json.dumps(params), headers=HEADERS)
    return r.json()

def retrieve_droplet_action(droplet_id, action_id):
    r = requests.get('%s/droplets/%s/actions/%s' % (ENDPOINT, droplet_id, action_id), headers=HEADERS)
    return r.json()

def shutdown_droplet(droplet_id):
    params = {'type': 'shutdown'}
    action = execute_droplet_action(droplet_id, params)
    action_id = action['action']['id']
    while not is_completed(action):
        LOGGER.debug('Shutting down droplet...')
        time.sleep(5)
        action = retrieve_droplet_action(droplet_id, action_id)
    LOGGER.debug('Shutdown complete')

def poweron_droplet(droplet_id):
    params = {'type': 'power_on'}
    action = execute_droplet_action(droplet_id, params)
    action_id = action['action']['id']
    while not is_completed(action):
        LOGGER.debug('Powering on droplet...')
        time.sleep(5)
        action = retrieve_droplet_action(droplet_id, action_id)
    LOGGER.debug('Power on complete')

def reboot_droplet(droplet_id):
    params = {'type': 'reboot'}
    action = execute_droplet_action(droplet_id, params)
    action_id = action['action']['id']
    while not is_completed(action):
        LOGGER.debug('Rebooting droplet...')
        time.sleep(5)
        action = retrieve_droplet_action(droplet_id, action_id)
    LOGGER.debug('Reboot complete')

def destroy_droplet(droplet_id):
    r = requests.delete('%s/droplets/%s' % (ENDPOINT, droplet_id), headers=HEADERS)
    if r.status_code != 204:
        raise Exception('Failed to destroy droplet')

def snapshot_droplet(droplet_id, snapshot_name):
    params = {
        'type'  : 'snapshot',
        'name'  : snapshot_name
    }
    action = execute_droplet_action(droplet_id, params)
    action_id = action['action']['id']
    while not is_completed(action):
        LOGGER.debug('Taking snapshot...')
        time.sleep(5)
        action = retrieve_droplet_action(droplet_id, action_id)
    LOGGER.debug('Snapshot complete')

def retrieve_image_by_name(name, private=False):
    images = list_images(private)
    for i in images['images']:
        if i['name'] == name:
            return i
    return None

def create_ssh_key(params):
    r = requests.post('%s/account/keys' % ENDPOINT, data=json.dumps(params), headers=HEADERS)
    return r.json()

def retrieve_ssh_key(key_id):
    r = requests.get('%s/account/keys/%s' % (ENDPOINT, key_id), headers=HEADERS)
    return r.json()
