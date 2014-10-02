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
        return self._list("/groups", "groups")

    def get(self, gid):
        return self._get("/groups/%s" % gid, "group")

    def _build_body(self, name, description=None):
        return {
            "group": {
                "name": name,
                "description": description if description else None
            }
        }

    def create(self, name, description=None):
        body = self._build_body(name, description)
        return self._create("/groups", body, "group")

    def update(self, gid, name, description=None):
        body = self._build_body(name, description)
        return self._update("/groups/%s" % gid, body, "group")

    def delete(self, gid):
        self._delete("/groups/%s" % gid)