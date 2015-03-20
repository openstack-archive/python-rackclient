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
import logging

from mock import patch, Mock
from rackclient.tests import utils
from rackclient.lib.syscall.default import signal


class SignalTest(utils.LibTestCase):

    def target_context(self):
        return "syscall.default.signal"

    def setUp(self):
        super(SignalTest, self).setUp()
        logging.basicConfig(level=logging.ERROR)

    @patch('websocket.WebSocketApp')
    def test_receive(self, mock_websocket_websocketapp):
        mock_app = Mock()
        mock_websocket_websocketapp.return_value = mock_app

        s = signal.SignalManager()
        on_msg_func = 'on_msg_func'
        excepted_on_msg_func = copy.deepcopy(on_msg_func)
        s.receive(on_msg_func)

        mock_websocket_websocketapp.\
            assert_called_with(url=s.url + '/receive',
                               header=['PID: ' + self.mock_RACK_CTX.pid],
                               on_message=s.on_message,
                               on_error=s.on_error,
                               on_close=s.on_close)
        mock_app.run_forever.assert_called_with()
        self.assertEqual(s.on_msg_func, excepted_on_msg_func)

    @patch('websocket.WebSocketApp')
    def test_receive_pid_specified(self, mock_websocket_websocketapp):
        mock_app = Mock()
        mock_websocket_websocketapp.return_value = mock_app

        url = '/test_url/'
        expected_url = url.rstrip('/')
        s = signal.SignalManager(url=url)
        on_msg_func = 'on_msg_func'
        excepted_on_msg_func = copy.deepcopy(on_msg_func)
        pid = 'singnal_pid'
        s.receive(on_msg_func, pid=pid)

        self.assertEqual(s.url, expected_url)
        mock_websocket_websocketapp.assert_called_with(url=s.url + '/receive',
                                                       header=['PID: ' + pid],
                                                       on_message=s.on_message,
                                                       on_error=s.on_error,
                                                       on_close=s.on_close)
        mock_app.run_forever.assert_called_with()
        self.assertEqual(s.on_msg_func, excepted_on_msg_func)

    @patch('websocket.WebSocketApp')
    def teston_msg_func_receive_pid_specified(self, mock_websocket_websocketapp):
        mock_app = Mock()
        mock_websocket_websocketapp.return_value = mock_app

        s = signal.SignalManager()
        on_msg_func = 'on_msg_func'
        self.mock_RACK_CTX.pid = None
        self.assertRaises(Exception, s.receive, on_msg_func)

    def test_on_message(self):
        on_msg_func = Mock()
        ws = Mock()
        s = signal.SignalManager()
        s.on_msg_func = on_msg_func
        message = 'test_msg'
        excepted_message = copy.deepcopy(message)
        s.on_message(ws, message)

        on_msg_func.assert_called_with(excepted_message)
        ws.close.assert_called_with()

    def test_on_error(self):
        ws = Mock()
        s = signal.SignalManager()
        error = 'test_error'

        self.assertRaises(Exception, s.on_error, ws, error)
        ws.close.assert_called_with()

    @patch('websocket.create_connection')
    def test_send(self, mock_create_connection):
        target_id = 'target_id'
        expected_target_id = copy.deepcopy(target_id)
        message = 'test_msg'
        expected_message = copy.deepcopy(message)
        url = '/test_url/'
        expected_url = url.rstrip('/') + '/send'
        ws = Mock()
        mock_create_connection.return_value = ws

        s = signal.SignalManager(url=url)
        s.send(target_id, message)

        mock_create_connection.\
            assert_called_with(expected_url,
                               header=['PID: ' + expected_target_id])
        ws.send.assert_called_with(expected_message)
        ws.close.assert_called_with()