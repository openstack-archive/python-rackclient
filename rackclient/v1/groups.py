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