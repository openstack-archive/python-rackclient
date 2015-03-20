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


class Securitygroup(base.Resource):

    def __repr__(self):
        return "<Securitygroup: %s>" % self.name


class SecuritygroupManager(base.Manager):

    resource_class = Securitygroup

    def list(self, gid):
        """
        Get a list of all securitygroups in the specified group.

        :param gid: ID of the group.
        :rtype: list of Securitygroup.
        """
        return self._list("/groups/%s/securitygroups" % gid, "securitygroups")

    def get(self, gid, securitygroup_id):
        """
        Get a securitygroup.

        :param gid: ID of the group.
        :param securitygroup_id: ID of the securitygroup to get.
        :rtype: Securitygroup.
        """
        return self._get("/groups/%s/securitygroups/%s" %
                         (gid, securitygroup_id), "securitygroup")

    def create(self, gid, name=None, is_default=False,
               securitygroup_rules=None):
        """
        Create a securitygroup.

        :param gid: ID of the group.
        :param name: Name of the securitygroup.
        :param is_default: Set to the default securitygroup of the group.
        :param list securitygroup_rules: List of rules of the securitygroup.
        """
        try:
            is_default = strutils.bool_from_string(is_default, True)
        except Exception:
            raise exceptions.CommandError("is_default must be a boolean.")

        if securitygroup_rules is not None:
            if not isinstance(securitygroup_rules, list):
                raise exceptions.CommandError(
                    "securitygroup_rules must be a list")

        body = {
            "securitygroup": {
                "name": name,
                "is_default": is_default,
                "securitygrouprules": securitygroup_rules
            }
        }
        return self._create("/groups/%s/securitygroups" %
                            gid, body, "securitygroup")

    def update(self, gid, securitygroup_id, is_default=False):
        """
        Update status of securitygroup.

        :param gid: ID of the group.
        :param securitygroup_id: ID of the securitygroup to update.
        :param is_default: Set to the default securitygroup of the group.
        """
        try:
            is_default = strutils.bool_from_string(is_default, True)
        except Exception:
            raise exceptions.CommandError("is_default must be a boolean.")

        body = {
            "securitygroup": {
                "is_default": is_default,
            }
        }
        return self._update("/groups/%s/securitygroups/%s" %
                            (gid, securitygroup_id), body, "securitygroup")

    def delete(self, gid, securitygroup_id):
        """
        Delete a securitygroup.

        :param gid: ID of the group.
        :param securitygroup_id: ID of the securitygroup to delete.
        """
        self._delete("/groups/%s/securitygroups/%s" % (gid, securitygroup_id))
