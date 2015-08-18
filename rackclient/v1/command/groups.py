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
import argparse
import os
import time

from ConfigParser import ConfigParser
from ConfigParser import NoOptionError

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

from rackclient import client
from rackclient import exceptions
from rackclient import utils


def _make_print_data(gid, name, description, user_id, project_id,
                     status, keypairs=None, securitygroups=None,
                     networks=None, proxy=None, processes=None):
    columns = ['gid', 'name', 'description', 'user_id', 'project_id', 'status']
    data = [gid, name, description, user_id, project_id, status]

    if keypairs is not None:
        columns.append('keypairs')
        data.append(keypairs)

    if securitygroups is not None:
        columns.append('securitygroups')
        data.append(securitygroups)

    if networks is not None:
        columns.append('networks')
        data.append(networks)

    if proxy is not None:
        columns.append('proxy')
        data.append(proxy)

    if processes is not None:
        columns.append('processes')
        data.append(processes)

    return columns, data


class RackConfigParser(ConfigParser):
    def get_ex(self, section, value):
        try:
            return self.get(section, value)
        except NoOptionError:
            pass


class ListGroups(Lister):
    """
    Print a list of all groups.
    """
    def __init__(self, app, app_args):
        super(ListGroups, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)

    def take_action(self, parsed_args):
        groups = self.client.groups.list()
        return (
            ('gid', 'name', 'description', 'status'),
            ((g.gid, g.name, g.description, g.status) for g in groups)
        )


class ShowGroup(ShowOne):
    """
    Show details about the given group.
    """
    def __init__(self, app, app_args):
        super(ShowGroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)

    def get_parser(self, prog_name):
        parser = super(ShowGroup, self).get_parser(prog_name)
        parser.add_argument('gid', metavar='<gid>',
                            default=os.environ.get('RACK_GID'),
                            help="Group id")
        return parser

    def take_action(self, parsed_args):
        group = self.client.groups.get(parsed_args.gid)
        keypairs = self.client.keypairs.list(parsed_args.gid)
        securitygroups = self.client.securitygroups.list(parsed_args.gid)
        networks = self.client.networks.list(parsed_args.gid)
        try:
            proxy = self.client.proxy.get(parsed_args.gid)
        except Exception:
            proxy = None

        return _make_print_data(
            group.gid,
            group.name,
            group.description,
            group.user_id,
            group.project_id,
            group.status,
            ','.join([k.keypair_id for k in keypairs]),
            ','.join([s.securitygroup_id for s in securitygroups]),
            ','.join([n.network_id for n in networks]),
            proxy.pid if proxy else ''
        )


class CreateGroup(ShowOne):
    """
    Create a new group.
    """
    def __init__(self, app, app_args):
        super(CreateGroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)

    def get_parser(self, prog_name):
        parser = super(CreateGroup, self).get_parser(prog_name)
        parser.add_argument('name', metavar='<name>',
                            help="Name of the new group")
        parser.add_argument('--description', metavar='<description>',
                            help="Details of the new group")
        return parser

    def take_action(self, parsed_args):
        group = self.client.groups.create(
            parsed_args.name,
            parsed_args.description)
        return _make_print_data(
            group.gid,
            group.name,
            group.description,
            group.user_id,
            group.project_id,
            group.status
        )


class UpdateGroup(ShowOne):
    """
    Update the specified group.
    """
    def __init__(self, app, app_args):
        super(UpdateGroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)

    def get_parser(self, prog_name):
        parser = super(UpdateGroup, self).get_parser(prog_name)
        parser.add_argument('gid', metavar='<gid>',
                            help="Group id")
        parser.add_argument('--name', metavar='<name>',
                            help="Name of the group")
        parser.add_argument('--description', metavar='<description>',
                            help="Details of the group")
        return parser

    def take_action(self, parsed_args):
        group = self.client.groups.update(parsed_args.gid,
                                          parsed_args.name,
                                          parsed_args.description)
        return _make_print_data(
            group.gid,
            group.name,
            group.description,
            group.user_id,
            group.project_id,
            group.status
        )


class DeleteGroup(Command):
    """
    Delete the specified group.
    """
    def __init__(self, app, app_args):
        super(DeleteGroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)

    def get_parser(self, prog_name):
        parser = super(DeleteGroup, self).get_parser(prog_name)
        parser.add_argument('gid', metavar='<gid>',
                            help="Group id")
        return parser

    def take_action(self, parsed_args):
        self.client.groups.delete(parsed_args.gid)


