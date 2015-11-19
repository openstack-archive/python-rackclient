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

from cliff.show import ShowOne

from rackclient import client


def _make_print_data(pid, ppid, name, nova_instance_id, nova_flavor_id,
                     glance_image_id, keypair_id, securitygroup_ids, networks,
                     userdata, args, app_status, fs_endpoint, ipc_endpoint,
                     shm_endpoint, gid, user_id, project_id, status=None):
    columns = ['pid', 'ppid', 'name', 'nova_instance_id', 'nova_flavor_id',
               'glance_image_id', 'keypair_id', 'securitygroup_ids',
               'networks', 'userdata', 'args', 'app_status', 'fs_endpoint',
               'ipc_endpoint', 'shm_endpoint', 'gid', 'user_id', 'project_id']
    data = [pid, ppid, name, nova_instance_id, nova_flavor_id,
            glance_image_id, keypair_id, securitygroup_ids, networks,
            userdata, args, app_status, fs_endpoint, ipc_endpoint,
            shm_endpoint, gid, user_id, project_id]

    if status is not None:
        columns.append('status')
        data.append(status)

    return columns, data


class ShowProxy(ShowOne):
    """
    Show details about the rack-proxy process.
    """
    def __init__(self, app, app_args):
        super(ShowProxy, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def take_action(self, parsed_args):
        proxy = self.client.proxy.get(self.gid)

        sg_ids = proxy.securitygroup_ids
        if sg_ids:
            sg_ids = ','.join(sg_ids)

        proxy_args = proxy.args
        if proxy_args:
            s = ''
            for k, v in sorted(proxy_args.items()):
                s += k + '=' + v + '\n'
            proxy_args = s.rstrip('\n')

        return _make_print_data(
            proxy.pid,
            proxy.ppid,
            proxy.name,
            proxy.nova_instance_id,
            proxy.nova_flavor_id,
            proxy.glance_image_id,
            proxy.keypair_id,
            sg_ids,
            proxy.networks,
            proxy.userdata,
            proxy_args,
            proxy.app_status,
            proxy.fs_endpoint,
            proxy.ipc_endpoint,
            proxy.shm_endpoint,
            proxy.gid,
            proxy.user_id,
            proxy.project_id,
            proxy.status
        )


class CreateProxy(ShowOne):
    """
    Create a rack-proxy process.
    """
    def __init__(self, app, app_args):
        super(CreateProxy, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(CreateProxy, self).get_parser(prog_name)

        parser.add_argument('--name', metavar='<name>',
                            help="Name of the rack-proxy process")
        parser.add_argument('--keypair', metavar='<keypair-id>',
                            help="Keypair id of the new process uses")
        parser.add_argument('--securitygroup', metavar='<securitygroup-id>',
                            dest='securitygroup', action='append',
                            default=[],
                            help=("Securitygroup id the rack-proxy process "
                                  "belongs to (Can be repeated)"))
        parser.add_argument('--flavor', metavar='<nova-flavor-id>',
                            required=True,
                            help=("(Required) Flavor id of "
                                  "the rack-proxy process"))
        parser.add_argument('--image', metavar='<glance-image-id>',
                            required=True,
                            help=("(Required) Image id that registered "
                                  "on Glance of the rack-proxy process"))

        return parser

    def take_action(self, parsed_args):
        proxy = self.client.proxy.create(
            self.gid,
            name=parsed_args.name,
            nova_flavor_id=parsed_args.flavor,
            glance_image_id=parsed_args.image,
            keypair_id=parsed_args.keypair,
            securitygroup_ids=parsed_args.securitygroup)

        sg_ids = proxy.securitygroup_ids
        if sg_ids:
            sg_ids = ','.join(sg_ids)

        proxy_args = proxy.args
        if proxy_args:
            s = ''
            for k, v in sorted(proxy_args.items()):
                s += k + '=' + v + '\n'
            proxy_args = s.rstrip('\n')

        return _make_print_data(
            proxy.pid,
            proxy.ppid,
            proxy.name,
            proxy.nova_instance_id,
            proxy.nova_flavor_id,
            proxy.glance_image_id,
            proxy.keypair_id,
            sg_ids,
            proxy.networks,
            proxy.userdata,
            proxy_args,
            proxy.app_status,
            proxy.fs_endpoint,
            proxy.ipc_endpoint,
            proxy.shm_endpoint,
            proxy.gid,
            proxy.user_id,
            proxy.project_id,
            proxy.status
        )


class UpdateProxy(ShowOne):
    """
    Update the rack-proxy process.
    """
    def __init__(self, app, app_args):
        super(UpdateProxy, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(UpdateProxy, self).get_parser(prog_name)

        parser.add_argument('--fs-endpoint', metavar='<fs-endpoint>',
                            help="Endpoint of the shared memory service")
        parser.add_argument('--ipc-endpoint', metavar='<ipc-endpoint>',
                            help="Endpoint of the IPC service")
        parser.add_argument('--shm-endpoint', metavar='<shm-endpoint>',
                            help="Endpoint of the file system service")
        parser.add_argument('--app-status', metavar='<app-status>',
                            help="Application layer status of the proxy")

        return parser

    def take_action(self, parsed_args):
        proxy = self.client.proxy.update(self.gid,
                                         shm_endpoint=parsed_args.shm_endpoint,
                                         ipc_endpoint=parsed_args.ipc_endpoint,
                                         fs_endpoint=parsed_args.fs_endpoint,
                                         app_status=parsed_args.app_status)

        sg_ids = proxy.securitygroup_ids
        if sg_ids:
            sg_ids = ','.join(sg_ids)

        proxy_args = proxy.args
        if proxy_args:
            s = ''
            for k, v in sorted(proxy_args.items()):
                s += k + '=' + v + '\n'
            proxy_args = s.rstrip('\n')

        return _make_print_data(
            proxy.pid,
            proxy.ppid,
            proxy.name,
            proxy.nova_instance_id,
            proxy.nova_flavor_id,
            proxy.glance_image_id,
            proxy.keypair_id,
            sg_ids,
            proxy.networks,
            proxy.userdata,
            proxy_args,
            proxy.app_status,
            proxy.fs_endpoint,
            proxy.ipc_endpoint,
            proxy.shm_endpoint,
            proxy.gid,
            proxy.user_id,
            proxy.project_id
        )
