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
        return self._list("/groups/%s/networks" % gid, "networks")

    def get(self, gid, network_id):
        return self._get("/groups/%s/networks/%s" % (gid, network_id), "network")

    def create(self, gid, cidr, name=None, is_admin=False, gateway=None, dns_nameservers=None, ext_router_id=None):
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

        try:
            is_admin = strutils.bool_from_string(is_admin, True)
        except Exception:
            raise exceptions.CommandError("is_admin must be a boolean.")

        if not netaddr.valid_ipv4(gateway):
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
        self._delete("/groups/%s/networks/%s" % (gid, network_id))