Client library for RACK API
=====================

## python-rackcilent

This is a client library for [**RACK**](https://github.com/stackforge/rack) API.
It provides a python API and a command-line tool.

### Install

```
git clone https://github.com/stackforge/python-rackclient.git
cd python-rackclient
pip install -r requirements.txt
python setup.py install
```

## command-line

Once you have rackclient installed, you can use a shell command, `rack`, that interacts with RACK API.

You'll need to provide the endpoint of RACK API.
You can set it with `--rack-url` option or as a environment variable:

```
export RACK_URL=http://example.com:8088/v1
```

Now you are all set.

You'll find complete documentation on the shell by running `rack help` command.

## python API

There's also a python API.
This is a very simple example:

```
from rackclient.v1 import client

# main client object
rack = client.Client(rack_url='http://192.168.100.218:8088/v1')

# create a process group
group = rack.groups.create(name='test-group')

# create a keypair
rack.keypairs.create(gid=group.gid, is_default=True)

# create a securitygroup
rules = [
    {
        "protocol": "tcp",
        "port_range_max": "65535",
        "port_range_min": "1",
        "remote_ip_prefix": "0.0.0.0/0"
    }
]
rack.securitygroups.create(gid=group.gid, is_default=True, securitygroup_rules=rules)

# create a network
rack.networks.create(gid=group.gid, cidr="10.10.10.0/24", dns_nameservers=["8.8.8.8"], ext_router_id="eda01125-8c40-41dd-a694-db7578ed7725")

# boot a rack-proxy
rack.proxy.create(gid=group.gid, nova_flavor_id="2", glance_image_id="42ec5e05-ade9-426d-a70a-fd5e02fcf261")

# boot a process
process = rack.processes.create(gid=group.gid, nova_flavor_id="2", glance_image_id="90d8d31c-6386-4740-8ae5-e8a80b8fc6dd")

# You can access the process's context as object's attribute
print process.gid, process.pid, process.name, ...
```


## RACK Project Resources

* [Wiki](https://wiki.openstack.org/wiki/RACK)
* [Source Code](https://github.com/stackforge/rack)
