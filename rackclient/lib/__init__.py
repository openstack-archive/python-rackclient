from rackclient import exceptions
from rackclient.client import Client

import cPickle
import json
import logging
import os
import pika
import requests


LOG = logging.getLogger(__name__)

META_URL = 'http://169.254.169.254/openstack/latest/meta_data.json'
RACK_CTX = None


def get_rack_context(proxy_port=8088, client_version="1", api_version="v1"):
    global RACK_CTX

    if not RACK_CTX:
        try:
            resp = requests.get(META_URL)
            metadata = json.loads(resp.text)["meta"]
            proxy_url = 'http://%s:%d/%s' % (metadata["proxy_ip"], proxy_port, api_version)
            client = Client(client_version, rack_url=proxy_url)
            proxy_info = client.proxy.get(metadata["gid"])

            RACK_CTX = type('', (object,), metadata)
            RACK_CTX.ppid = getattr(RACK_CTX, "ppid", "")
            RACK_CTX.client = client
            RACK_CTX.fs_endpoint = proxy_info.fs_endpoint
            RACK_CTX.ipc_endpoint = proxy_info.ipc_endpoint
            RACK_CTX.shm_endpoint = proxy_info.shm_endpoint

            try:
                # Check if this process is not recognized by RACK.
                RACK_CTX.client.processes.get(RACK_CTX.gid, RACK_CTX.pid)
            except exceptions.NotFound:
                msg = "This process is not recognized by RACK"
                raise exceptions.InvalidProcessError(msg)

            if RACK_CTX.ppid:
                LOG.debug("Messaging: send message to %s", RACK_CTX.ppid)
                msg = _Messaging(RACK_CTX)
                msg.send_msg(RACK_CTX.ppid)
                while True:
                    receive_msg = msg.receive_msg(getattr(RACK_CTX, "msg_limit_time", 180))
                    if receive_msg and RACK_CTX.ppid == receive_msg.get("pid"):
                        LOG.debug("Messaging: receive message from %s", receive_msg.get("pid"))
                        break

        except Exception as e:
            msg = "Failed to initialize the process: %s." % e.message
            raise exceptions.ProcessInitError(msg)

    return RACK_CTX


class _Messaging(object):

    def __init__(self, ctx):
        self.ctx = ctx
        connection_param = pika.ConnectionParameters(self.ctx.proxy_ip)
        if self.ctx.ipc_endpoint:
            connection_param = pika.ConnectionParameters(self.ctx.ipc_endpoint)
        self.connection = pika.BlockingConnection(connection_param)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=ctx.gid, type='topic')
        self.channel.queue_declare(queue=ctx.pid)
        self.channel.queue_bind(exchange=ctx.gid, queue=ctx.pid, routing_key=ctx.gid + '.' + ctx.pid)


    def receive_msg(self, timeout_limit=180):
        queue_name = self.ctx.pid
        self.channel = self.connection.channel()
        receive = self.Receive()
        self.connection.add_timeout(deadline=int(timeout_limit), callback_method=receive.time_out)
        self.channel.basic_consume(receive.get_msg, queue=queue_name, no_ack=False)
        receive.channel = self.channel
        self.channel.start_consuming()
        return receive.message


    class Receive(object):

        def __init__(self):
            self.channel = None
            self.message = None

        def get_msg(self, ch, method, properties, body):
            self.message = cPickle.loads(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()

        def time_out(self):
            self.channel.stop_consuming()


    def send_msg(self, target):
        routing_key = self.ctx.gid + '.' + target
        send_dict = {'pid': self.ctx.pid}
        send_msg = cPickle.dumps(send_dict)
        self.channel.basic_publish(exchange=self.ctx.gid, routing_key=routing_key, body=send_msg)

if not os.environ.get("RACK_IS_TEST"):
    get_rack_context()
