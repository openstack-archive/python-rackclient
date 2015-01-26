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
from rackclient.client import HTTPClient
from rackclient.v1.groups import GroupManager
from rackclient.v1.keypairs import KeypairManager
from rackclient.v1.networks import NetworkManager
from rackclient.v1.processes import ProcessManager
from rackclient.v1.proxy import ProxyManager
from rackclient.v1.securitygroups import SecuritygroupManager


class Client(object):
    """
    Top-level Object to access the rack API.

    Create an rackclient instance::

        >>> from rackclient.v1 import client
        >>> client = client.Client()

    Then call methods on its managers::

        >>> client.processes.list()
        ...
        >>> client.groups.list()
        ...
    """
    def __init__(self, rack_url=None, http_log_debug=False):
        self.rack_url = rack_url
        self.http_log_debug = http_log_debug
        self.groups = GroupManager(self)
        self.keypairs = KeypairManager(self)
        self.securitygroups = SecuritygroupManager(self)
        self.networks = NetworkManager(self)
        self.processes = ProcessManager(self)
        self.proxy = ProxyManager(self)
        self.client = HTTPClient(rack_url, http_log_debug=http_log_debug)
