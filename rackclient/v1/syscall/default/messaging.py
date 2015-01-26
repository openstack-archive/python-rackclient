import cPickle
import logging
import pika
from rackclient import exceptions
from rackclient import process_context

LOG = logging.getLogger(__name__)
PCTXT = process_context.PCTXT


class Messaging(object):
    def __init__(self):
        self.connection = _create_connection()
        self.channel = self.connection.channel()
        self.declare_queue(PCTXT.pid)

    def declare_queue(self, queue_name):
        queue_name = str(queue_name)
        self.channel.exchange_declare(exchange=PCTXT.gid, type='topic')
        self.channel.queue_declare(queue=queue_name)
        self.channel.queue_bind(exchange=PCTXT.gid,
                                queue=queue_name,
                                routing_key=PCTXT.gid + '.' + queue_name)

    def receive_all_msg(self, queue_name=None,
                        timeout_limit=180, msg_limit_count=None):
        if not queue_name:
            queue_name = PCTXT.pid

        self.channel = self.connection.channel()
        receive = self.Receive()
        timeout_limit = int(timeout_limit)
        self.connection.add_timeout(deadline=timeout_limit,
                                    callback_method=receive.time_out)
        self.channel.basic_consume(receive.get_all_msg,
                                   queue=queue_name,
                                   no_ack=False)
        receive.channel = self.channel
        receive.msg_count_limit = msg_limit_count
        self.channel.start_consuming()
        return receive.message_list

    def receive_msg(self, queue_name=None, timeout_limit=180):
        if not queue_name:
            queue_name = PCTXT.pid
        self.channel = self.connection.channel()
        receive = self.Receive()
        timeout_limit = int(timeout_limit)
        self.connection.add_timeout(deadline=timeout_limit,
                                    callback_method=receive.time_out)
        self.channel.basic_consume(receive.get_msg,
                                   queue=queue_name,
                                   no_ack=False)
        receive.channel = self.channel
        self.channel.start_consuming()
        return receive.message

    class Receive(object):
        def __init__(self):
            self.channel = None
            self.message = None
            self.message_list = []
            self.msg_count_limit = None

        def get_all_msg(self, ch, method, properties, body):
            ch.basic_ack(delivery_tag=method.delivery_tag)
            self.message_list.append(cPickle.loads(body))
            msg_count = len(self.message_list)
            LOG.debug("Received message count. %s", msg_count)
            if self.msg_count_limit and self.msg_count_limit <= msg_count:
                ch.stop_consuming()

        def get_msg(self, ch, method, properties, body):
            self.message = cPickle.loads(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()

        def time_out(self):
            self.channel.stop_consuming()

    def send_msg(self, target, message=None):
        routing_key = PCTXT.gid + '.' + target
        send_dict = {'pid': PCTXT.pid}
        if message:
            send_dict['message'] = message
        send_msg = cPickle.dumps(send_dict)
        self.channel.basic_publish(exchange=PCTXT.gid,
                                   routing_key=routing_key,
                                   body=send_msg)


def _create_connection():
    if PCTXT.ipc_endpoint:
        connection_param = pika.ConnectionParameters(PCTXT.ipc_endpoint)
    else:
        connection_param = pika.ConnectionParameters(PCTXT.proxy_ip)
    try:
        connection = pika.BlockingConnection(connection_param)
    except pika.exceptions.AMQPConnectionError as e:
        raise exceptions.AMQPConnectionError(e)
    return connection


def init():
    msg = Messaging()
    if PCTXT.ppid:
        LOG.debug("Messaging: send message to %s", PCTXT.ppid)
        msg.send_msg(PCTXT.ppid)
        while True:
            receive_msg = msg.receive_msg()
            if receive_msg and PCTXT.ppid == receive_msg.get("pid"):
                LOG.debug("Messaging: receive message from %s",
                          receive_msg.get("pid"))
                break