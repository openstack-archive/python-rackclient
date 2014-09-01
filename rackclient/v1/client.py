from rackclient.client import HTTPClient
from rackclient.v1.groups import GroupManager
from rackclient.v1.keypairs import KeypairManager
from rackclient.v1.networks import NetworkManager
from rackclient.v1.processes import ProcessManager
from rackclient.v1.proxy import ProxyManager
from rackclient.v1.securitygroups import SecuritygroupManager


class Client(object):

    def __init__(self, user, tenant_name, rack_url, http_log_debug=False):
        self.user = user
        self.tenant_name = tenant_name
        self.rack_url = rack_url
        self.http_log_debug = http_log_debug
        self.groups = GroupManager(self)
        self.keypairs = KeypairManager(self)
        self.securitygroups = SecuritygroupManager(self)
        self.networks = NetworkManager(self)
        self.processes = ProcessManager(self)
        self.proxy = ProxyManager(self)
        self.client = HTTPClient(user, tenant_name, rack_url, http_log_debug=http_log_debug)
