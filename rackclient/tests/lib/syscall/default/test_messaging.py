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
import copy
import cPickle

import pika

from mock import patch, Mock
from rackclient import exceptions
from rackclient.tests import utils
from rackclient.lib.syscall.default import messaging as rack_ipc


class MessagingTest(utils.LibTestCase):

    def target_context(self):
        return "syscall.default.messaging"

    def setUp(self):
        super(MessagingTest, self).setUp()
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_receive = Mock(spec=rack_ipc.Messaging.Receive)
        self.patch_pika_blocking = patch('pika.BlockingConnection', autospec=True)
        # self.addCleanup(self.patch_pika_blocking.stop)
        self.mock_pika_blocking = self.patch_pika_blocking.start()
        self.mock_pika_blocking.return_value = self.mock_connection
        self.mock_connection.channel.return_value = self.mock_channel

    def tearDown(self):
        super(MessagingTest, self).tearDown()
        self.patch_pika_blocking.stop()

    def test_declare_queue(self):
        queue_name = 'test_queue_name'
        msg = rack_ipc.Messaging()
        msg.declare_queue(queue_name)

        self.mock_channel.\
            exchange_declare.assert_called_with(exchange=self.mock_RACK_CTX.gid,
                                                type='topic')
        self.mock_channel.queue_declare.assert_called_with(queue=queue_name)
        r_key = self.mock_RACK_CTX.gid + '.' + queue_name
        self.mock_channel.queue_bind.assert_called_with(exchange=self.mock_RACK_CTX.gid,
                                                        queue=queue_name,
                                                        routing_key=r_key)

    @patch('rackclient.lib.syscall.default.messaging.Messaging.Receive')
    def test_receive_all_msg(self, mock_receive):
        timeout_limit = 123
        msg = rack_ipc.Messaging()
        msg_list = msg.receive_all_msg(timeout_limit=timeout_limit)

        self.mock_connection.add_timeout.\
            assert_called_with(deadline=timeout_limit,
                               callback_method=mock_receive().time_out)
        self.mock_channel.\
            basic_consume.assert_called_with(mock_receive().get_all_msg,
                                             queue=self.mock_RACK_CTX.pid,
                                             no_ack=False)
        self.mock_channel.start_consuming.assert_called_with()
        self.assertEqual(msg_list, mock_receive().message_list)

    @patch('rackclient.lib.syscall.default.messaging.Messaging.Receive')
    def test_receive_msg(self, mock_receive):
        timeout_limit = 123
        msg = rack_ipc.Messaging()
        message = msg.receive_msg(timeout_limit=timeout_limit)

        self.mock_connection.add_timeout.\
            assert_called_with(deadline=timeout_limit,
                               callback_method=mock_receive().time_out)
        self.mock_channel.\
            basic_consume.assert_called_with(mock_receive().get_msg,
                                             queue=self.mock_RACK_CTX.pid,
                                             no_ack=False)
        self.mock_channel.start_consuming.assert_called_with()
        self.assertEqual(message, mock_receive().message)

    def test_send_msg(self):
        send_msg = 'test_msg'
        target = 'test_pid'
        msg = rack_ipc.Messaging()
        msg.send_msg(target,
                     message=send_msg)
        routing_key = self.mock_RACK_CTX.gid + '.' + target
        send_dict = {'pid': self.mock_RACK_CTX.pid,
                     'message': send_msg}
        send_msg = cPickle.dumps(send_dict)
        self.mock_channel.\
            basic_publish.assert_called_with(exchange=self.mock_RACK_CTX.gid,
                                             routing_key=routing_key,
                                             body=send_msg)

    def test_send_msg_no_message(self):
        msg = rack_ipc.Messaging()
        target = 'test_pid'
        msg.send_msg(target)
        routing_key = self.mock_RACK_CTX.gid + '.' + target
        send_dict = {'pid': self.mock_RACK_CTX.pid}
        send_msg = cPickle.dumps(send_dict)

        self.mock_channel.\
            basic_publish.assert_called_with(exchange=self.mock_RACK_CTX.gid,
                                             routing_key=routing_key,
                                             body=send_msg)

    def test_receive_get_all_msg(self):
        ch = Mock()
        method = Mock()
        properties = Mock()
        receive_msg = 'receive_msg'
        body = cPickle.dumps(receive_msg)
        ch_object = {'delivery_tag': 'delivery_tag'}
        method.configure_mock(**ch_object)

        msg = rack_ipc.Messaging()
        receive = msg.Receive()
        receive.get_all_msg(ch, method, properties, body)

        ch.basic_ack.assert_called_with(delivery_tag=ch_object['delivery_tag'])
        self.assertEqual(receive.message_list[0], receive_msg)

    def test_receive_get_all_msg_count_limit(self):
        ch = Mock()
        method = Mock()
        properties = Mock()
        message_list = [{'pid': 'child_pid1'},
                        {'pid': 'child_pid2'}]
        expected_message_list = copy.deepcopy(message_list)
        receive_msg = {'pid': 'child_pid3'}
        expected_message_list.append(receive_msg)
        body = cPickle.dumps(receive_msg)
        ch_object = {'delivery_tag': 'delivery_tag'}
        method.configure_mock(**ch_object)
        msg = rack_ipc.Messaging()
        receive = msg.Receive()
        receive.message_list = message_list
        receive.msg_count_limit = 3

        receive.get_all_msg(ch, method, properties, body)

        ch.basic_ack.assert_called_with(delivery_tag=ch_object['delivery_tag'])
        ch.stop_consuming.assert_called_with()
        self.assertEqual(receive.message_list, expected_message_list)

    def test_receive_get_msg(self):
        ch = Mock()
        method = Mock()
        properties = Mock()
        receive_msg = 'receive_msg'
        body = cPickle.dumps(receive_msg)
        ch_object = {'delivery_tag': 'delivery_tag'}
        method.configure_mock(**ch_object)

        msg = rack_ipc.Messaging()
        receive = msg.Receive()
        receive.get_msg(ch, method, properties, body)

        ch.basic_ack.assert_called_with(delivery_tag=ch_object['delivery_tag'])
        ch.stop_consuming.assert_call_with()
        self.assertEqual(receive.message, receive_msg)

    def test_receive_timeout(self):
        msg = rack_ipc.Messaging()
        receive = msg.Receive()
        receive.channel = self.mock_channel
        receive.time_out()
        self.mock_channel.stop_consuming.assert_called_with()

    def test_create_connection(self):
        p = patch('pika.ConnectionParameters', autospec=True)
        self.addCleanup(p.stop)
        mock_pika_connection_param = p.start()
        rack_ipc.Messaging()
        mock_pika_connection_param.assert_called_with(self.mock_RACK_CTX.proxy_ip)

    @patch('pika.ConnectionParameters', autospec=True)
    def test_create_connection_ipc_endpoint(self, mock_pika_connection_param):
        ipc_ip = 'ipc_ip'
        self.mock_RACK_CTX.ipc_endpoint = ipc_ip
        rack_ipc.Messaging()
        mock_pika_connection_param.assert_called_with(ipc_ip)

    def test_create_connection_amqp_connection_error(self):
        self.mock_pika_blocking.side_effect = pika.\
            exceptions.AMQPConnectionError()
        self.assertRaises(exceptions.AMQPConnectionError, rack_ipc.Messaging)