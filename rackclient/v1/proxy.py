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


class Proxy(base.Resource):

    def __repr__(self):
        return "<Proxy: %s>" % self.name


class ProxyManager(base.Manager):

    resource_class = Proxy

    def get(self, gid):
        """
        Get a rack-proxy process information.

        :param gid: ID of the group.
        :rtype: Process
        """
        return self._get("/groups/%s/proxy" % (gid), "proxy")

    def create(self, gid, name=None, nova_flavor_id=None, glance_image_id=None, keypair_id=None,
               securitygroup_ids=None, userdata=None, args=None):
        """
        Create a rack-proxy process.

        :param gid: ID of a group
        :param name: Name of the rack-proxy process
        :param nova_flavor_id: ID of a flavor
        :param glance_image_id: ID of a glance image
        :param keypair_id: ID of a keypair
        :param securitygroup_ids: List of IDs of securitygroups
        :param userdata: file type object or string of script
        :param dict args: Dict of key-value pairs to be stored as metadata
        """

        if securitygroup_ids is not None and not isinstance(securitygroup_ids, list):
            raise exceptions.CommandError("securitygroup_ids must be a list")

        if userdata:
            if hasattr(userdata, 'read'):
                userdata = userdata.read()
            userdata_b64 = base64.b64encode(userdata)

        if args is not None and not isinstance(args, dict):
            raise exceptions.CommandError("args must be a dict")

        body = {
            "proxy": {
                "name": name,
                "nova_flavor_id": nova_flavor_id,
                "glance_image_id": glance_image_id,
                "keypair_id": keypair_id,
                "securitygroup_ids": securitygroup_ids,
                "userdata": userdata_b64 if userdata else userdata,
                "args": args
            }
        }
        return self._create("/groups/%s/proxy" % gid, body, "proxy")

    def update(self, gid, shm_endpoint=None, ipc_endpoint=None, fs_endpoint=None, app_status=None):
        """
        Update parameters of a rack-proxy process.

        :param gid: ID of a group
        :param shm_endpoint: An endpoint of Shared memory. Arbitrary string value.
        :param ipc_endpoint: An endpoint of IPC. Arbitrary string value.
        :param fs_endpoint: An endpoint of File System. Arbitrary string value.
        :param app_status: Application layer status of a rack-proxy process.
        """

        body = {
            "proxy": {
                "shm_endpoint": shm_endpoint,
                "ipc_endpoint": ipc_endpoint,
                "fs_endpoint": fs_endpoint,
                "app_status": app_status
            }
        }
        return self._update("/groups/%s/proxy" % gid, body, "proxy")
