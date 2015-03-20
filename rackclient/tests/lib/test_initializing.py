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

from mock import *
from rackclient import exceptions
from rackclient.tests import utils
from rackclient.lib import initializing


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.WARN)


class InitializingTest(utils.TestCase):

    def setUp(self):
        super(InitializingTest, self).setUp()
        p = patch("requests.get")
        self.addCleanup(p.stop)
        mock_request = p.start()
        mock_resp = Mock()
        mock_resp.text= json.dumps(dict(meta=dict(
            proxy_ip="10.0.0.2",gid="gid", pid="pid", ppid="ppid")))
        mock_request.return_value = mock_resp

    def test_get_rack_context(self):
        p = patch("rackclient.lib.initializing.Client")
        self.addCleanup(p.stop)
        mock_client = p.start()
        mock_client = mock_client.return_value

        def proxy_info(args):
            info = type('', (object,), {})
            info.ipc_endpoint = None
            info.fs_endpoint = None
            info.shm_endpoint = None
            return info

        mock_client.proxy = Mock()
        mock_client_processes = Mock()
        mock_client.proxy.get.side_effect = proxy_info
        p2 = patch("rackclient.lib.initializing._Messaging")
        self.addCleanup(p2.stop)
        mock_messaging = p2.start()
        mock_messaging = mock_messaging.return_value
        mock_messaging.receive_msg.return_value=dict(pid="ppid")
        actual_context = initializing.get_rack_context()

        expect_context = type('', (object,), dict(
            proxy_ip="10.0.0.2",
            gid="gid", pid="pid",
            ppid="ppid",
            ipc_endpoint=None,
            fs_endpoint=None,
            shm_endpoint=None,
            client=mock_client))

        self.assertEquals(expect_context.pid, actual_context.pid)
        self.assertEquals(expect_context.ppid, actual_context.ppid)
        self.assertEquals(expect_context.proxy_ip, actual_context.proxy_ip)
        self.assertEquals(expect_context.ipc_endpoint, actual_context.ipc_endpoint)
        self.assertEquals(expect_context.fs_endpoint, actual_context.fs_endpoint)
        self.assertEquals(expect_context.shm_endpoint, actual_context.shm_endpoint)

    def test_get_rack_cotext_ProcessInitError_due_to_proxy(self):
        self.p = patch("rackclient.lib.initializing.Client")
        self.addCleanup(self.p.stop)
        mock_client = self.p.start()
        mock_client = mock_client.return_value
        mock_client.proxy = Mock()
        mock_client_processes = Mock()
        mock_client.proxy.get.side_effect = Exception()
        self.assertRaises(Exception, initializing.get_rack_context)

    def test_get_rack_cotext_ProcessInitError_doe_to_processes(self):
        self.p = patch("rackclient.lib.initializing.Client")
        self.addCleanup(self.p.stop)
        mock_client = self.p.start()
        mock_client = mock_client.return_value
        mock_client.proxy = Mock()
        mock_client_processes = Mock()
        mock_client.processes.get.side_effect = exceptions.NotFound("")
        self.assertRaises(Exception, initializing.get_rack_context)

    @patch("rackclient.lib.initializing._Messaging.Receive")
    def test_messaging_receive_msg(self, mock_receive):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.patch_pika_blocking = patch('pika.BlockingConnection', autospec=True)
        self.addCleanup(self.patch_pika_blocking.stop)
        self.mock_pika_blocking = self.patch_pika_blocking.start()
        self.mock_pika_blocking.return_value = self.mock_connection
        self.mock_connection.channel.return_value = self.mock_channel

        context = type('', (object,), dict(
            proxy_ip="10.0.0.2",
            gid="gid", pid="pid",
            ppid="ppid",
            ipc_endpoint=None,
            fs_endpoint=None,
            shm_endpoint=None))

        timeout_limit = 123
        msg = initializing._Messaging(context)
        message = msg.receive_msg(timeout_limit=timeout_limit)

        self.mock_connection.add_timeout.\
            assert_called_with(deadline=int(timeout_limit),
                               callback_method=mock_receive().time_out)
        self.mock_channel.\
            basic_consume.assert_called_with(mock_receive().get_msg,
                                             queue="pid",
                                             no_ack=False)
        self.mock_channel.start_consuming.assert_called_with()
        self.assertEqual(message, mock_receive().message)


    def test_messaging_send_msg(self):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.patch_pika_blocking = patch('pika.BlockingConnection', autospec=True)
        self.addCleanup(self.patch_pika_blocking.stop)
        self.mock_pika_blocking = self.patch_pika_blocking.start()
        self.mock_pika_blocking.return_value = self.mock_connection
        self.mock_connection.channel.return_value = self.mock_channel

        context = type('', (object,), dict(
            proxy_ip="10.0.0.2",
            gid="gid", pid="pid",
            ppid="ppid",
            ipc_endpoint=None,
            fs_endpoint=None,
            shm_endpoint=None))

        send_msg = 'test_msg'
        target = 'test_pid'
        msg = initializing._Messaging(context)
        msg.send_msg(target)
        routing_key = context.gid + '.' + target
        send_dict = {'pid': context.pid}
        send_msg = cPickle.dumps(send_dict)
        self.mock_channel.\
            basic_publish.assert_called_with(exchange=context.gid,
                                             routing_key=routing_key,
                                             body=send_msg)

    def test_receive_get_msg(self):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.patch_pika_blocking = patch('pika.BlockingConnection', autospec=True)
        self.addCleanup(self.patch_pika_blocking.stop)
        self.mock_pika_blocking = self.patch_pika_blocking.start()
        self.mock_pika_blocking.return_value = self.mock_connection
        self.mock_connection.channel.return_value = self.mock_channel

        ch = Mock()
        method = Mock()
        properties = Mock()
        receive_msg = 'receive_msg'
        body = cPickle.dumps(receive_msg)
        ch_object = {'delivery_tag': 'delivery_tag'}
        method.configure_mock(**ch_object)

        context = type('', (object,), dict(
            proxy_ip="10.0.0.2",
            gid="gid", pid="pid",
            ppid="ppid",
            ipc_endpoint=None,
            fs_endpoint=None,
            shm_endpoint=None))

        msg = initializing._Messaging(context)
        receive = msg.Receive()
        receive.get_msg(ch, method, properties, body)

        ch.basic_ack.assert_called_with(delivery_tag=ch_object['delivery_tag'])
        ch.stop_consuming.assert_call_with()
        self.assertEqual(receive.message, receive_msg)

    def test_receive_timeout(self):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.patch_pika_blocking = patch('pika.BlockingConnection', autospec=True)
        self.addCleanup(self.patch_pika_blocking.stop)
        self.mock_pika_blocking = self.patch_pika_blocking.start()
        self.mock_pika_blocking.return_value = self.mock_connection
        self.mock_connection.channel.return_value = self.mock_channel

        context = type('', (object,), dict(
            proxy_ip="10.0.0.2",
            gid="gid", pid="pid",
            ppid="ppid",
            ipc_endpoint="data",
            fs_endpoint=None,
            shm_endpoint=None))

        msg = initializing._Messaging(context)
        receive = msg.Receive()
        receive.channel = self.mock_channel
        receive.time_out()
        self.mock_channel.stop_consuming.assert_called_with()
