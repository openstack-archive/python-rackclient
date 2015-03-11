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
from rackclient.tests import utils
from rackclient.v1 import processes
from rackclient.lib.syscall.default import messaging, file, syscall, pipe
from mock import call
from mock import Mock


class SyscallTest(utils.LibTestCase):

    def target_context(self):
        return "syscall.default.syscall"

    def setUp(self):
        super(SyscallTest, self).setUp()

    def test_fork(self):
        def create_process(gid, ppid, **kwargs):
            count = self.mock_RACK_CTX.client.processes.create.call_count
            d = {'ppid': ppid,
                 'pid': 'pid' + str(count),
                 'gid': gid,
                 'proxy_ip': self.mock_RACK_CTX.proxy_ip}
            args = kwargs['args']
            args.update(d)
            kwargs.update(d)
            return_process = processes.Process(self.mock_RACK_CTX.client, kwargs)
            return return_process

        self.mock_RACK_CTX.client.processes.create = Mock(side_effect=create_process)
        # messaging mock
        mock_messaging = Mock()
        messaging.Messaging = Mock(return_value=mock_messaging)
        msg_list = [{'pid': 'pid1'}, {'pid': 'pid2'}, {'pid': 'pid3'}]
        mock_messaging.receive_all_msg.return_value = msg_list
        # pip mock
        pipe.Pipe = Mock()

        # call fork
        arg1 = {'test': 'test1'}
        arg2 = {'test': 'test2'}
        arg3 = {'test': 'test3'}
        arg_list = [{'args': arg1},
                    {'args': arg2},
                    {'args': arg3}]
        process_list = syscall.fork(arg_list)

        # check
        expected_pipe_share = [call('pid', 'pid1'),
                               call('pid', 'pid2'),
                               call('pid', 'pid3')]
        self.assertEqual(expected_pipe_share, pipe.Pipe.share.call_args_list)
        expected_msg_send = [call(message='start', target='pid1'),
                             call(message='start', target='pid2'),
                             call(message='start', target='pid3')]
        self.assertEqual(expected_msg_send,
                         mock_messaging.send_msg.call_args_list)
        expected_arg_list = [arg1, arg2, arg3]
        for process in process_list:
            self.assertTrue(process.args in expected_arg_list)
            self.assertEqual(process.ppid, self.mock_RACK_CTX.pid)
            self.assertEqual(process.gid, self.mock_RACK_CTX.gid)
            expected_arg_list.remove(process.args)

    def test_bulk_fork_check_connection_recoverable_error(self):
        # setup
        def create_process(gid, ppid, **kwargs):
            count = self.mock_RACK_CTX.client.processes.create.call_count
            if count == 2:
                raise Exception()
            d = {'ppid': ppid,
                 'pid': 'pid' + str(count),
                 'gid': gid,
                 'proxy_ip': self.mock_RACK_CTX.proxy_ip}
            args = kwargs['args']
            args.update(d)
            kwargs.update(d)
            return_process = processes.Process(self.mock_RACK_CTX.client, kwargs)
            return return_process

        self.mock_RACK_CTX.client.processes.create = Mock(side_effect=create_process)
        self.mock_RACK_CTX.client.processes.delete = Mock()

        # messaging mock
        mock_messaging = Mock()
        messaging.Messaging = Mock(return_value=mock_messaging)
        msg_list = [{'pid': 'pid3'}, {'pid': 'pid4'}, {'pid': 'pid5'}]
        mock_messaging.receive_all_msg.return_value = msg_list

        # pip mock
        pipe.Pipe = Mock()

        # call fork
        arg1 = {'test': 'test1'}
        arg2 = {'test': 'test2'}
        arg3 = {'test': 'test3'}
        arg_list = [{'args': arg1},
                    {'args': arg2},
                    {'args': arg3}]
        process_list = syscall.fork(arg_list)

        # check
        self.mock_RACK_CTX.client.processes.delete.assert_called_with(self.mock_RACK_CTX.gid, 'pid1')
        expected_pipe_share = [call('pid', 'pid3'),
                               call('pid', 'pid4'),
                               call('pid', 'pid5')]
        self.assertEqual(expected_pipe_share, pipe.Pipe.share.call_args_list)
        expected_msg_send = [call(message='start', target='pid3'),
                             call(message='start', target='pid4'),
                             call(message='start', target='pid5')]
        self.assertEqual(expected_msg_send,
                         mock_messaging.send_msg.call_args_list)
        expected_arg_list = [arg1, arg2, arg3]
        for process in process_list:
            self.assertTrue(process.args in expected_arg_list)
            self.assertEqual(process.ppid, self.mock_RACK_CTX.pid)
            self.assertEqual(process.gid, self.mock_RACK_CTX.gid)
            expected_arg_list.remove(process.args)

    def test_bulk_fork_error_no_child_process_is_created(self):
        self.mock_RACK_CTX.client.processes.create = Mock(side_effect=Exception)
        # call fork
        arg1 = {'test': 'test1'}
        arg2 = {'test': 'test2'}
        arg3 = {'test': 'test3'}
        arg_list = [{'args': arg1},
                    {'args': arg2},
                    {'args': arg3}]
        self.assertRaises(Exception, syscall.fork, arg_list)

    def test_check_connection_error_no_child_process_is_active(self):
        # setup
        def create_process(gid, ppid, **kwargs):
            count = self.mock_RACK_CTX.client.processes.create.call_count
            d = {'ppid': ppid,
                 'pid': 'pid' + str(count),
                 'gid': gid,
                 'proxy_ip': self.mock_RACK_CTX.proxy_ip}
            args = kwargs['args']
            args.update(d)
            kwargs.update(d)
            return_process = processes.Process(self.mock_RACK_CTX.client, kwargs)
            return return_process

        self.mock_RACK_CTX.client.processes.create = Mock(side_effect=create_process)
        self.mock_RACK_CTX.client.processes.delete = Mock()
        # messaging mock
        mock_messaging = Mock()
        messaging.Messaging = Mock(return_value=mock_messaging)
        msg_list = [{'pid': 'pid6'}]
        mock_messaging.receive_all_msg.return_value = msg_list

        # call fork
        arg_list = [{'args': {'test': 'test1'}},
                    {'args': {'test': 'test2'}},
                    {'args': {'test': 'test3'}}]
        self.assertRaises(Exception, syscall.fork, arg_list)
        expected_processes_delete = [call(self.mock_RACK_CTX.gid, 'pid1'),
                                     call(self.mock_RACK_CTX.gid, 'pid2'),
                                     call(self.mock_RACK_CTX.gid, 'pid3')]
        self.assertEqual(expected_processes_delete,
                         self.mock_RACK_CTX.client.processes.delete.call_args_list)

    def test_pipe_no_arg(self):
        pipe.Pipe = Mock()
        return_value = 'pipe'
        pipe.Pipe.return_value = return_value

        pipe_obj = syscall.pipe()
        self.assertEqual(pipe_obj, return_value)

    def test_pipe(self):
        return_value = 'pipe'
        side_effect = lambda value: return_value + value
        pipe.Pipe = Mock(side_effect=side_effect)

        name = 'pipe_name'
        pipe_obj = syscall.pipe(name)
        self.assertEqual(pipe_obj, return_value + name)

    def test_fopen(self):
        file.File = Mock()
        return_value = 'file_obj'
        file.File.return_value = return_value

        file_path = 'file_path'
        mode = 'w'
        file_obj = syscall.fopen(file_path, mode=mode)
        self.assertEqual(return_value, file_obj)
        file.File.assert_called_once_with(file_path, mode)

    def test_fopen_no_mode(self):
        file.File = Mock()
        return_value = 'file_obj'
        file.File.return_value = return_value

        file_path = 'file_path'
        mode = 'r'
        file_obj = syscall.fopen(file_path)
        self.assertEqual(return_value, file_obj)
        file.File.assert_called_once_with(file_path, mode)