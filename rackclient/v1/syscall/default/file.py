import json
import tempfile
from rackclient import process_context
from swiftclient import client as swift_client

PCTXT = process_context.PCTXT
SWIFT_PORT = 8080


def _get_swift_client(v1_authurl=None):
    if v1_authurl:
        authurl = v1_authurl
    elif PCTXT.fs_endpoint:
        d = json.loads(PCTXT.fs_endpoint)
        credentials = {
            "user": d["os_username"],
            "key": d["os_password"],
            "tenant_name": d["os_tenant_name"],
            "authurl": d["os_auth_url"],
            "auth_version": "2"
        }
        return swift_client.Connection(**credentials)
    else:
        authurl = "http://" + ':'.join([PCTXT.proxy_ip, str(SWIFT_PORT)]) + "/auth/v1.0"

    credentials = {
        "user": "rack:admin",
        "key": "admin",
        "authurl": authurl
    }
    swift = swift_client.Connection(**credentials)
    authurl, token = swift.get_auth()
    return swift_client.Connection(preauthurl=authurl, preauthtoken=token)


def get_objects(container, url=None):
    swift = _get_swift_client(url)
    objects = []
    for f in swift.get_container(container)[1]:
        objects.append(f["name"])
    return objects


def load(container, name, chunk_size=None, url=None):
    swift = _get_swift_client(url)
    return swift.get_object(container, name, resp_chunk_size=chunk_size)[1]


def save(container, name, data, url=None):
    swift = _get_swift_client(url)
    try:
        swift.put_container(container)
    except:
        pass
    return swift.put_object(container, name, data)


class File(object):
    def __init__(self, container, name, mode="r", chunk_size=102400000, url=None):
        self.container = container
        self.name = name
        self.mode = mode
        self.url = url
        self.file = tempfile.TemporaryFile()
        if self.mode == 'r':
            self._rsync(chunk_size=chunk_size)
        elif self.mode == 'w':
            pass
        else:
            raise ValueError("mode string must begin with 'r' or 'w', not %s" % mode)

    def _load(self, chunk_size=None):
        return load(self.container, self.name, chunk_size=chunk_size, url=self.url)

    def _rsync(self, chunk_size=None):
        for c in self._load(chunk_size=chunk_size):
            self.file.write(c)
        self.file.flush()
        self.file.seek(0)

    def _save(self):
        return save(self.container, self.name, self.file, url=self.url)

    def close(self):
        if self.mode == "w":
            self.file.seek(0)
            self._save()
        self.file.close()

    def __getattr__(self, name):
        return getattr(self.file, name)
