import re
import StringIO
import sys
import fixtures
import mock
from testtools import matchers
from rackclient import exceptions
import rackclient.shell
from rackclient.tests import utils

FAKE_ENV = {'RACK_URL': 'http://www.example.com:8088/v1',
            'RACK_GID': '11111111'}

class ShellTest(utils.TestCase):

    def make_env(self, exclude=None, fake_env=FAKE_ENV):
        env = dict((k, v) for k, v in fake_env.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def shell(self, argstr, exitcodes=(0,)):
        orig = sys.stdout
        orig_stderr = sys.stderr
        try:
            sys.stdout = StringIO.StringIO()
            sys.stderr = StringIO.StringIO()
            _shell = rackclient.shell.RackShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertIn(exc_value.code, exitcodes)
        finally:
            stdout = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
            stderr = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = orig_stderr
        return (stdout, stderr)

    def test_help(self):
        required = [
            '.*?^usage: ',
            '.*?^\s+process-show\s+Show details about the given process',
            '.*?^See "rack help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('help')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: ',
            '.*?^Show details about the given process',
            '.*?^positional arguments:',
        ]
        stdout, stderr = self.shell('help process-show')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_no_options(self):
        required = [
            '.*?^usage: ',
            '.*?^\s+process-show\s+Show details about the given process',
            '.*?^See "rack help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_no_url(self):
        required = ('You must provide an RACK url '
                    'via either --rack-url or env[RACK_URL] ')
        self.make_env(exclude='RACK_URL')
        try:
            self.shell('process-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    def test_no_gid(self):
        required = ('You must provide a gid '
                    'via either --gid or env[RACK_GID] ')
        self.make_env(exclude='RACK_GID')
        try:
            self.shell('process-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args[0])
        else:
            self.fail('CommandError not raised')

    @mock.patch('sys.argv', ['rack'])
    @mock.patch('sys.stdout', StringIO.StringIO())
    @mock.patch('sys.stderr', StringIO.StringIO())
    def test_main_noargs(self):
        # Ensure that main works with no command-line arguments
        try:
            rackclient.shell.main()
        except SystemExit:
            self.fail('Unexpected SystemExit')

        # We expect the normal usage as a result
        self.assertIn('Command-line interface to the RACK API',
                      sys.stdout.getvalue())

    @mock.patch('sys.stderr', StringIO.StringIO())
    @mock.patch.object(rackclient.shell.RackShell, 'main')
    def test_main_exception(self, mock_rack_shell):
        mock_rack_shell.side_effect = exceptions.CommandError('error message')
        try:
            rackclient.shell.main()
        except SystemExit as ex:
            self.assertEqual(ex.code, 1)
            self.assertIn('ERROR (CommandError): error message', sys.stderr.getvalue())

    @mock.patch.object(rackclient.shell.RackShell, 'main')
    def test_main_keyboard_interrupt(self, mock_rack_shell):
        mock_rack_shell.side_effect = KeyboardInterrupt()
        try:
            rackclient.shell.main()
        except SystemExit as ex:
            self.assertEqual(ex.code, 1)