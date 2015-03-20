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
import json
import logging
import mock
import fixtures
import requests
from rackclient import client
from rackclient.tests import utils


class ClientTest(utils.TestCase):

    def test_log_req(self):
        self.logger = self.useFixture(
            fixtures.FakeLogger(
                name=client.__name__,
                format="%(message)s",
                level=logging.DEBUG,
                nuke_handlers=True
            )
        )
        cs = client.HTTPClient('rack_url', True)

        cs.http_log_req('GET', '/foo', {'headers': {}})
        cs.http_log_req('GET', '/foo', {'headers': {
            'Content-Type': 'application/json',
            'User-Agent': 'python-rackclient'
        }})

        data = {'group': {
            'name': 'group1',
            'description': 'This is group1'
        }}
        cs.http_log_req('POST', '/foo', {
            'headers': {
                'Content-Type': 'application/json'
            },
            'data': json.dumps(data)
        })

        output = self.logger.output.split('\n')
        self.assertIn("REQ: curl -i '/foo' -X GET", output)
        self.assertIn("REQ: curl -i '/foo' -X GET "
                      '-H "Content-Type: application/json" '
                      '-H "User-Agent: python-rackclient"',
                      output)
        self.assertIn("REQ: curl -i '/foo' -X POST "
                      '-H "Content-Type: application/json" '
                      '-d \'{"group": {"name": "group1", '
                      '"description": "This is group1"}}\'',
                      output)

    def test_log_resp(self):
        self.logger = self.useFixture(
            fixtures.FakeLogger(
                name=client.__name__,
                format="%(message)s",
                level=logging.DEBUG,
                nuke_handlers=True
            )
        )
        cs = client.HTTPClient('rack_url', True)

        text = '{"group": {"name": "group1", "description": "This is group1"}}'
        resp = utils.TestResponse({'status_code': 200, 'headers': {},
                                   'text': text})
        cs.http_log_resp(resp)

        output = self.logger.output.split('\n')
        self.assertIn("RESP: [200] {}", output)
        self.assertIn('RESP BODY: {"group": {"name": "group1", '
                      '"description": "This is group1"}}', output)

    def test_request(self):
        cs = client.HTTPClient('http://www.foo.com', False)
        data = (
            '{"group": { "gid": "11111111",'
            '"user_id": "4ffc664c198e435e9853f253lkbcd7a7",'
            '"project_id": "9sac664c198e435e9853f253lkbcd7a7",'
            '"name": "group1",'
            '"description": "This is group1",'
            '"status": "ACTIVE"}}'
        )

        mock_request = mock.Mock()
        mock_request.return_value = requests.Response()
        mock_request.return_value.status_code = 201
        mock_request.return_value._content = data

        with mock.patch('requests.request', mock_request):
            resp, body = cs.post('/groups', body=data)
            kwargs = {
                'headers': {
                    'User-Agent': 'python-rackclient',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                'data': json.dumps(data)
            }
            mock_request.assert_called_with('POST',
                                            'http://www.foo.com/groups',
                                            **kwargs)

    def test_request_raise_exception(self):
        cs = client.HTTPClient('http://www.foo.com', False)

        mock_request = mock.Mock()
        mock_request.return_value = requests.Response()
        mock_request.return_value.status_code = 404

        mock_exec = mock.Mock()
        mock_exec.return_value = Exception('Not Found')

        with mock.patch('requests.request', mock_request):
            with mock.patch('rackclient.exceptions.from_response',
                            mock_exec):
                self.assertRaises(Exception, cs.get, '/groups')