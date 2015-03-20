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
from rackclient import utils


def _make_print_data(securitygroup_id, name, neutron_securitygroup_id,
                     is_default, gid, user_id, project_id, status=None):
    columns = ['securitygroup_id', 'name', 'neutron_securitygroup_id',
               'is_default', 'gid', 'user_id', 'project_id']
    data = [securitygroup_id, name, neutron_securitygroup_id,
            is_default, gid, user_id, project_id]

    if status is not None:
        columns.append('status')
        data.append(status)

    return columns, data


class ListSecuritygroups(Lister):
    """
    Print a list of all security groups in the specified group.
    """
    def __init__(self, app, app_args):
        super(ListSecuritygroups, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def take_action(self, parsed_args):
        securitygroups = self.client.securitygroups.list(self.gid)
        return (
            ('securitygroup_id', 'name', 'is_default', 'status'),
            ((s.securitygroup_id, s.name, s.is_default, s.status)
             for s in securitygroups)
        )


class ShowSecuritygroup(ShowOne):
    """
    Show details about the given security group.
    """
    def __init__(self, app, app_args):
        super(ShowSecuritygroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(ShowSecuritygroup, self).get_parser(prog_name)
        parser.add_argument('securitygroup_id', metavar='<securitygroup-id>',
                            help="Securitygroup ID")
        return parser

    def take_action(self, parsed_args):
        securitygroup = self.client.securitygroups.get(
                            self.gid,
                            parsed_args.securitygroup_id)
        return _make_print_data(
            securitygroup.securitygroup_id,
            securitygroup.name,
            securitygroup.neutron_securitygroup_id,
            securitygroup.is_default,
            securitygroup.gid,
            securitygroup.user_id,
            securitygroup.project_id,
            securitygroup.status,
        )


class CreateSecuritygroup(ShowOne):
    """
    Create a new securitygroup.
    """
    def __init__(self, app, app_args):
        super(CreateSecuritygroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(CreateSecuritygroup, self).get_parser(prog_name)
        parser.add_argument('--name', metavar='<name>',
                            help="Name of the new securitygroup")
        parser.add_argument('--is-default', metavar='<true/false>',
                            default=False,
                            help=("Defaults to the default securitygroup "
                                  "of the group"))
        parser.add_argument('--rule',
                            metavar=("<protocol=tcp|udp|icmp,"
                                     "port_range_max=integer,"
                                     "port_range_min=integer,"
                                     "remote_ip_prefix=cidr,"
                                     "remote_securitygroup_id="
                                     "securitygroup_uuid>"),
                            action='append',
                            type=utils.keyvalue_to_dict,
                            dest='rules',
                            default=[],
                            help=("Securitygroup rules. "
                                  "protocol: Protocol of packet, "
                                  "port_range_max: Starting port range, "
                                  "port_range_min: Ending port range, "
                                  "remote_ip_prefix: CIDR to match on, "
                                  "remote_securitygroup_id: "
                                  "Remote securitygroup id "
                                  "to apply rule. (Can be repeated)"))

        return parser

    def take_action(self, parsed_args):
        securitygroup = self.client.securitygroups.create(
            self.gid,
            parsed_args.name,
            parsed_args.is_default,
            parsed_args.rules)

        return _make_print_data(
            securitygroup.securitygroup_id,
            securitygroup.name,
            securitygroup.neutron_securitygroup_id,
            securitygroup.is_default,
            securitygroup.gid,
            securitygroup.user_id,
            securitygroup.project_id,
        )


class UpdateSecuritygroup(ShowOne):
    """
    Update the specified securitygroup.
    """
    def __init__(self, app, app_args):
        super(UpdateSecuritygroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(UpdateSecuritygroup, self).get_parser(prog_name)
        parser.add_argument('securitygroup_id', metavar='<securitygroup-id>',
                            help="Securitygroup ID")
        parser.add_argument('--is-default', metavar='<true/false>',
                            required=True,
                            help=("Defaults to the default securitygroup "
                                  "of the group"))
        return parser

    def take_action(self, parsed_args):
        securitygroup = self.client.securitygroups.update(
                            self.gid,
                            parsed_args.securitygroup_id,
                            parsed_args.is_default)
        return _make_print_data(
            securitygroup.securitygroup_id,
            securitygroup.name,
            securitygroup.neutron_securitygroup_id,
            securitygroup.is_default,
            securitygroup.gid,
            securitygroup.user_id,
            securitygroup.project_id,
        )


class DeleteSecuritygroup(Command):
    """
    Delete the specified securitygroup.
    """
    def __init__(self, app, app_args):
        super(DeleteSecuritygroup, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(DeleteSecuritygroup, self).get_parser(prog_name)
        parser.add_argument('securitygroup_id', metavar='<securitygroup-id>',
                            help="Securitygroup ID")
        return parser

    def take_action(self, parsed_args):
        self.client.securitygroups.delete(
            self.gid,
            parsed_args.securitygroup_id)
