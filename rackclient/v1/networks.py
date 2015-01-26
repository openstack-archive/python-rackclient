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
import netaddr
from rackclient import exceptions
from rackclient.openstack.common import strutils
from rackclient.v1 import base


class Network(base.Resource):

    def __repr__(self):
        return "<Network: %s>" % self.name


class NetworkManager(base.Manager):

    resource_class = Network

    def list(self, gid):
        """
        Get a list of all networks in the specified group.

        :param gid: ID of the group.
        :rtype: list of Network.
        """
        return self._list("/groups/%s/networks" % gid, "networks")

    def get(self, gid, network_id):
        """
        Get a network.

        :param gid: ID of the group.
        :param network_id: ID of the network to get.
        :rtype: Network.
        """
        return self._get("/groups/%s/networks/%s" % (gid, network_id), "network")

    def create(self, gid, cidr, name=None, is_admin=False, gateway=None, dns_nameservers=None, ext_router_id=None):
        """
        Create a network.

        :param gid: ID of the group.
        :param cidr: CIDR of the new network.
        :param name: Name of the new network.
        :param is_admin: is_admin.
        :param gateway: Gateway ip address of the new network.
        :param list dns_nameservers: List of DNS servers for the new network.
        :param ext_router_id: Router id the new network connect to.
        """
        def _is_valid_cidr(address):
            try:
                netaddr.IPNetwork(address)
            except netaddr.AddrFormatError:
                return False

            ip_segment = address.split('/')
            if (len(ip_segment) <= 1 or
                    ip_segment[1] == ''):
                return False

            return True

        if not _is_valid_cidr(cidr):
                raise exceptions.CommandError("cidr must be a CIDR.")

        if is_admin:
            try:
                is_admin = strutils.bool_from_string(is_admin, True)
            except Exception:
                raise exceptions.CommandError("is_admin must be a boolean.")

        if gateway and not netaddr.valid_ipv4(gateway):
            raise exceptions.CommandError("gateway must be a IP address")

        if dns_nameservers is not None and not isinstance(dns_nameservers, list):
            raise exceptions.CommandError("dns_nameservers must be a list")

        body = {
            "network": {
                "cidr": cidr,
                "name": name,
                "is_admin": is_admin,
                "gateway": gateway,
                "dns_nameservers": dns_nameservers,
                "ext_router_id": ext_router_id
            }
        }
        return self._create("/groups/%s/networks" % gid, body, "network")

    def delete(self, gid, network_id):
        """
        Delete a network.
        
        :param gid: ID of the group.
        :param network_id: ID of the network to delete.
        """
        self._delete("/groups/%s/networks/%s" % (gid, network_id))
