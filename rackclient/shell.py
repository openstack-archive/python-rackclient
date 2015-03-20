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
import logging
import os
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
import requests

from rackclient import exceptions

VERSION = '1'


class RackShell(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(RackShell, self).__init__(
            description='rack shell',
            version=VERSION,
            command_manager=CommandManager('rack.command'),
        )

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        parser = super(RackShell, self).build_option_parser(
            description, version, argparse_kwargs)

        parser.add_argument(
            '--rack-api-version',
            metavar='<api-verion>',
            default=os.environ.get('RACK_API_VERSION', VERSION),
            help=('Accepts only 1, '
                  'defaults to env[RACK_API_VERSION].')
        )
        parser.add_argument(
            '--rack-url',
            metavar='<rack-url>',
            default=os.environ.get('RACK_URL', ''),
            help='Defaults to env[RACK_URL].'
        )
        parser.add_argument(
            '--gid',
            metavar='<gid>',
            default=os.environ.get('RACK_GID', ''),
            help='Defaults to env[RACK_GID].'
        )

        return parser

    def configure_logging(self):
        super(RackShell, self).configure_logging()

        rlogger = logging.getLogger(requests.__name__)
        rlogger.setLevel(logging.WARNING)

    def initialize_app(self, argv):
        self.check_options()

    def check_options(self):
        if self.options.rack_api_version != '1':
            raise exceptions.CommandError(
                "'rack-api-version' must be 1")

        if not self.options.rack_url:
            raise exceptions.CommandError(
                "You must provide an RACK url "
                "via either --rack-url or env[RACK_URL]")

    def prepare_to_run_command(self, cmd):
        commands = ['HelpCommand', 'ListGroups', 'ShowGroup',
                    'CreateGroup', 'UpdateGroup', 'DeleteGroup',
                    'InitGroup']
        if cmd.__class__.__name__ not in commands:
            if not self.options.gid:
                raise exceptions.CommandError(
                    "You must provide a gid "
                    "via either --gid or env[RACK_GID]")

    def clean_up(self, cmd, result, err):
        if err:
            self.log.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = RackShell()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
