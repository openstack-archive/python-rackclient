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
from rackclient.v1 import base


class Group(base.Resource):

    def __repr__(self):
        return "<Group: %s>" % self.name


class GroupManager(base.Manager):

    resource_class = Group

    def list(self):
        """
        Get a list of all groups.

        :rtype: list of Group.
        """
        return self._list("/groups", "groups")

    def get(self, gid):
        """
        Get a group.

        :param gid: ID of group to get.
        :rtype: Group.
        """
        return self._get("/groups/%s" % gid, "group")

    def _build_body(self, name, description=None):
        return {
            "group": {
                "name": name,
                "description": description if description else None
            }
        }

    def create(self, name, description=None):
        """
        Create a group.

        :param name: Name of the group.
        :param description: Descritpion of the group.
        """
        body = self._build_body(name, description)
        return self._create("/groups", body, "group")

    def update(self, gid, name, description=None):
        """
        Update the name or the description of the group.

        :param gid: ID of the group.
        :param name: Name of the group to update.
        :param description: Description of the group to update.
        """
        body = self._build_body(name, description)
        return self._update("/groups/%s" % gid, body, "group")

    def delete(self, gid):
        """
        Delete a group.
        
        :param gid: ID of the group to delete.
        """
        self._delete("/groups/%s" % gid)
