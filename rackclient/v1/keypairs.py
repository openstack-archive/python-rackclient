from rackclient import exceptions
from rackclient.openstack.common import strutils
from rackclient.v1 import base


class Keypair(base.Resource):

    def __repr__(self):
        return "<Keypair: %s>" % self.name


class KeypairManager(base.Manager):

    resource_class = Keypair

    def list(self, gid):
        return self._list("/groups/%s/keypairs" % gid, "keypairs")

    def get(self, gid, keypair_id):
        return self._get("/groups/%s/keypairs/%s" % (gid, keypair_id), "keypair")

    def create(self, gid, name=None, is_default=False):
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
        self._delete("/groups/%s/keypairs/%s" % (gid, keypair_id))