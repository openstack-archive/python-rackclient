"""
Command-line interface to the RACK API.
"""

import sys
import argparse
import logging
from oslo.utils import encodeutils
from rackclient.openstack.common.gettextutils import _
from rackclient.openstack.common import cliutils
from rackclient.v1 import shell as shell_v1
from rackclient.v1 import client as client_v1
from rackclient import exceptions

DEFAULT_RACK_API_VERSION = "1"

logger = logging.getLogger(__name__)


class RackShell(object):

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='rack',
            description=__doc__.strip(),
            epilog='See "rack help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
        )

        parser.add_argument(
            '-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS
        )

        parser.add_argument(
            '--version',
            action='version'
        )

        parser.add_argument(
            '-d', '--debug',
            default=False,
            action='store_true',
            help=_("Print debugging output")
        )

        parser.add_argument(
            '--rack-api-version',
            metavar='<rack-api-ver>',
            default=cliutils.env('RACK_API_VERSION',
                default=DEFAULT_RACK_API_VERSION),
            help=_('Accepts only 1, '
                   'defaults to env[RACK_API_VERSION].'))

        parser.add_argument(
            '--rack-url',
            metavar='<rack-url>',
            default=cliutils.env('RACK_URL'),
            help=_('Defaults to env[RACK_URL].'))

        parser.add_argument(
            '--gid',
            metavar='<gid>',
            default=cliutils.env('RACK_GID'),
            help=_('Defaults to env[RACK_GID].'))

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        try:
            actions_module = {
                '1': shell_v1,
            }[version]
        except KeyError:
            actions_module = shell_v1

        self._find_actions(subparsers, actions_module)
        self._find_actions(subparsers, self)

        return parser

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            action_help = desc.strip()
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=action_help,
                description=desc,
                add_help=False,
            )
            subparser.add_argument(
                '-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def setup_debugging(self, debug):
        if not debug:
            return

        streamformat = "%(levelname)s (%(module)s:%(lineno)d) %(message)s"
        logging.basicConfig(level=logging.DEBUG,
                            format=streamformat)

    @cliutils.arg('command', metavar='<subcommand>', nargs='?',
                  help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exceptions.CommandError(
                    _("'%s' is not a valid subcommand") % args.command)
        else:
            self.parser.print_help()

    def main(self, argv):
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.setup_debugging(options.debug)

        subcommand_parser = self.get_subcommand_parser(
            options.rack_api_version)
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        if args.func == self.do_help:
            self.do_help(args)
            return 0

        if not args.rack_url:
            raise exceptions.CommandError(
                _("You must provide an RACK url "
                  "via either --rack-url or env[RACK_URL] "))

        if options.rack_api_version == '1':
            self.cs = client_v1.Client(rack_url=args.rack_url, http_log_debug=options.debug)
        else:
            return 0

        if args.func.func_name[3:].split('_')[0] != 'group' and not args.gid:
            raise exceptions.CommandError(
                _("You must provide a gid "
                  "via either --gid or env[RACK_GID] "))

        args.func(self.cs, args)


def main():
    try:
        argv = [encodeutils.safe_decode(a) for a in sys.argv[1:]]
        RackShell().main(argv)

    except Exception as e:
        logger.debug(e, exc_info=1)
        details = {'name': encodeutils.safe_encode(e.__class__.__name__),
                   'msg': encodeutils.safe_encode(unicode(e))}
        print >> sys.stderr, "ERROR (%(name)s): %(msg)s" % details
        sys.exit(1)
    except KeyboardInterrupt as e:
        print >> sys.stderr, ("Shutting down rackclient")
        sys.exit(1)


if __name__ == "__main__":
    main()