class InitGroup(ShowOne):
    """
    Create a group, a keypair, a security group, a network and
    a rack-proxy based on the specified configuration file.
    """
    def __init__(self, app, app_args):
        super(InitGroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)

    def get_parser(self, prog_name):
        parser = super(InitGroup, self).get_parser(prog_name)
        parser.add_argument('config', metavar='<config-file>',
                            help=("Configuration file including parameters"
                                  " of the new group"))
        return parser

    def take_action(self, parsed_args):
        config = RackConfigParser()
        config.read(parsed_args.config)

        group_description = None
        keypair_name = None
        keypair_is_default = True
        securitygroup_name = None
        securitygroup_is_default = True
        securitygroup_rules = None
        network_name = None
        network_is_admin = True
        network_gateway_ip = None
        network_dns_nameservers = []
        proxy_name = None

        # Required options
        try:
            group_name = config.get('group', 'name')
            network_cidr = config.get('network', 'cidr')
            network_ext_router_id = config.get('network', 'ext_router_id')
            proxy_flavor = config.get('proxy', 'nova_flavor_id')
            proxy_image = config.get('proxy', 'glance_image_id')
        except NoOptionError as e:
            msg = "%s in %s section is required." % (e.option, e.section)
            raise exceptions.CommandError(msg)

        try:
            securitygroup_rules = config.get('securitygroup', 'rules').split()
            securitygroup_rules = \
                [utils.keyvalue_to_dict(r) for r in securitygroup_rules]
        except argparse.ArgumentTypeError:
            raise exceptions.CommandError(
                "securitygroup rules are not valid formart")
        except NoOptionError:
            pass

        group_description = config.get_ex('group', 'description')
        keypair_name = config.get_ex('keypair', 'name')
        keypair_is_default = config.get_ex('keypair', 'is_default')
        securitygroup_name = config.get_ex('securitygroup', 'name')
        securitygroup_is_default = \
            config.get_ex('securitygroup', 'is_default')
        network_name = config.get_ex('network', 'name')
        network_is_admin = config.get_ex('network', 'is_admin')
        network_gateway_ip = config.get_ex('network', 'gateway_ip')
        network_dns_nameservers = \
            config.get_ex('network', 'dns_nameservers').split()
        proxy_name = config.get_ex('proxy', 'name')
        process_name = config.get_ex('process', 'name')
        process_flavor = config.get_ex('process', 'nova_flavor_id')
        process_image = config.get_ex('process', 'glance_image_id')

        try:
            process_args = config.get('process', 'args')
            process_args = utils.keyvalue_to_dict(process_args)
        except argparse.ArgumentTypeError:
            raise exceptions.CommandError(
                "process args are not valid formart")
        except NoOptionError:
            pass

        group = self.client.groups.create(group_name, group_description)
        keypair = self.client.keypairs.create(group.gid, keypair_name,
                                              keypair_is_default)
        securitygroup = self.client.securitygroups.create(
            group.gid,
            securitygroup_name,
            securitygroup_is_default,
            securitygroup_rules)
        network = self.client.networks.create(
            group.gid, network_cidr, network_name,
            network_is_admin, network_gateway_ip,
            network_dns_nameservers,
            network_ext_router_id)
        proxy = self.client.proxy.create(
            group.gid, name=proxy_name,
            nova_flavor_id=proxy_flavor,
            glance_image_id=proxy_image,
            keypair_id=keypair.keypair_id,
            securitygroup_ids=[securitygroup.securitygroup_id])

        columns = ['gid', 'keypair_id', 'securitygroup_id', 'network_id',
                   'proxy_pid', 'proxy_name']
        data = [group.gid, keypair.keypair_id, securitygroup.securitygroup_id,
                network.network_id, proxy.pid, proxy.name]

        if process_image:
            while True:
                p = self.client.processes.get(proxy.gid, proxy.pid)
                if p.app_status == "ACTIVE":
                    break
                time.sleep(1)
            process = self.client.processes.create(
                gid=group.gid,
                name=process_name,
                nova_flavor_id=process_flavor,
                glance_image_id=process_image,
                args=process_args)
            columns.append('pid')
            data.append(process.pid)

        return columns, data
