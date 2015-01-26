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
from rackclient.v1 import securitygroups


class SecuritygroupsTest(utils.TestCase):

    def setUp(self):
        super(SecuritygroupsTest, self).setUp()
        self.cs = fakes.FakeClient()
        self.securitygroup_type = securitygroups.Securitygroup
        self.gid = '11111111'
        self.user_id = '4ffc664c198e435e9853f253lkbcd7a7'
        self.project_id = '9sac664c198e435e9853f253lkbcd7a7'

    def test_list(self):
        securitygroups = self.cs.securitygroups.list(self.gid)
        self.cs.assert_called('GET', '/groups/%s/securitygroups' % self.gid)
        for securitygroup in securitygroups:
            self.assertIsInstance(securitygroup, self.securitygroup_type)

    def test_get(self):
        securitygroup_id = 'aaaaaaaa'
        securitygroup = self.cs.securitygroups.get(self.gid, securitygroup_id)
        self.cs.assert_called('GET', '/groups/%s/securitygroups/%s' % (self.gid, securitygroup_id))
        self.assertEqual(self.gid, securitygroup.gid)
        self.assertEqual(self.user_id, securitygroup.user_id)
        self.assertEqual(self.project_id, securitygroup.project_id)
        self.assertEqual(securitygroup_id, securitygroup.securitygroup_id)
        self.assertEqual('pppppppp', securitygroup.neutron_securitygroup_id)
        self.assertEqual('securitygroup1', securitygroup.name)
        self.assertEqual(True, securitygroup.is_default)
        self.assertEqual('Exist', securitygroup.status)

    def _create_body(self, name, is_default, rules):
        return {
            'securitygroup': {
                'name': name,
                'is_default': is_default,
                'securitygrouprules': rules
            }
        }

    def test_create(self):
        name = 'securitygroup1'
        is_default = True
        rules = [{
            'protocol': 'tcp',
            'port_range_max': '80',
            'port_range_min': '80',
            'remote_ip_prefix': '0.0.0.0/0'
        }]
        securitygroup = self.cs.securitygroups.create(self.gid, name, is_default, rules)
        body = self._create_body(name, is_default, rules)
        self.cs.assert_called('POST', '/groups/%s/securitygroups' % self.gid, body)
        self.assertIsInstance(securitygroup, self.securitygroup_type)

    def test_create_invalid_parameters(self):
        name = 'securitygroup1'
        rules = [{
            'protocol': 'tcp',
            'port_range_max': '80',
            'port_range_min': '80',
            'remote_ip_prefix': '0.0.0.0/0'
        }]
        self.assertRaises(exc.CommandError, self.cs.securitygroups.create,
                          self.gid, name, 'invalid', rules)

        rules = {}
        self.assertRaises(exc.CommandError, self.cs.securitygroups.create,
                          self.gid, name, True, rules)

    def _update_body(self, is_default):
        return {
            'securitygroup': {
                'is_default': is_default
            }
        }

    def test_update(self):
        is_default = True
        securitygroup_id = 'aaaaaaaa'
        securitygroup = self.cs.securitygroups.update(self.gid, securitygroup_id, is_default)
        body = self._update_body(is_default)
        self.cs.assert_called('PUT', '/groups/%s/securitygroups/%s' % (self.gid, securitygroup_id), body)
        self.assertIsInstance(securitygroup, self.securitygroup_type)

    def test_update_invalid_parameters(self):
        is_default = 'invalid'
        securitygroup_id = 'aaaaaaaa'
        self.assertRaises(exc.CommandError, self.cs.securitygroups.update,
                          self.gid, securitygroup_id, is_default)

    def test_delete(self):
        securitygroup_id = 'aaaaaaaa'
        self.cs.securitygroups.delete(self.gid, securitygroup_id)
        self.cs.assert_called('DELETE', '/groups/%s/securitygroups/%s' % (self.gid, securitygroup_id))
