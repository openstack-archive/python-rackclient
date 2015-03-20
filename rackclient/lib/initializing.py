# Copyright (c) 2014 ITOCHU Techno-Solutions Corporation.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import cPickle
import json
import logging
import pika
import requests

from rackclient import exceptions
from rackclient.client import Client


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

META_URL = 'http://169.254.169.254/openstack/latest/meta_data.json'


def get_rack_context(proxy_port=8088, client_version="1", api_version="v1"):

    try:
        resp = requests.get(META_URL)
        metadata = json.loads(resp.text)["meta"]
        proxy_url = 'http://%s:%d/%s' % (
            metadata["proxy_ip"], proxy_port, api_version)
        client = Client(client_version, rack_url=proxy_url)
        proxy_info = client.proxy.get(metadata["gid"])

        rack_ctx = type('', (object,), metadata)
        rack_ctx.ppid = getattr(rack_ctx, "ppid", "")
        rack_ctx.client = client
        rack_ctx.fs_endpoint = proxy_info.fs_endpoint
        rack_ctx.ipc_endpoint = proxy_info.ipc_endpoint
        rack_ctx.shm_endpoint = proxy_info.shm_endpoint

        try:
            # Check if this process is not recognized by RACK.
            rack_ctx.client.processes.get(rack_ctx.gid, rack_ctx.pid)
        except exceptions.NotFound:
            msg = "This process is not recognized by RACK"
            raise exceptions.InvalidProcessError(msg)

        if rack_ctx.ppid:
            LOG.debug("Messaging: send message to %s", rack_ctx.ppid)
            msg = _Messaging(rack_ctx)
            msg.send_msg(rack_ctx.ppid)
            while True:
                receive_msg = msg.receive_msg(
                    getattr(rack_ctx, "msg_limit_time", 180))
                if receive_msg and rack_ctx.ppid == receive_msg.get("pid"):
                    LOG.debug(
                        "Messaging: receive message from %s",
                        receive_msg.get("pid"))
                    break

    except Exception as e:
        msg = "Failed to initialize the process: %s." % e.message
        raise exceptions.ProcessInitError(msg)

    return rack_ctx


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
        self.channel.queue_bind(
            exchange=ctx.gid,
            queue=ctx.pid,
            routing_key=ctx.gid + '.' + ctx.pid)

    def receive_msg(self, timeout_limit=180):
        queue_name = self.ctx.pid
        self.channel = self.connection.channel()
        receive = self.Receive()
        self.connection.add_timeout(
            deadline=int(timeout_limit),
            callback_method=receive.time_out)
        self.channel.basic_consume(
            receive.get_msg,
            queue=queue_name,
            no_ack=False)
        receive.channel = self.channel
        self.channel.start_consuming()
        return receive.message

    def send_msg(self, target):
        routing_key = self.ctx.gid + '.' + target
        send_dict = {'pid': self.ctx.pid}
        send_msg = cPickle.dumps(send_dict)
        self.channel.basic_publish(
            exchange=self.ctx.gid,
            routing_key=routing_key,
            body=send_msg)

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
