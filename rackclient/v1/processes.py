import base64
from rackclient import exceptions
from rackclient.v1 import base


class Process(base.Resource):

    def __repr__(self):
        return "<Process: %s>" % self.name


class ProcessManager(base.Manager):

    resource_class = Process

    def list(self, gid):
        return self._list("/groups/%s/processes" % gid, "processes")

    def get(self, gid, pid):
        return self._get("/groups/%s/processes/%s" % (gid, pid), "process")

    def create(self, gid, ppid=None, **kwargs):
        '''
        Create a process.

        If you give a ppid(Parent process ID),
        all other parameters will be inherited to its child process,
        but you can override them.

        Parameters in kwargs:

        :param name: string
        :param nova_flavor_id: string
        :param glance_image_id: string
        :param keypair_id: string
        :param securitygroup_ids: a list of strings
        :param userdata: file type object or string
        :param dict args: a dict of key-value pairs to be stored as metadata
        '''

        securitygroup_ids = kwargs.get('securitygroup_ids')
        if securitygroup_ids is not None and not isinstance(securitygroup_ids, list):
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
        body = {
            "process": {
                "app_status": app_status
            }
        }
        self._update("/groups/%s/processes/%s" % (gid, pid), body, "process")

    def delete(self, gid, pid):
        self._delete("/groups/%s/processes/%s" % (gid, pid))