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
from rackclient.tests.v1 import fakes
from rackclient.v1 import groups


class GroupsTest(utils.TestCase):

    def setUp(self):
        super(GroupsTest, self).setUp()
        self.cs = fakes.FakeClient()
        self.group_type = groups.Group

    def test_list(self):
        groups = self.cs.groups.list()
        self.cs.assert_called('GET', '/groups')
        for group in groups:
            self.assertIsInstance(group, self.group_type)

    def test_get(self):
        group = self.cs.groups.get('11111111')
        self.cs.assert_called('GET', '/groups/11111111')
        self.assertEqual('11111111', group.gid)
        self.assertEqual('4ffc664c198e435e9853f253lkbcd7a7', group.user_id)
        self.assertEqual('9sac664c198e435e9853f253lkbcd7a7', group.project_id)
        self.assertEqual('group1', group.name)
        self.assertEqual('This is group1', group.description)
        self.assertEqual('ACTIVE', group.status)

    def _create_body(self, name, description):
        return {
            'group': {
                'name': name,
                'description': description
            }
        }

    def test_create(self):
        name = 'group1'
        description = 'This is group1'
        group = self.cs.groups.create(name, description)
        body = self._create_body(name, description)
        self.cs.assert_called('POST', '/groups', body)
        self.assertIsInstance(group, self.group_type)

    def test_update(self):
        gid = '11111111'
        name = 'group1'
        description = 'This is group1'
        group = self.cs.groups.update(gid, name, description)
        body = self._create_body(name, description)
        self.cs.assert_called('PUT', '/groups/11111111', body)
        self.assertIsInstance(group, self.group_type)

    def test_delete(self):
        gid = '11111111'
        self.cs.groups.delete(gid)
        self.cs.assert_called('DELETE', '/groups/11111111')
