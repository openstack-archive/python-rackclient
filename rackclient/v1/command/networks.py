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

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

from rackclient import client
from rackclient import exceptions


def _make_print_data(network_id, name, neutron_network_id, is_admin,
                     cidr, ext_router_id, gid, user_id, project_id,
                     status=None):
    columns = ['network_id', 'name', 'neutron_network_id', 'is_admin',
               'cidr', 'ext_router_id', 'gid', 'user_id', 'project_id']
    data = [network_id, name, neutron_network_id, is_admin,
            cidr, ext_router_id, gid, user_id, project_id]

    if status is not None:
        columns.append('status')
        data.append(status)

    return columns, data


class ListNetworks(Lister):
    """
    Print a list of all networks in the specified group.
    """
    def __init__(self, app, app_args):
        super(ListNetworks, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def take_action(self, parsed_args):
        networks = self.client.networks.list(self.gid)
        return (
            ('network_id', 'name', 'is_admin', 'status'),
            ((n.network_id, n.name, n.is_admin, n.status) for n in networks)
        )


class ShowNetwork(ShowOne):
    """
    Show details about the given network group.
    """
    def __init__(self, app, app_args):
        super(ShowNetwork, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(ShowNetwork, self).get_parser(prog_name)
        parser.add_argument('network_id', metavar='<network-id>',
                            help="Network ID")
        return parser

    def take_action(self, parsed_args):
        network = self.client.networks.get(self.gid,
                                           parsed_args.network_id)
        return _make_print_data(
            network.network_id,
            network.name,
            network.neutron_network_id,
            network.is_admin,
            network.cidr,
            network.ext_router_id,
            network.gid,
            network.user_id,
            network.project_id,
            network.status,
        )


class CreateNetwork(ShowOne):
    """
    Create a new securitygroup.
    """
    def __init__(self, app, app_args):
        super(CreateNetwork, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(CreateNetwork, self).get_parser(prog_name)
        parser.add_argument('cidr', metavar='<cidr>',
                            help="Cidr of the new network")
        parser.add_argument('--name', metavar='<name>',
                            help="Name of the new securitygroup")
        parser.add_argument('--is-admin', metavar='<true/false>',
                            default=False,
                            help="")
        parser.add_argument('--gateway-ip', metavar='<x.x.x.x>',
                            help="Gateway ip address of the new network")
        parser.add_argument('--dns-nameserver', metavar='<x.x.x.x>',
                            dest='dns_nameservers', action='append',
                            help=("DNS server for the new network "
                                 "(Can be repeated)"))
        parser.add_argument('--ext-router-id', metavar='<router-id>',
                            help="Router id the new network connects to")

        return parser

    def take_action(self, parsed_args):
        network = self.client.networks.create(self.gid,
                                              parsed_args.cidr,
                                              parsed_args.name,
                                              parsed_args.is_admin,
                                              parsed_args.gateway_ip,
                                              parsed_args.dns_nameservers,
                                              parsed_args.ext_router_id)
        return _make_print_data(
            network.network_id,
            network.name,
            network.neutron_network_id,
            network.is_admin,
            network.cidr,
            network.ext_router_id,
            network.gid,
            network.user_id,
            network.project_id
        )


class DeleteNetwork(Command):
    """
    Delete the specified network.
    """
    def __init__(self, app, app_args):
        super(DeleteNetwork, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(DeleteNetwork, self).get_parser(prog_name)
        parser.add_argument('network_id', metavar='<network-id>',
                            help="Network ID")
        return parser

    def take_action(self, parsed_args):
        self.client.networks.delete(self.gid,
                                    parsed_args.network_id)
