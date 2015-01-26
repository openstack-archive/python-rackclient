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
import base64
import tempfile
from rackclient import exceptions as exc
from rackclient.tests import utils
from rackclient.tests.v1 import fakes
from rackclient.v1 import processes


class ProcesssTest(utils.TestCase):

    def setUp(self):
        super(ProcesssTest, self).setUp()
        self.cs = fakes.FakeClient()
        self.process_type = processes.Process
        self.gid = '11111111'
        self.user_id = '4ffc664c198e435e9853f253lkbcd7a7'
        self.project_id = '9sac664c198e435e9853f253lkbcd7a7'

    def test_list(self):
        processes = self.cs.processes.list(self.gid)
        self.cs.assert_called('GET', '/groups/%s/processes' % self.gid)
        for process in processes:
            self.assertIsInstance(process, self.process_type)

    def test_get(self):
        pid = 'aaaaaaaa'
        process = self.cs.processes.get(self.gid, pid)
        self.cs.assert_called('GET', '/groups/%s/processes/%s' % (self.gid, pid))
        self.assertEqual(self.gid, process.gid)
        self.assertEqual(self.user_id, process.user_id)
        self.assertEqual(self.project_id, process.project_id)
        self.assertEqual(pid, process.pid)
        self.assertEqual(None, process.ppid)
        self.assertEqual('pppppppp', process.nova_instance_id)
        self.assertEqual('process1', process.name)
        self.assertEqual('xxxxxxxx', process.glance_image_id)
        self.assertEqual('yyyyyyyy', process.nova_flavor_id)
        self.assertEqual('iiiiiiii', process.keypair_id)
        self.assertEqual(['jjjjjjjj', 'kkkkkkkk'], process.securitygroup_ids)
        networks = [{
            'network_id': 'mmmmmmmm',
            'fixed': '10.0.0.2',
            'floating': '1.1.1.1'
        }]
        self.assertEqual(networks, process.networks)
        self.assertEqual('ACTIVE', process.app_status)
        self.assertEqual('ACTIVE', process.status)
        self.assertEqual('IyEvYmluL3NoICBlY2hvICJIZWxsbyI=', process.userdata)
        args = {
            'key1': 'value1',
            'key2': 'value2'
        }
        self.assertEqual(args, process.args)


    def _create_body(self, ppid=None, name=None, nova_flavor_id=None,
                     glance_image_id=None, keypair_id=None,
                     securitygroup_ids=None, userdata=None, args=None):
        return {
            'process': {
                'ppid': ppid,
                'name': name,
                'nova_flavor_id': nova_flavor_id,
                'glance_image_id': glance_image_id,
                'keypair_id': keypair_id,
                'securitygroup_ids': securitygroup_ids,
                'userdata': userdata,
                'args': args
            }
        }

    def test_create(self):
        userdata = '#!/bin/sh echo "Hello"'
        f = tempfile.TemporaryFile()
        f.write(userdata)
        f.seek(0)
        params = {
            'ppid': '11111111',
            'name':'process1',
            'nova_flavor_id': 1,
            'glance_image_id': '22222222',
            'keypair_id': '33333333',
            'securitygroup_ids': ['44444444', '55555555'],
            'userdata': f,
            'args': {
                "key1": "value1",
                "key2": "value2"
            }
        }
        process = self.cs.processes.create(self.gid, **params)
        body = self._create_body(**params)
        body['process']['userdata'] = base64.b64encode(userdata)
        self.cs.assert_called('POST', '/groups/%s/processes' % self.gid, body)
        self.assertIsInstance(process, self.process_type)

    def test_create_invalid_parameters(self):
        ppid = 'aaaaaaaa'
        self.assertRaises(exc.CommandError, self.cs.processes.create,
                          self.gid, ppid=ppid, securitygroup_ids='invalid')
        self.assertRaises(exc.CommandError, self.cs.processes.create,
                          self.gid, ppid=ppid, args='invalid')

    def _update_body(self, app_status):
        return {
            'process': {
                'app_status': app_status
            }
        }

    def test_update(self):
        app_status = 'ACTIVE'
        pid = 'aaaaaaaa'
        process = self.cs.processes.update(self.gid,
                                          pid, app_status)
        body = self._update_body(app_status)
        self.cs.assert_called('PUT', '/groups/%s/processes/%s' % (self.gid, pid), body)
        self.assertIsInstance(process, self.process_type)

    def test_delete(self):
        pid = 'aaaaaaaa'
        self.cs.processes.delete(self.gid, pid)
        self.cs.assert_called('DELETE', '/groups/%s/processes/%s' % (self.gid, pid))
