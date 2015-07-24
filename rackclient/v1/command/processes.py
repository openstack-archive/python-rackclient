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


class PS(Lister):
    """
    Print a list of all processes in the specified group.
    """
    def __init__(self, app, app_args):
        super(PS, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def take_action(self, parsed_args):
        processes = self.client.processes.list(self.gid)

        def _make_command(process):
            p_args = process.args
            p_args.pop('gid')
            p_args.pop('pid')
            p_args.pop('ppid', None)
            p_args.pop('proxy_ip', None)
            p_args.pop('rackapi_ip', None)

            cmd = process.name
            for k, v in sorted(p_args.items()):
                cmd += ' --' + k + ' ' + v

            return cmd

        return (
            ('pid', 'ppid', 'command'),
            ((p.pid, p.ppid, _make_command(p)) for p in processes)
        )


def _make_print_data(pid, ppid, name, nova_instance_id, nova_flavor_id,
                     glance_image_id, keypair_id, securitygroup_ids, networks,
                     userdata, args, app_status, gid, user_id, project_id,
                     status=None):
    columns = ['pid', 'ppid', 'name', 'nova_instance_id', 'nova_flavor_id',
               'glance_image_id', 'keypair_id', 'securitygroup_ids',
               'networks', 'userdata', 'args', 'app_status', 'gid', 'user_id',
               'project_id']
    data = [pid, ppid, name, nova_instance_id, nova_flavor_id,
            glance_image_id, keypair_id, securitygroup_ids, networks,
            userdata, args, app_status, gid, user_id, project_id]

    if status is not None:
        columns.append('status')
        data.append(status)

    return columns, data


class Show(ShowOne):
    """
   Show details about the given process.
    """
    def __init__(self, app, app_args):
        super(Show, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)

        parser.add_argument('pid', metavar='<pid>',
                            help="process ID")
        return parser

    def take_action(self, parsed_args):
        process = self.client.processes.get(self.gid, parsed_args.pid)

        sg_ids = process.securitygroup_ids
        if sg_ids:
            sg_ids = ','.join(sg_ids)

        process_args = process.args
        if process_args:
            s = ''
            for k, v in sorted(process_args.items()):
                s += k + '=' + v + '\n'
            process_args = s.rstrip('\n')

        return _make_print_data(
            process.pid,
            process.ppid,
            process.name,
            process.nova_instance_id,
            process.nova_flavor_id,
            process.glance_image_id,
            process.keypair_id,
            sg_ids,
            process.networks,
            process.userdata,
            process_args,
            process.app_status,
            process.gid,
            process.user_id,
            process.project_id,
            process.status
        )


class Boot(ShowOne):
    """
    Boot a process.
    """
    def __init__(self, app, app_args):
        super(Boot, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(Boot, self).get_parser(prog_name)

        parser.add_argument('--ppid', metavar='<ppid>',
                            help="ID of a parent process")
        parser.add_argument('--name', metavar='<name>',
                            help="Name of the new process")
        parser.add_argument('--flavor', metavar='<flavor-id>',
                            help="ID of a flavor that is provided by Nova")
        parser.add_argument('--image', metavar='<image-id>',
                            help="ID of a image that is provided by Glance")
        parser.add_argument('--keypair', metavar='<keypair-id>',
                            help="Keypair ID")
        parser.add_argument('--securitygroup', metavar='<securitygroup-id>',
                            dest='securitygroup_ids', action='append',
                            default=[],
                            help="Securitygroup ID (Can be repeated)")
        parser.add_argument('--floating_network', metavar='<network-id>',
                            dest='floating_networks', action='append',
                            default=[],
                            help="Network ID. A floating IP address will be "
                                 "associated with a new process's port that "
                                  "is on this network (Can be repeated)")
        parser.add_argument('--userdata', metavar='</file/path>',
                            help="Userdata file path")
        parser.add_argument('--args', metavar='<key1=value1,key2=value2,...>',
                            type=utils.keyvalue_to_dict,
                            help=("Key-value pairs to be passed to "
                                  "metadata server"))

        return parser

    def take_action(self, parsed_args):
        userdata = None
        if parsed_args.userdata:
            try:
                userdata = open(parsed_args.userdata)
            except IOError:
                raise exceptions.CommandError(
                    "Can't open '%s'" % parsed_args.userdata)

        process = self.client.processes.create(
            gid=self.gid,
            ppid=parsed_args.ppid,
            name=parsed_args.name,
            nova_flavor_id=parsed_args.flavor,
            glance_image_id=parsed_args.image,
            keypair_id=parsed_args.keypair,
            securitygroup_ids=parsed_args.securitygroup_ids,
            floating_networks=parsed_args.floating_networks,
            userdata=userdata,
            args=parsed_args.args)

        sg_ids = process.securitygroup_ids
        if sg_ids:
            sg_ids = ','.join(sg_ids)

        process_args = process.args
        if process_args:
            s = ''
            for k, v in sorted(process_args.items()):
                s += k + '=' + v + '\n'
            process_args = s.rstrip('\n')

        return _make_print_data(
            process.pid,
            process.ppid,
            process.name,
            process.nova_instance_id,
            process.nova_flavor_id,
            process.glance_image_id,
            process.keypair_id,
            sg_ids,
            process.networks,
            process.userdata,
            process_args,
            process.app_status,
            process.gid,
            process.user_id,
            process.project_id,
        )


class Kill(Command):
    """
    Delete the specified process.
    """
    def __init__(self, app, app_args):
        super(Kill, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(Kill, self).get_parser(prog_name)
        parser.add_argument('pid', metavar='<pid>',
                            help="process ID")
        return parser

    def take_action(self, parsed_args):
        self.client.processes.delete(self.gid, parsed_args.pid)
