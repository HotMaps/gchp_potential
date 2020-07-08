#!/usr/bin/env python
import pika

import socket
import requests
import logging
from app.constant import PORT,CM_ID,CELERY_BROKER_URL,RPC_Q,TRANFER_PROTOCOLE


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel("DEBUG")

queue_name =  RPC_Q + str(CM_ID)
parameters = pika.URLParameters(CELERY_BROKER_URL + "?heartbeat_interval=0")

try:
    connection = pika.BlockingConnection(parameters)
except Exception as exc:
    LOGGER.exception("Failed to pika.BlockConnection >> "
                     f"queue_name = {queue_name} >> "
                     f"broaker = {str(CELERY_BROKER_URL)} >> "
                     f"parameters = {parameters} >> "
                     f"exception = {exc}"
                     )
    raise exc
    
try:
    channel = connection.channel()
except Exception as exc:
    LOGGER.exception("Failed to acquire the channel >> "
                     f"queue_name = {queue_name} >> "
                     f"broaker = {str(CELERY_BROKER_URL)} >> "
                     f"parameters = {parameters} >> "
                     f"connection = {connection} >> "
                     f"exception = {exc}"
                     )
    raise exc

try:
    channel.queue_declare(queue=queue_name)
except Exception as exc:
    LOGGER.exception("Failed to declare queue >> "
                     f"queue_name = {queue_name} >> "
                     f"broaker = {str(CELERY_BROKER_URL)} >> "
                     f"parameters = {parameters} >> "
                     f"connection = {connection} >> "
                     f"exception = {exc}"
                     )
    raise exc



def on_request(ch, method, props, body):
    #body.status = 'up'

    LOGGER.info(f'body: {body}')

    headers = {'Content-Type':  'application/json'}
    ip = socket.gethostbyname(socket.gethostname())

    base_url = TRANFER_PROTOCOLE+ str(ip) +':'+str(PORT)+'/computation-module/compute/'
    LOGGER.info(f'base_url: {base_url}')
    res = requests.post(base_url, data = body, headers = headers)
    response = res.text
    LOGGER.info(f'onRequest response: {response}')
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))

    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)

LOGGER.info(" [x] Awaiting RPC requests")
channel.start_consuming()

