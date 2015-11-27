#!/usr/bin/env python
"""
    Main application script.

    Executes without arguments (settings on settings.json)
"""
import json
import pika
import events
import logging

SCRIPT_OPTIONS = json.loads(open('settings.json').read())

# Setup logging
LOGGER = logging.getLogger()
LOGGER.setLevel(int(SCRIPT_OPTIONS['loglevel']))
HANDLER = logging.FileHandler(SCRIPT_OPTIONS['logfile'])
HANDLER.setFormatter(logging.Formatter(SCRIPT_OPTIONS['logformat']))
LOGGER.addHandler(HANDLER)


# Initialize AMQP connection
CONNECTION = pika.BlockingConnection(
    pika.ConnectionParameters(host=SCRIPT_OPTIONS['broker']['host'])
)
CHANNEL = CONNECTION.channel()

# Declare exchange and exchange_type (defaults to smarthive, direct)
CHANNEL.exchange_declare(exchange=SCRIPT_OPTIONS['broker']['exchange'],
                         type=SCRIPT_OPTIONS['broker']['exchange_type'])


# Create an exclusive queue for this script
QUEUE = CHANNEL.queue_declare(exclusive=True)
QUEUE_NAME = QUEUE.method.queue

# And subscribe for different events
for subscription in SCRIPT_OPTIONS['subscriptions']:
    CHANNEL.queue_bind(exchange=SCRIPT_OPTIONS['broker']['exchange'],
                       queue=QUEUE_NAME,
                       routing_key=subscription)


# Start listening
DISPATCHER = events.Dispatcher()
LOGGER.info('Start listening...')
CHANNEL.basic_consume(DISPATCHER.dispatch,
                      queue=QUEUE_NAME,
                      no_ack=True)

CHANNEL.start_consuming()
