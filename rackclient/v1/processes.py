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
import base64
from rackclient import exceptions
from rackclient.v1 import base


class Process(base.Resource):

    def __repr__(self):
        return "<Process: %s>" % self.name


class ProcessManager(base.Manager):

    resource_class = Process

    def list(self, gid):
        """
        Get a list of all processes in the specified group.

        :param gid: ID of the group.
        :rtype: list of Process.
        """
        return self._list("/groups/%s/processes" % gid, "processes")

    def get(self, gid, pid):
        """
        Get a server.

        :param gid: ID of the group.
        :param pid: ID of the process to get.
        :rtype: Process.
        """
        return self._get("/groups/%s/processes/%s" % (gid, pid), "process")

    def create(self, gid, ppid=None, **kwargs):
        """
        Create a process.

        If you give a ppid(Parent process ID),
        all other parameters will be inherited to its child process,
        but you can override them.

        Parameters in kwargs:

        :param name: Name of the new process
        :param nova_flavor_id: ID of a flavor
        :param glance_image_id: ID of a glance image
        :param keypair_id: ID of a keypair
        :param list securitygroup_ids: List of IDs of securitygroups
        :param userdata: file type object or string of script
        :param dict args: Dict of key-value pairs to be stored as metadata
        """

        securitygroup_ids = kwargs.get('securitygroup_ids')
        if securitygroup_ids is not None and not isinstance(
                securitygroup_ids, list):
            raise exceptions.CommandError("securitygroup_ids must be a list")

        userdata = kwargs.get('userdata')
        if userdata:
            if hasattr(userdata, 'read'):
                userdata = userdata.read()
            userdata_b64 = base64.b64encode(userdata)

        args = kwargs.get('args')
        if args is not None and not isinstance(args, dict):
            raise exceptions.CommandError("args must be a dict")

        body = {
            "process": {
                "ppid": ppid,
                "name": kwargs.get('name'),
                "nova_flavor_id": kwargs.get('nova_flavor_id'),
                "glance_image_id": kwargs.get('glance_image_id'),
                "keypair_id": kwargs.get('keypair_id'),
                "securitygroup_ids": securitygroup_ids,
                "userdata": userdata_b64 if userdata else userdata,
                "args": args
            }
        }
        return self._create("/groups/%s/processes" % gid, body, "process")

    def update(self, gid, pid, app_status):
        """
        Update status of process.

        :param gid: ID of the group.
        :param pid: ID of the process.
        :param app_status: Application layer status of the process.
        """
        body = {
            "process": {
                "app_status": app_status
            }
        }
        return self._update("/groups/%s/processes/%s" %
                            (gid, pid), body, "process")

    def delete(self, gid, pid):
        """
        Delete a process.

        :param gid: ID of the group.
        :param pid: ID of the process to delete.
        """
        self._delete("/groups/%s/processes/%s" % (gid, pid))
