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


class Montecarlo(ShowOne):
    """
    The application to approximate the circular constant
    with the Monte Carlo method
    """
    def __init__(self, app, app_args):
        super(Montecarlo, self).__init__(app, app_args)

        # When the help command is called,
        # the type of 'app_args' is list.
        if isinstance(app_args, argparse.Namespace):
            self.client = client.Client(app_args.rack_api_version,
                                        rack_url=app_args.rack_url,
                                        http_log_debug=app_args.debug)
            self.gid = app_args.gid

    def get_parser(self, prog_name):
        parser = super(Montecarlo, self).get_parser(prog_name)

        parser.add_argument('--msg_limit_time', metavar='<integer>',
                            default=300, type=int,
                            help="Parent waits for notifications of "
                                 "preparation completion from children "
                                 "until the timer reaches to msg_limit_time "
                                 "seconds")
        parser.add_argument('--noterm', metavar='<true/false>',
                            default=False,
                            help="(Intended for debugging) "
                                 "If true, all processes won't be deleted")
        parser.add_argument('--image', metavar='<image-id>',
                            required=True,
                            help="(Required) ID of the montecarlo image")
        parser.add_argument('--flavor', metavar='<flavor-id>',
                            required=True,
                            help="(Required) ID of a flavor")
        parser.add_argument('--trials', metavar='<integer>',
                            required=True, type=int,
                            help="(Required) The number of trials in a "
                                 "simulation")
        parser.add_argument('--workers', metavar='<integer>',
                            required=True, type=int,
                            help="(Required) The number of workers that "
                                 "will be launched")
        parser.add_argument('--stdout', metavar='</file/path>',
                            required=True,
                            help="(Required) File path on Swift to output "
                                 "the simulation report to")
        return parser

    def take_action(self, parsed_args):
        options = {
            "trials": parsed_args.trials,
            "workers": parsed_args.workers,
            "stdout": parsed_args.stdout,
            "msg_limit_time": parsed_args.msg_limit_time,
            "noterm": parsed_args.noterm
        }

        process = self.client.processes.create(
                        self.gid, name="montecarlo",
                        nova_flavor_id=parsed_args.flavor,
                        glance_image_id=parsed_args.image,
                        args=options)

        process_args = process.args
        process_args.pop('gid')
        process_args.pop('pid')
        process_args.pop('ppid', None)
        process_args.pop('proxy_ip', None)
        process_args.pop('rackapi_ip', None)

        cmd = process.name
        for k, v in sorted(process_args.items()):
            cmd += ' --' + k + ' ' + v

        columns = ['pid', 'ppid', 'cmd']
        data = [process.pid, process.ppid, cmd]

        return columns, data
