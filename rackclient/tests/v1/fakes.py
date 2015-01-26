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
import urlparse
from rackclient import client as base_client
from rackclient.tests import fakes
from rackclient.tests import utils
from rackclient.v1 import client


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, *args, **kwargs):
        client.Client.__init__(self, 'rack_rul', 'http_log_debug')
        self.client = FakeHTTPClient()


class FakeHTTPClient(base_client.HTTPClient):

    def __init__(self, **kwargs):
        self.rack_url = 'rack_url'
        self.http_log_debug = 'http_log_debug'
        self.callstack = []

    def request(self, url, method, **kwargs):
        if method in ['GET', 'DELETE']:
            assert 'body' not in kwargs
        elif method == 'PUT':
            assert 'body' in kwargs

        args = urlparse.parse_qsl(urlparse.urlparse(url)[4])
        kwargs.update(args)
        munged_url = url.rsplit('?', 1)[0]
        munged_url = munged_url.strip('/').replace('/', '_').replace('.', '_')
        munged_url = munged_url.replace('-', '_')
        munged_url = munged_url.replace(' ', '_')

        callback = "%s_%s" % (method.lower(), munged_url)

        if not hasattr(self, callback):
            raise AssertionError('Called unknown API method: %s %s, '
                                 'expected fakes method name: %s' %
                                 (method, url, callback))

        self.callstack.append((method, url, kwargs.get('body')))

        status, headers, body = getattr(self, callback)(**kwargs)
        r = utils.TestResponse({
            "status_code": status,
            "text": body,
            "headers": headers,
        })
        return r, body

    #
    # groups
    #

    def get_groups(self, **kw):
        groups = {'groups': [
            {
                'gid': '11111111',
                "user_id": '4ffc664c198e435e9853f253lkbcd7a7',
                "project_id": '9sac664c198e435e9853f253lkbcd7a7',
                "name": 'group1',
                "description": 'This is group1',
                "status": 'ACTIVE'
            },
            {
                'gid': '22222222',
                "user_id": '4ffc664c198e435e9853f253lkbcd7a7',
                "project_id": '9sac664c198e435e9853f253lkbcd7a7',
                "name": 'group2',
                "description": 'This is group2',
                "status": 'ACTIVE'
            }
        ]}
        return (200, {}, groups)

    def get_groups_11111111(self, **kw):
        group = {'group': self.get_groups()[2]["groups"][0]}
        return (200, {}, group)

    def post_groups(self, body, **kw):
        group = {'group': self.get_groups()[2]["groups"][0]}
        return (201, {}, group)

    def put_groups_11111111(self, body, **kw):
        group = {'group': self.get_groups()[2]["groups"][0]}
        return (200, {}, group)

    def delete_groups_11111111(self, **kw):
        return (204, {}, None)

    #
    # keypairs
    #

    def get_groups_11111111_keypairs(self, **kw):
        keypairs = {'keypairs': [
            {
                'keypair_id': 'aaaaaaaa',
                'nova_keypair_id': 'keypair1',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'name': 'keypair1',
                'private_key': '1234',
                'is_default': True,
                'status': 'Exist'
            },
            {
                'keypair_id': 'bbbbbbbb',
                'nova_keypair_id': 'keypair2',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'name': 'keypair2',
                'private_key': '5678',
                'is_default': False,
                'status': 'Exist'
            }
        ]}
        return (200, {}, keypairs)

    def get_groups_11111111_keypairs_aaaaaaaa(self, **kw):
        keypair = {'keypair': self.get_groups_11111111_keypairs()[2]['keypairs'][0]}
        return (200, {}, keypair)

    def post_groups_11111111_keypairs(self, body, **kw):
        keypair = {'keypair': self.get_groups_11111111_keypairs()[2]['keypairs'][0]}
        return (201, {}, keypair)

    def put_groups_11111111_keypairs_aaaaaaaa(self, body, **kw):
        keypair = {'keypair': self.get_groups_11111111_keypairs()[2]['keypairs'][0]}
        return (200, {}, keypair)

    def delete_groups_11111111_keypairs_aaaaaaaa(self, **kw):
        return (204, {}, None)

    #
    # securitygroups
    #

    def get_groups_11111111_securitygroups(self, **kw):
        securitygroups = {'securitygroups': [
            {
                'securitygroup_id': 'aaaaaaaa',
                'neutron_securitygroup_id': 'pppppppp',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'name': 'securitygroup1',
                'is_default': True,
                'status': 'Exist'
            },
            {
                'securitygroup_id': 'bbbbbbbb',
                'neutron_securitygroup_id': 'qqqqqqqq',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'name': 'securitygroup2',
                'is_default': False,
                'status': 'Exist'
            }
        ]}
        return (200, {}, securitygroups)

    def get_groups_11111111_securitygroups_aaaaaaaa(self, **kw):
        securitygroup = {'securitygroup': self.get_groups_11111111_securitygroups()[2]['securitygroups'][0]}
        return (200, {}, securitygroup)

    def post_groups_11111111_securitygroups(self, body, **kw):
        securitygroup = {'securitygroup': self.get_groups_11111111_securitygroups()[2]['securitygroups'][0]}
        return (201, {}, securitygroup)

    def put_groups_11111111_securitygroups_aaaaaaaa(self, body, **kw):
        securitygroup = {'securitygroup': self.get_groups_11111111_securitygroups()[2]['securitygroups'][0]}
        return (200, {}, securitygroup)

    def delete_groups_11111111_securitygroups_aaaaaaaa(self, **kw):
        return (204, {}, None)

    #
    # networks
    #

    def get_groups_11111111_networks(self, **kw):
        networks = {'networks': [
            {
                'network_id': 'aaaaaaaa',
                'neutron_network_id': 'pppppppp',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'name': 'network1',
                'is_admin': True,
                'ext_router_id': 'rrrrrrrr',
                'status': 'Exist'
            },
            {
                'network_id': 'bbbbbbbb',
                'neutron_network_id': 'qqqqqqqq',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'name': 'network2',
                'is_admin': False,
                'ext_router_id': 'rrrrrrrr',
                'status': 'Exist'
            }
        ]}
        return (200, {}, networks)

    def get_groups_11111111_networks_aaaaaaaa(self, **kw):
        network = {'network': self.get_groups_11111111_networks()[2]['networks'][0]}
        return (200, {}, network)

    def post_groups_11111111_networks(self, body, **kw):
        network = {'network': self.get_groups_11111111_networks()[2]['networks'][0]}
        return (201, {}, network)

    def delete_groups_11111111_networks_aaaaaaaa(self, **kw):
        return (204, {}, None)
    
    #
    # processes
    #

    def get_groups_11111111_processes(self, **kw):
        processes = {'processes': [
            {
                'nova_instance_id': 'pppppppp',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'pid': 'aaaaaaaa',
                'ppid': None,
                'name': 'process1',
                'glance_image_id': 'xxxxxxxx',
                'nova_flavor_id': 'yyyyyyyy',
                'keypair_id': 'iiiiiiii',
                'securitygroup_ids': [
                    'jjjjjjjj', 'kkkkkkkk'
                ],
                'networks': [
                    {'network_id': 'mmmmmmmm',
                     'fixed': '10.0.0.2',
                     'floating': '1.1.1.1'}
                ],
                'app_status': 'ACTIVE',
                'userdata': 'IyEvYmluL3NoICBlY2hvICJIZWxsbyI=',
                'status': 'ACTIVE',
                'args': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            },
            {
                'process_id': 'bbbbbbbb',
                'nova_instance_id': 'qqqqqqqq',
                'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
                'project_id': '9sac664c198e435e9853f253lkbcd7a7',
                'gid': '11111111',
                'pid': 'bbbbbbbb',
                'ppid': 'aaaaaaaa',
                'name': 'process2',
                'glance_image_id': 'xxxxxxxx',
                'nova_flavor_id': 'yyyyyyyy',
                'keypair_id': 'iiiiiiii',
                'securitygroup_ids': [
                    'jjjjjjjj', 'kkkkkkkk'
                ],
                'networks': [
                    {'network_id': 'mmmmmmmm',
                     'fixed': '10.0.0.3',
                     'floating': '2.2.2.2'}
                ],
                'app_status': 'ACTIVE',
                'userdata': 'IyEvYmluL3NoICBlY2hvICJIZWxsbyI=',
                'status': 'ACTIVE',
                'args': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
        ]}
        return (200, {}, processes)

    def get_groups_11111111_processes_aaaaaaaa(self, **kw):
        process = {'process': self.get_groups_11111111_processes()[2]['processes'][0]}
        return (200, {}, process)

    def post_groups_11111111_processes(self, body, **kw):
        process = {'process': self.get_groups_11111111_processes()[2]['processes'][0]}
        return (202, {}, process)

    def put_groups_11111111_processes_aaaaaaaa(self, body, **kw):
        process = {'process': self.get_groups_11111111_processes()[2]['processes'][0]}
        return (200, {}, process)

    def delete_groups_11111111_processes_aaaaaaaa(self, **kw):
        return (204, {}, None)

    #
    # proxy
    #

    def get_groups_11111111_proxy(self, **kw):
        proxy = {'proxy': {
            'nova_instance_id': 'pppppppp',
            'user_id': '4ffc664c198e435e9853f253lkbcd7a7',
            'project_id': '9sac664c198e435e9853f253lkbcd7a7',
            'gid': '11111111',
            'pid': 'aaaaaaaa',
            'ppid': None,
            'name': 'proxy',
            'glance_image_id': 'xxxxxxxx',
            'nova_flavor_id': 'yyyyyyyy',
            'keypair_id': 'iiiiiiii',
            'securitygroup_ids': [
                'jjjjjjjj', 'kkkkkkkk'
            ],
            'networks': [
                {'network_id': 'mmmmmmmm',
                 'fixed': '10.0.0.2',
                 'floating': '1.1.1.1'}
            ],
            'app_status': 'ACTIVE',
            'userdata': 'IyEvYmluL3NoICBlY2hvICJIZWxsbyI=',
            'status': 'ACTIVE',
            'args': {
                'key1': 'value1',
                'key2': 'value2'
            },
            'ipc_endpoint': 'ipc_endpoint',
            'shm_endpoint': 'shm_endpoint',
            'fs_endpoint': 'fs_endpoint'
        }}
        return (200, {}, proxy)

    def post_groups_11111111_proxy(self, body, **kw):
        proxy = {'proxy': self.get_groups_11111111_proxy()[2]['proxy']}
        return (202, {}, proxy)

    def put_groups_11111111_proxy(self, body, **kw):
        proxy = {'proxy': self.get_groups_11111111_proxy()[2]['proxy']}
        return (200, {}, proxy)
