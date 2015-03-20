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
from rackclient.lib import RACK_CTX
from rackclient import exceptions
from swiftclient import client as swift_client
from swiftclient import exceptions as swift_exc

import json
import logging
import tempfile


LOG = logging.getLogger(__name__)

SWIFT_PORT = 8080


def _get_swift_client():
    if RACK_CTX.fs_endpoint:
        try:
            d = json.loads(RACK_CTX.fs_endpoint)
            credentials = {
                "user": d["os_username"],
                "key": d["os_password"],
                "tenant_name": d["os_tenant_name"],
                "authurl": d["os_auth_url"],
                "auth_version": "2"
            }
            return swift_client.Connection(**credentials)
        except (ValueError, KeyError):
            msg = "The format of fs_endpoint is invalid."
            raise exceptions.InvalidFSEndpointError(msg)
    else:
        authurl = "http://%s:%d/auth/v1.0" % (RACK_CTX.proxy_ip, SWIFT_PORT)

    credentials = {
        "user": "rack:admin",
        "key": "admin",
        "authurl": authurl
    }
    swift = swift_client.Connection(**credentials)
    authurl, token = swift.get_auth()

    return swift_client.Connection(preauthurl=authurl, preauthtoken=token)


def listdir(directory):
    swift = _get_swift_client()
    directory = directory.strip('/')

    files = []
    try:
        objects = swift.get_container(directory)[1]
        for o in objects:
            file_path = '/' + directory + '/' + o['name']
            files.append(File(file_path))
    except swift_exc.ClientException as e:
        if e.http_status == 404:
            msg = "Directory '%s' does not exist." % directory
            raise exceptions.InvalidDirectoryError(msg)
        else:
            raise exceptions.FileSystemAccessError()

    return files


class File(object):

    def __init__(self, file_path, mode="r"):
        self.path = file_path
        self.file = None
        if mode not in ('r', 'w'):
            raise ValueError(
                "mode must be 'r' or 'w', not %s" % mode)
        else:
            self.mode = mode

    def get_name(self):
        return self.path.strip('/').split('/', 1)[1]

    def get_directory(self):
        return self.path.strip('/').split('/', 1)[0]

    def load(self, chunk_size=None):
        if self.file:
            return

        if self.mode == 'r':
            self.file = tempfile.TemporaryFile()
            swift = _get_swift_client()

            try:
                _, contents = swift.get_object(self.get_directory(),
                                               self.get_name(), chunk_size)
                if chunk_size:
                    for c in contents:
                        self.file.write(c)
                else:
                    self.file.write(contents)
                self.file.flush()
                self.file.seek(0)
            except swift_exc.ClientException as e:
                if e.http_status == 404:
                    msg = "File '%s' does not exist." % self.path
                    raise exceptions.InvalidFilePathError(msg)
                else:
                    raise exceptions.FileSystemAccessError()

    def write(self, *args, **kwargs):
        if not self.file:
            self.file = tempfile.TemporaryFile()

        self.file.write(*args, **kwargs)

    def close(self):
        if self.mode == 'w':
            swift = _get_swift_client()

            try:
                swift.put_container(self.get_directory())
                self.file.seek(0)
                swift.put_object(self.get_directory(), self.get_name(),
                                 self.file)
            except swift_exc.ClientException as e:
                if e.http_status == 404:
                    msg = ("Directory '%s' does not exist. "
                           "The file object will be closed."
                           % self.get_directory())
                    raise exceptions.InvalidDirectoryError(msg)
                else:
                    msg = ("Could not save the file to the file system. "
                           "The file object will be closed.")
                    raise exceptions.FileSystemAccessError(msg)
            finally:
                self.file.close()

        self.file.close()

    def __getattr__(self, name):
        if self.file:
            return getattr(self.file, name)
        else:
            raise AttributeError("%s instance has no attribute '%s'",
                                 self.__class__.__name__, name)
