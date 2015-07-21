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
from swiftclient import exceptions as swift_exc

from mock import patch
from rackclient.tests import utils
from rackclient.lib.syscall.default import file as rackfile
from rackclient.exceptions import InvalidFSEndpointError
from rackclient.exceptions import InvalidDirectoryError
from rackclient.exceptions import InvalidFilePathError
from rackclient.exceptions import FileSystemAccessError


class FileTest(utils.LibTestCase):

    def target_context(self):
        return "syscall.default.file"

    def setUp(self):
        super(FileTest, self).setUp()
        patcher = patch('swiftclient.client.Connection', autospec=True)
        self.addCleanup(patcher.stop)
        self.mock_conn = patcher.start()
        self.mock_conn.return_value.get_auth.return_value = 'fake', 'fake'

    def test_get_swift_client(self):
        self.mock_conn.return_value.get_auth.return_value = 'fake', 'fake'
        rackfile._get_swift_client()
        expected = {
            "user": "rack:admin",
            "key": "admin",
            "authurl": "http://10.0.0.2:8080/auth/v1.0"
        }
        self.mock_conn.assert_any_call(**expected)
        self.mock_conn.assert_any_call(preauthurl='fake', preauthtoken='fake')

    def test_get_swift_client_fs_endpoint(self):
        endpoint = ('{"os_username": "user", '
                    '"os_password": "password", '
                    '"os_tenant_name": "tenant", '
                    '"os_auth_url": "http://www.example.com:5000/v2.0"}')
        self.mock_RACK_CTX.fs_endpoint = endpoint
        rackfile._get_swift_client()
        expected = {
            "user": 'user',
            "key": 'password',
            "tenant_name": 'tenant',
            "authurl": 'http://www.example.com:5000/v2.0',
            "auth_version": "2"
        }
        self.mock_conn.assert_any_call(**expected)

    def test_get_swift_client_invalid_fs_endpoint_error(self):
        self.mock_RACK_CTX.fs_endpoint = 'invalid'
        self.assertRaises(InvalidFSEndpointError, rackfile._get_swift_client)

    def test_listdir(self):
        self.mock_conn.return_value.get_container.return_value = \
            None, [{'name': 'file1'}, {'name': 'file2'}]
        files = rackfile.listdir('/dir')

        self.mock_conn.return_value.get_container.assert_called_with('dir')
        self.assertEqual('/dir/file1', files[0].path)
        self.assertEqual('/dir/file2', files[1].path)

    def test_listdir_invalid_directory_error(self):
        self.mock_conn.return_value.get_container.side_effect = \
            swift_exc.ClientException('', http_status=404)
        self.assertRaises(InvalidDirectoryError, rackfile.listdir, 'dir')

    def test_listdir_filesystem_error(self):
        self.mock_conn.return_value.get_container.side_effect = \
            swift_exc.ClientException('', http_status=500)
        self.assertRaises(FileSystemAccessError, rackfile.listdir, 'dir')

    def test_file_read_mode(self):
        self.mock_conn.return_value.get_object.return_value = \
            None, 'example text'
        f = rackfile.File('/dir1/dir2/file.txt')
        f.load()

        self.mock_conn.return_value.get_object.assert_called_with(
                                                        'dir1',
                                                        'dir2/file.txt', None)
        self.assertEqual('example text', f.read())

        f.load()
        call_count = self.mock_conn.return_value.get_object.call_count
        self.assertEqual(1, call_count)

        f.close()

    def test_file_read_mode_with_chunk_size(self):
        def _content():
            for i in ['11111111', '22222222']:
                yield i

        self.mock_conn.return_value.get_object.return_value = \
            None, _content()
        f = rackfile.File('/dir1/dir2/file.txt')
        f.load(8)

        self.mock_conn.return_value.get_object.assert_called_with(
                                                        'dir1',
                                                        'dir2/file.txt', 8)
        self.assertEqual('1111111122222222', f.read())
        f.close()

    def test_file_load_invalid_file_path_error(self):
        self.mock_conn.return_value.get_object.side_effect = \
            swift_exc.ClientException('', http_status=404)
        f = rackfile.File('/dir1/dir2/file.txt')
        self.assertRaises(InvalidFilePathError, f.load)

    def test_file_load_filesystem_error(self):
        self.mock_conn.return_value.get_object.side_effect = \
            swift_exc.ClientException('')
        f = rackfile.File('/dir1/dir2/file.txt')
        self.assertRaises(FileSystemAccessError, f.load)

    def test_file_write_mode(self):
        f = rackfile.File('/dir1/dir2/file.txt', mode='w')
        f.write('example text')
        f.close()

        self.mock_conn.return_value.put_container.assert_called_with('dir1')
        self.mock_conn.return_value.put_object.assert_called_with(
            'dir1', 'dir2/file.txt', f.file)

    def test_file_close_invalid_directory_error(self):
        self.mock_conn.return_value.put_object.side_effect = \
            swift_exc.ClientException('', http_status=404)
        f = rackfile.File('/dir1/dir2/file.txt', mode='w')
        f.write('example text')
        self.assertRaises(InvalidDirectoryError, f.close)

    def test_file_close_invalid_filesystem_error(self):
        self.mock_conn.return_value.put_container.side_effect = \
            swift_exc.ClientException('')
        f = rackfile.File('/dir1/dir2/file.txt', mode='w')
        f.write('example text')
        self.assertRaises(FileSystemAccessError, f.close)

    def test_file_attriute_error(self):
        f = rackfile.File('/dir1/dir2/file.txt')
        try:
            f.invalid
        except AttributeError:
            pass
        else:
            self.fail("Expected 'AttributeError'.")

    def test_file_invalid_mod(self):
        self.assertRaises(ValueError, rackfile.File, '/dir1/dir2/file.txt',
                          'invalid_mode')
