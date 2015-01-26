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
from rackclient.v1 import proxy


class ProxyTest(utils.TestCase):

    def setUp(self):
        super(ProxyTest, self).setUp()
        self.cs = fakes.FakeClient()
        self.proxy_type = proxy.Proxy
        self.gid = '11111111'
        self.user_id = '4ffc664c198e435e9853f253lkbcd7a7'
        self.project_id = '9sac664c198e435e9853f253lkbcd7a7'

    def test_get(self):
        proxy = self.cs.proxy.get(self.gid)
        self.cs.assert_called('GET', '/groups/%s/proxy' % self.gid)
        self.assertEqual(self.gid, proxy.gid)
        self.assertEqual(self.user_id, proxy.user_id)
        self.assertEqual(self.project_id, proxy.project_id)
        self.assertEqual(None, proxy.ppid)
        self.assertEqual('pppppppp', proxy.nova_instance_id)
        self.assertEqual('proxy', proxy.name)
        self.assertEqual('xxxxxxxx', proxy.glance_image_id)
        self.assertEqual('yyyyyyyy', proxy.nova_flavor_id)
        self.assertEqual('iiiiiiii', proxy.keypair_id)
        self.assertEqual(['jjjjjjjj', 'kkkkkkkk'], proxy.securitygroup_ids)
        networks = [{
            'network_id': 'mmmmmmmm',
            'fixed': '10.0.0.2',
            'floating': '1.1.1.1'
        }]
        self.assertEqual(networks, proxy.networks)
        self.assertEqual('ACTIVE', proxy.app_status)
        self.assertEqual('ACTIVE', proxy.status)
        self.assertEqual('IyEvYmluL3NoICBlY2hvICJIZWxsbyI=', proxy.userdata)
        args = {
            'key1': 'value1',
            'key2': 'value2'
        }
        self.assertEqual(args, proxy.args)
        self.assertEqual('ipc_endpoint', proxy.ipc_endpoint)
        self.assertEqual('shm_endpoint', proxy.shm_endpoint)
        self.assertEqual('fs_endpoint', proxy.fs_endpoint)


    def _create_body(self, name=None, nova_flavor_id=None,
                     glance_image_id=None, keypair_id=None,
                     securitygroup_ids=None, userdata=None, args=None):
        return {
            'proxy': {
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
            'name':'proxy',
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
        proxy = self.cs.proxy.create(self.gid, **params)
        body = self._create_body(**params)
        body['proxy']['userdata'] = base64.b64encode(userdata)
        self.cs.assert_called('POST', '/groups/%s/proxy' % self.gid, body)
        self.assertIsInstance(proxy, self.proxy_type)

    def test_create_invalid_parameters(self):
        self.assertRaises(exc.CommandError, self.cs.proxy.create,
                          self.gid, securitygroup_ids='invalid')
        self.assertRaises(exc.CommandError, self.cs.proxy.create,
                          self.gid, args='invalid')

    def _update_body(self, ipc_endpoint=None, shm_endpoint=None,
                     fs_endpoint=None, app_status=None):
        return {
            'proxy': {
                'ipc_endpoint': ipc_endpoint,
                'shm_endpoint': shm_endpoint,
                'fs_endpoint': fs_endpoint,
                'app_status': app_status
            }
        }

    def test_update(self):
        ipc_endpoint = 'ipc_endpoint'
        shm_endpoint = 'shm_endpoint'
        fs_endpoint = 'fs_endpoint'
        app_status = 'ACTIVE'
        proxy = self.cs.proxy.update(self.gid, shm_endpoint,
                                     ipc_endpoint, fs_endpoint,
                                     app_status)
        body = self._update_body(ipc_endpoint, shm_endpoint,
                                 fs_endpoint, app_status)
        self.cs.assert_called('PUT', '/groups/%s/proxy' % self.gid, body)
        self.assertIsInstance(proxy, self.proxy_type)
