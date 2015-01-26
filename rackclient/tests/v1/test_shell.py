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
from ConfigParser import NoOptionError
import StringIO
import copy
import fixtures
import mock
from mock import mock_open
import os
import re
from testtools import matchers
from rackclient import exceptions
import rackclient.shell
from rackclient.v1.proxy import ProxyManager
from rackclient.tests.v1 import fakes
from rackclient.tests import utils


class BaseShellTest(utils.TestCase):

    FAKE_ENV = {
        'RACK_URL': 'http://www.example.com:8088/v1',
        'RACK_GID': '11111111',
    }

    def setUp(self):
        """Run before each test."""
        super(BaseShellTest, self).setUp()

        for var in self.FAKE_ENV:
            self.useFixture(fixtures.EnvironmentVariable(var,
                                                         self.FAKE_ENV[var]))
        self.shell = rackclient.shell.RackShell()
        self.useFixture(fixtures.MonkeyPatch(
            'rackclient.client.get_client_class',
            lambda *_: fakes.FakeClient))

    def assert_called(self, method, url, body=None, **kwargs):
        self.shell.cs.assert_called(method, url, body, **kwargs)

    def assert_called_anytime(self, method, url, body=None):
        self.shell.cs.assert_called_anytime(method, url, body)

    @mock.patch('sys.stdout', new_callable=StringIO.StringIO)
    def run_command(self, cmd, mock_stdout):
        if isinstance(cmd, list):
            self.shell.main(cmd)
        else:
            self.shell.main(cmd.split())
        return mock_stdout.getvalue()


