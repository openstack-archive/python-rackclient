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
import requests
import testtools
from rackclient import client
from mock import patch


class TestCase(testtools.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()


class LibTestCase(testtools.TestCase):

    def setUp(self):
        super(LibTestCase, self).setUp()
        patcher = patch(
            "rackclient.lib." + self.target_context() + ".RACK_CTX")
        self.addCleanup(patcher.stop)
        self.mock_RACK_CTX = patcher.start()
        self._init_context()

    def _init_context(self):
        self.mock_RACK_CTX.gid = "gid"
        self.mock_RACK_CTX.pid = "pid"
        self.mock_RACK_CTX.ppid = None
        self.mock_RACK_CTX.proxy_ip = "10.0.0.2"
        self.mock_RACK_CTX.proxy_url = 'http://10.0.0.2:8088/v1'
        self.mock_RACK_CTX.client = \
            client.Client('1', rack_url=self.mock_RACK_CTX.proxy_url)
        self.mock_RACK_CTX.fs_endpoint = None
        self.mock_RACK_CTX.ipc_endpoint = None
        self.mock_RACK_CTX.shm_endpoint = None

    def target_context(self):
        pass


class TestResponse(requests.Response):
    """
    Class used to wrap requests.Response and provide some
    convenience to initialize with a dict
    """

    def __init__(self, data):
        super(TestResponse, self).__init__()
        self._text = None
        if isinstance(data, dict):
            self.status_code = data.get('status_code')
            self.headers = data.get('headers')
            # Fake the text attribute to streamline Response creation
            self._text = data.get('text')
        else:
            self.status_code = data

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def text(self):
        return self._text
