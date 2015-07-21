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
from rackclient import exceptions as exc
from rackclient.tests import utils
from rackclient.tests.v1 import fakes
from rackclient.v1 import networks


class NetworksTest(utils.TestCase):

    def setUp(self):
        super(NetworksTest, self).setUp()
        self.cs = fakes.FakeClient()
        self.network_type = networks.Network
        self.gid = '11111111'
        self.user_id = '4ffc664c198e435e9853f253lkbcd7a7'
        self.project_id = '9sac664c198e435e9853f253lkbcd7a7'

    def test_list(self):
        networks = self.cs.networks.list(self.gid)
        self.cs.assert_called('GET', '/groups/%s/networks' % self.gid)
        for network in networks:
            self.assertIsInstance(network, self.network_type)

    def test_get(self):
        network_id = 'aaaaaaaa'
        network = self.cs.networks.get(self.gid, network_id)
        self.cs.assert_called('GET', '/groups/%s/networks/%s'
                                     % (self.gid, network_id))
        self.assertEqual(self.gid, network.gid)
        self.assertEqual(self.user_id, network.user_id)
        self.assertEqual(self.project_id, network.project_id)
        self.assertEqual(network_id, network.network_id)
        self.assertEqual('pppppppp', network.neutron_network_id)
        self.assertEqual('network1', network.name)
        self.assertEqual(True, network.is_admin)
        self.assertEqual('rrrrrrrr', network.ext_router_id)
        self.assertEqual('Exist', network.status)

    def _create_body(self, cidr, name=None, is_admin=False, gateway=None,
                     dns_nameservers=None, ext_router_id=None):
        return {
            'network': {
                'cidr': cidr,
                'name': name,
                'is_admin': is_admin,
                'gateway': gateway,
                'dns_nameservers': dns_nameservers,
                'ext_router_id': ext_router_id
            }
        }

    def test_create(self):
        cidr = '10.0.0.0/24'
        name = 'network1'
        is_admin = True
        dns_nameservers = ['8.8.8.8', '8.8.4.4']
        gateway = '10.0.0.254'
        ext_router_id = 'rrrrrrrr'

        network = self.cs.networks.create(
            self.gid, cidr, name, is_admin, gateway,
            dns_nameservers, ext_router_id)
        body = self._create_body(
            cidr, name, is_admin, gateway,
            dns_nameservers, ext_router_id)
        self.cs.assert_called('POST', '/groups/%s/networks' % self.gid, body)
        self.assertIsInstance(network, self.network_type)

    def test_create_invalid_parameters(self):
        name = 'network1'
        ext_router_id = 'rrrrrrrr'
        self.assertRaises(exc.CommandError, self.cs.networks.create,
                          self.gid, 'invalid', name, True, '10.0.0.254',
                          ['8.8.8.8', '8.8.4.4'], ext_router_id)
        self.assertRaises(exc.CommandError, self.cs.networks.create,
                          self.gid, '10.0.0.0', name, True, '10.0.0.254',
                          ['8.8.8.8', '8.8.4.4'], ext_router_id)
        self.assertRaises(exc.CommandError, self.cs.networks.create,
                          self.gid, '10.0.0.0/24', name, 'invalid',
                          '10.0.0.254', ['8.8.8.8', '8.8.4.4'], ext_router_id)
        self.assertRaises(exc.CommandError, self.cs.networks.create,
                          self.gid, '10.0.0.0/24', name, True, 'invalid',
                          ['8.8.8.8', '8.8.4.4'], ext_router_id)
        self.assertRaises(exc.CommandError, self.cs.networks.create,
                          self.gid, '10.0.0.0/24', name, True, '10.0.0.254',
                          {}, ext_router_id)

    def test_delete(self):
        network_id = 'aaaaaaaa'
        self.cs.networks.delete(self.gid, network_id)
        self.cs.assert_called('DELETE', '/groups/%s/networks/%s'
                                        % (self.gid, network_id))