class ShellTest(BaseShellTest):

    def test_group_list(self):
        self.run_command('group-list')
        self.assert_called('GET', '/groups')

    def test_group_show(self):
        self.run_command('group-show 11111111')
        self.assert_called('GET', '/groups/11111111', pos=-6)
        self.assert_called('GET', '/groups/11111111/keypairs', pos=-5)
        self.assert_called('GET', '/groups/11111111/securitygroups', pos=-4)
        self.assert_called('GET', '/groups/11111111/networks', pos=-3)
        self.assert_called('GET', '/groups/11111111/processes', pos=-2)
        self.assert_called('GET', '/groups/11111111/proxy', pos=-1)

    @mock.patch.object(ProxyManager, 'get', side_effect=Exception())
    def test_group_show_no_proxy(self, mock_proxy_manager):
        stdout = self.run_command('group-show 11111111')
        required = '.*?^\|\s+proxy \(pid\)\s+\|\s+\|'
        self.assertThat(stdout,
                        matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_group_create(self):
        self.run_command('group-create --description detail group1')
        self.assert_called('POST', '/groups')

    def test_group_update(self):
        self.run_command('group-update --name group2 --description detail2 11111111')
        self.assert_called('PUT', '/groups/11111111')

    def test_group_delete(self):
        self.run_command('group-delete 11111111')
        self.assert_called('DELETE', '/groups/11111111')

    def test_keypair_list(self):
        self.run_command('keypair-list')
        self.assert_called('GET', '/groups/11111111/keypairs')

    def test_keypair_show(self):
        self.run_command('keypair-show aaaaaaaa')
        self.assert_called('GET', '/groups/11111111/keypairs/aaaaaaaa')

    def test_keypair_create(self):
        self.run_command('keypair-create --name keypair1 '
                         '--is_default true')
        self.assert_called('POST', '/groups/11111111/keypairs')

    def test_keypair_update(self):
        self.run_command('keypair-update --is_default false aaaaaaaa')
        self.assert_called('PUT', '/groups/11111111/keypairs/aaaaaaaa')

    def test_keypair_delete(self):
        self.run_command('keypair-delete aaaaaaaa')
        self.assert_called('DELETE', '/groups/11111111/keypairs/aaaaaaaa')

    def test_securitygroup_list(self):
        self.run_command('securitygroup-list')
        self.assert_called('GET', '/groups/11111111/securitygroups')

    def test_securitygroup_show(self):
        self.run_command('securitygroup-show aaaaaaaa')
        self.assert_called('GET', '/groups/11111111/securitygroups/aaaaaaaa')

    def test_securitygroup_create(self):
        self.run_command('securitygroup-create --name securitygroup1 '
                         '--is_default true '
                         '--rule protocol=tcp,port_range_max=80,'
                         'port_range_min=80,remote_ip_prefix=10.0.0.0/24 '
                         '--rule protocol=icmp,remote_ip_prefix=10.0.0.0/24')
        self.assert_called('POST', '/groups/11111111/securitygroups')

    def test_securitygroup_update(self):
        self.run_command('securitygroup-update --is_default false aaaaaaaa')
        self.assert_called('PUT', '/groups/11111111/securitygroups/aaaaaaaa')

    def test_securitygroup_delete(self):
        self.run_command('securitygroup-delete aaaaaaaa')
        self.assert_called('DELETE', '/groups/11111111/securitygroups/aaaaaaaa')

    def test_network_list(self):
        self.run_command('network-list')
        self.assert_called('GET', '/groups/11111111/networks')

    def test_network_show(self):
        self.run_command('network-show aaaaaaaa')
        self.assert_called('GET', '/groups/11111111/networks/aaaaaaaa')

    def test_network_create(self):
        self.run_command('network-create --name network1 '
                         '--is_admin true '
                         '--gateway_ip 10.0.0.254 '
                         '--dns_nameserver 8.8.8.8 '
                         '--dns_nameserver 8.8.4.4 '
                         '--ext_router_id rrrrrrrr '
                         '10.0.0.0/24')
        self.assert_called('POST', '/groups/11111111/networks')

    def test_network_delete(self):
        self.run_command('network-delete aaaaaaaa')
        self.assert_called('DELETE', '/groups/11111111/networks/aaaaaaaa')

    def test_process_list(self):
        self.run_command('process-list')
        self.assert_called('GET', '/groups/11111111/processes')

    def test_process_show(self):
        self.run_command('process-show aaaaaaaa')
        self.assert_called('GET', '/groups/11111111/processes/aaaaaaaa')

    def test_process_create(self):
        test_userdata = os.path.join(os.path.dirname(__file__), 'test_userdata.txt')
        self.run_command('process-create --ppid aaaaaaaa '
                         '--name process1 '
                         '--nova_flavor_id yyyyyyyy '
                         '--glance_image_id xxxxxxxx '
                         '--keypair_id iiiiiiii '
                         '--securitygroup_id jjjjjjjj '
                         '--securitygroup_id kkkkkkkk '
                         '--userdata %s '
                         '--args key1=value1,key2=value2' % test_userdata)
        self.assert_called('POST', '/groups/11111111/processes')

    def test_process_create_with_no_option(self):
        self.run_command('process-create')
        self.assert_called('POST', '/groups/11111111/processes')

    def test_process_could_not_open_userdata_file(self):
        try:
            self.run_command('process-create --ppid aaaaaaaa '
                             '--userdata not_exists.txt')
        except exceptions.CommandError as e:
            required = ".*?^Can't open 'not_exists.txt'"
            self.assertThat(e.message,
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_process_with_args_file(self):
        test_args = os.path.join(os.path.dirname(__file__), 'test_args.txt')
        self.run_command('process-create --ppid aaaaaaaa '
                         '--args %s' % test_args)
        self.assert_called('POST', '/groups/11111111/processes')

    @mock.patch('__builtin__.open', side_effect=IOError())
    def test_process_could_not_open_args_file(self, m_open):
        try:
            test_args = os.path.join(os.path.dirname(__file__), 'test_args.txt')
            self.run_command('process-create --ppid aaaaaaaa '
                             '--args %s' % test_args)
        except exceptions.CommandError as e:
            required = ".*?^Can't open '.*?rackclient/tests/v1/test_args.txt'"
            self.assertThat(str(e.message),
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_process_invalid_args_file(self):
        invalid_args = os.path.join(os.path.dirname(__file__), 'test_invalid_args.txt')
        try:
            self.run_command('process-create --ppid aaaaaaaa '
                              '--args %s' % invalid_args)
        except exceptions.CommandError as e:
            required = ('.*?rackclient/tests/v1/test_invalid_args.txt '
                        'is not the format of key=value lines')
            self.assertThat(e.message,
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_process_invalid_args(self):
        try:
            self.run_command('process-create --ppid aaaaaaaa '
                             '--args key1value1')
        except exceptions.CommandError as e:
            required = '.*?^\'key1value1\' is not in the format of key=value'
            self.assertThat(str(e.message),
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_process_update(self):
        self.run_command('process-update --app_status ACTIVE aaaaaaaa')
        self.assert_called('PUT', '/groups/11111111/processes/aaaaaaaa')

    def test_process_delete(self):
        self.run_command('process-delete aaaaaaaa')
        self.assert_called('DELETE', '/groups/11111111/processes/aaaaaaaa')

    def test_proxy_show(self):
        self.run_command('proxy-show')
        self.assert_called('GET', '/groups/11111111/proxy')

    def test_proxy_create(self):
        test_userdata = os.path.join(os.path.dirname(__file__), 'test_userdata.txt')
        self.run_command('proxy-create '
                         '--name proxy '
                         '--nova_flavor_id yyyyyyyy '
                         '--glance_image_id xxxxxxxx '
                         '--keypair_id iiiiiiii '
                         '--securitygroup_id jjjjjjjj '
                         '--securitygroup_id kkkkkkkk '
                         '--userdata %s '
                         '--args key1=value1,key2=value2' % test_userdata)
        self.assert_called('POST', '/groups/11111111/proxy')

    def test_proxy_create_with_no_option(self):
        self.run_command('proxy-create')
        self.assert_called('POST', '/groups/11111111/proxy')

    def test_procexy_could_not_open_userdata_file(self):
        try:
            self.run_command('proxy-create '
                             '--userdata not_exists.txt')
        except exceptions.CommandError as e:
            required = ".*?^Can't open 'not_exists.txt'"
            self.assertThat(e.message,
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_proxy_with_args_file(self):
        test_args = os.path.join(os.path.dirname(__file__), 'test_args.txt')
        self.run_command('proxy-create '
                         '--args %s' % test_args)
        self.assert_called('POST', '/groups/11111111/proxy')

    @mock.patch('__builtin__.open', side_effect=IOError())
    def test_proxy_could_not_open_args_file(self, m_open):
        try:
            test_args = os.path.join(os.path.dirname(__file__), 'test_args.txt')
            self.run_command('proxy-create '
                             '--args %s' % test_args)
        except exceptions.CommandError as e:
            required = ".*?^Can't open '.*?rackclient/tests/v1/test_args.txt'"
            self.assertThat(str(e.message),
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_proxy_invalid_args_file(self):
        invalid_args = os.path.join(os.path.dirname(__file__), 'test_invalid_args.txt')
        try:
            self.run_command('proxy-create '
                              '--args %s' % invalid_args)
        except exceptions.CommandError as e:
            required = ('.*?rackclient/tests/v1/test_invalid_args.txt '
                        'is not the format of key=value lines')
            self.assertThat(e.message,
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_proxy_invalid_args(self):
        try:
            self.run_command('proxy-create '
                             '--args key1value1')
        except exceptions.CommandError as e:
            required = '.*?^\'key1value1\' is not in the format of key=value'
            self.assertThat(str(e.message),
                            matchers.MatchesRegex(required, re.DOTALL | re.MULTILINE))

    def test_proxy_update(self):
        self.run_command('proxy-update --app_status ACTIVE '
                         '--shm_endpoint shm_endpoint '
                         '--ipc_endpoint ipc_endpoint '
                         '--fs_endpoint fs_endpoint')
        self.assert_called('PUT', '/groups/11111111/proxy')


class ShellGroupInitTest(BaseShellTest):

    CONFIG = {
        'group': {
            'name': 'group1',
            'description': 'This is group1'
        },
        'keypair': {
            'name': 'keypair1',
            'is_default': 't'
        },
        'securitygroup': {
            'name': 'securitygroup1',
            'is_default': 't',
            'rules': 'protocol=tcp,port_range_max=80,'
                     'port_range_min=80,remote_ip_prefix=10.0.0.0/24 '
                     'protocol=icmp,remote_ip_prefix=10.0.0.0/24'
        },
        'network': {
            'cidr': '10.0.0.0/24',
            'name': 'network1',
            'is_admin': 't',
            'gateway_ip': '10.0.0.254',
            'dns_nameservers': '8.8.8.8 8.8.4.4',
            'ext_router_id': 'rrrrrrrr'
        },
        'proxy': {
            'name': 'proxy',
            'nova_flavor_id': 'yyyyyyyy',
            'glance_image_id': 'xxxxxxxx',
            'args': 'key1=value1,key2=value2'
        }
    }

    def setUp(self):
        super(ShellGroupInitTest, self).setUp()
        self.config = copy.deepcopy(self.CONFIG)
        self.patcher = mock.patch('rackclient.v1.shell.ConfigParser')
        self.mock_config = self.patcher.start()

    def tearDown(self):
        super(BaseShellTest, self).tearDown()
        self.patcher.stop()

    def _fake_get(self, section, key):
        try:
            return self.config[section][key]
        except KeyError:
            raise NoOptionError(key, section)

    def test_group_init(self):
        test_userdata = os.path.join(os.path.dirname(__file__),
                                     'test_userdata.txt')
        self.config['proxy']['userdata'] = test_userdata
        self.mock_config.return_value.get = self._fake_get
        self.run_command('group-init /path/to/group.conf')

    def test_group_init_with_required(self):
        self.config['group'].pop('description')
        self.config['keypair'].pop('name')
        self.config['keypair'].pop('is_default')
        self.config['securitygroup'].pop('name')
        self.config['securitygroup'].pop('is_default')
        self.config['securitygroup'].pop('rules')
        self.config['network'].pop('name')
        self.config['network'].pop('is_admin')
        self.config['network'].pop('gateway_ip')
        self.config['network'].pop('dns_nameservers')
        self.config['network'].pop('ext_router_id')
        self.config['proxy'].pop('name')
        self.config['proxy'].pop('args')
        self.mock_config.return_value.get = self._fake_get
        self.run_command('group-init /path/to/group.conf')

    def test_group_init_without_group_name(self):
        self.config['group'].pop('name')
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = '.*?^Group name is required.'
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))

    def test_group_init_invalid_securitygroup_rules(self):
        self.config['securitygroup']['rules'] = 'invalid'
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = ('.*?^Could not create a securitygroup: '
                        'securitygroup rules are not valid formart: '
                       '\'.*\' is not in the format of key=value')
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))

    def test_group_init_without_network_cidr(self):
        self.config['network'].pop('cidr')
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = '.*?^Network cidr is required.'
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))

    def test_group_init_without_proxy_nova_flavor_id(self):
        self.config['proxy'].pop('nova_flavor_id')
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = '.*?^Flavor id is required.'
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))

    def test_group_init_without_proxy_glance_image_id(self):
        self.config['proxy'].pop('glance_image_id')
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = '.*?^Image id is required.'
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))

    @mock.patch('__builtin__.open', side_effect=IOError())
    def test_group_init_could_not_open_userdata(self, m_open):
        self.config['proxy']['userdata'] = 'fake_userdata.txt'
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = '.*?^Can\'t open fake_userdata.txt.'
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))

    def test_group_init_invalid_args(self):
        self.config['proxy']['args'] = 'key1:value1'
        self.mock_config.return_value.get = self._fake_get

        try:
            self.run_command('group-init /path/to/group.conf')
        except exceptions.CommandError as e:
            required = ('.*?^\'key1:value1\' is not '
                       'in the format of key=value')
            self.assertThat(
                str(e.message),
                matchers.MatchesRegex(required,
                                      re.DOTALL | re.MULTILINE))