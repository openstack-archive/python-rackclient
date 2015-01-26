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
from rackclient import exceptions
from rackclient.openstack.common import strutils
from rackclient.v1 import base


class Keypair(base.Resource):

    def __repr__(self):
        return "<Keypair: %s>" % self.name


class KeypairManager(base.Manager):

    resource_class = Keypair

    def list(self, gid):
        """
        Get a list of all keypairs in the specified group.

        :param gid: ID of the group.
        :rtype: list of Keypair.
        """
        return self._list("/groups/%s/keypairs" % gid, "keypairs")

    def get(self, gid, keypair_id):
        """
        Get a keypair.

        :param gid: ID of the group.
        :param keypair_id: ID of the keypair to get.
        :rtype: Keypair.
        """
        return self._get("/groups/%s/keypairs/%s" % (gid, keypair_id), "keypair")

    def create(self, gid, name=None, is_default=False):
        """
        Create a keypair.

        :param gid: ID of the group.
        :param name: Name of the keypair.
        :param is_default: Set to the default keypair of the group.
        """
        try:
            is_default = strutils.bool_from_string(is_default, True)
        except Exception:
            raise exceptions.CommandError("is_default must be a boolean.")

        body = {
            "keypair": {
                "name": name,
                "is_default": is_default
            }
        }
        return self._create("/groups/%s/keypairs" % gid, body, "keypair")

    def update(self, gid, keypair_id, is_default):
        """
        Update the status of keypair.

        :param gid: ID of the group.
        :param keypair_id: ID of the keypair to update.
        :param is_default: Set to the default keypair of the group.
        """
        try:
            is_default = strutils.bool_from_string(is_default, True)
        except Exception:
            raise exceptions.CommandError("is_default must be a boolean.")

        body = {
            "keypair": {
                "is_default": is_default
            }
        }
        return self._update("/groups/%s/keypairs/%s" % (gid, keypair_id), body, "keypair")

    def delete(self, gid, keypair_id):
        """
        Delete a keypair.

        :param gid: ID of the group.
        :param keypair_id: ID of the keypair to delete.
        """
        self._delete("/groups/%s/keypairs/%s" % (gid, keypair_id))
