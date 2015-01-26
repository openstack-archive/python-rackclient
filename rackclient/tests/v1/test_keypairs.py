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
from rackclient.v1 import keypairs


class KeypairsTest(utils.TestCase):

    def setUp(self):
        super(KeypairsTest, self).setUp()
        self.cs = fakes.FakeClient()
        self.keypair_type = keypairs.Keypair
        self.gid = '11111111'
        self.user_id = '4ffc664c198e435e9853f253lkbcd7a7'
        self.project_id = '9sac664c198e435e9853f253lkbcd7a7'

    def test_list(self):
        keypairs = self.cs.keypairs.list(self.gid)
        self.cs.assert_called('GET', '/groups/%s/keypairs' % self.gid)
        for keypair in keypairs:
            self.assertIsInstance(keypair, self.keypair_type)

    def test_get(self):
        keypair_id = 'aaaaaaaa'
        keypair = self.cs.keypairs.get(self.gid, keypair_id)
        self.cs.assert_called('GET', '/groups/%s/keypairs/%s' % (self.gid, keypair_id))
        self.assertEqual(self.gid, keypair.gid)
        self.assertEqual(self.user_id, keypair.user_id)
        self.assertEqual(self.project_id, keypair.project_id)
        self.assertEqual(keypair_id, keypair.keypair_id)
        self.assertEqual('keypair1', keypair.nova_keypair_id)
        self.assertEqual('keypair1', keypair.name)
        self.assertEqual('1234', keypair.private_key)
        self.assertEqual(True, keypair.is_default)
        self.assertEqual('Exist', keypair.status)

    def _create_body(self, name, is_default):
        return {
            'keypair': {
                'name': name,
                'is_default': is_default
            }
        }

    def test_create(self):
        name = 'keypair1'
        is_default = True
        keypair = self.cs.keypairs.create(self.gid, name, is_default)
        body = self._create_body(name, is_default)
        self.cs.assert_called('POST', '/groups/%s/keypairs' % self.gid, body)
        self.assertIsInstance(keypair, self.keypair_type)

    def test_create_invalid_parameters(self):
        name = 'keypair1'
        is_default = 'invalid'
        self.assertRaises(exc.CommandError, self.cs.keypairs.create,
                          self.gid, name, is_default)

    def _update_body(self, is_default):
        return {
            'keypair': {
                'is_default': is_default
            }
        }

    def test_update(self):
        is_default = True
        keypair_id = 'aaaaaaaa'
        keypair = self.cs.keypairs.update(self.gid,
                                          keypair_id, is_default)
        body = self._update_body(is_default)
        self.cs.assert_called('PUT', '/groups/%s/keypairs/%s' % (self.gid, keypair_id), body)
        self.assertIsInstance(keypair, self.keypair_type)

    def test_update_invalid_parameters(self):
        is_default = 'invalid'
        keypair_id = 'aaaaaaaa'
        self.assertRaises(exc.CommandError, self.cs.keypairs.update,
                          self.gid, keypair_id, is_default)

    def test_delete(self):
        keypair_id = 'aaaaaaaa'
        self.cs.keypairs.delete(self.gid, keypair_id)
        self.cs.assert_called('DELETE', '/groups/%s/keypairs/%s' % (self.gid, keypair_id))
