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
from mock import patch
import requests
from rackclient import process_context as pctxt
from rackclient.tests import utils
from rackclient.v1.proxy import ProxyManager, Proxy
from rackclient import exceptions


class ProcessContextTest(utils.TestCase):

    def setUp(self):
        super(ProcessContextTest, self).setUp()

        patcher = patch('requests.get')
        self.addCleanup(patcher.stop)
        self.mock_request = patcher.start()
        self.mock_request.return_value = requests.Response()
        self.mock_request.return_value._content = \
            ('{"meta": {"gid": "11111111", '
             '"pid": "22222222", "ppid": "33333333", '
             '"proxy_ip": "10.0.0.2", "opt1": "value1", '
             '"opt2": "value2"}}')

    @patch.object(ProxyManager, 'get')
    def test_init(self, mock_proxy_get):
        proxy = {
            'fs_endpoint': 'fs_endpoint',
            'shm_endpoint': 'shm_endpoint',
            'ipc_endpoint': 'ipc_endpoint'
        }
        mock_proxy_get.return_value = Proxy(None, proxy)

        pctxt.init()
        d = pctxt.PCTXT.__dict__
        d.pop('client')

        expected = {
            'ipc_endpoint': 'ipc_endpoint',
            'fs_endpoint': 'fs_endpoint',
            'proxy_url': 'http://10.0.0.2:8088/v1',
            'pid': '22222222',
            'gid': '11111111',
            'proxy_ip': '10.0.0.2',
            'shm_endpoint': 'shm_endpoint',
            'ppid': '33333333',
            'opt1': 'value1',
            'opt2': 'value2'
        }
        self.assertEqual(expected, d)
        mock_proxy_get.assert_called_with('11111111')

    def test_init_metadata_error(self):
        self.mock_request.side_effect = Exception()
        self.assertRaises(exceptions.MetadataAccessError, pctxt.init)
