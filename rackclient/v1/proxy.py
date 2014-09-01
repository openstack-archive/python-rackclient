import base64
from rackclient import exceptions
from rackclient.v1 import base


class Proxy(base.Resource):

    def __repr__(self):
        return "<Proxy: %s>" % self.name


class ProxyManager(base.Manager):

    resource_class = Proxy

    def get(self, gid):
        return self._get("/groups/%s/proxy" % (gid), "proxy")

    def create(self, gid, name=None, nova_flavor_id=None, glance_image_id=None, keypair_id=None,
               securitygroup_ids=None, userdata=None, args=None):
        """
        Create a RACK proxy.

        :param gid: string
        :param name: string
        :param nova_flavor_id: string
        :param glance_image_id: string
        :param keypair_id: string
        :param securitygroup_ids: a list of strings
        :param userdata: file type object or string
        :param dict args: a dict of key-value pairs to be stored as metadata
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
        Update parameters of a RACK proxy.

        :param gid: string
        :param shm_endpoint: A endpoint of Shared memory. Arbitrary string value.
        :param ipc_endpoint: A endpoint of IPC. Arbitrary string value.
        :param fs_endpoint: A endpoint of File System. Arbitrary string value.
        :param app_status: An application layer status of a RACK proxy, assuming 'ACTIVE' or 'ERROR'.
        """

        body = {
            "proxy": {
                "shm_endpoint": shm_endpoint,
                "ipc_endpoint": ipc_endpoint,
                "fs_endpoint": fs_endpoint,
                "app_status": app_status
            }
        }
        self._update("/groups/%s/proxy" % gid, body, "proxy")
