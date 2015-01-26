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
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError

import argparse
import os
import prettytable

from oslo.utils import strutils
from rackclient import exceptions
from rackclient.openstack.common import cliutils
from rackclient.openstack.common.gettextutils import _
from rackclient.v1.syscall.default import signal
from rackclient.v1.syscall.default import file as rackfile


def _keyvalue_to_dict(text):
    try:
        d = {}
        pairs = text.split(',')
        for pair in pairs:
            (k, v) = pair.split('=', 1)
            d.update({k: v})
        return d
    except ValueError:
        msg = "%r is not in the format of key=value" % text
        raise argparse.ArgumentTypeError(msg)


def do_group_list(cs, args):
    """
    Print a list of all groups.
    """
    groups = cs.groups.list()
    fields = ['gid', 'name', 'description', 'status']
    print_list(groups, fields, sortby='gid')


@cliutils.arg(
    'gid',
    metavar='<gid>',
    help=_("Group id"))
def do_group_show(cs, args):
    """
    Show details about the given group.
    """
    group = cs.groups.get(args.gid)
    keypairs = cs.keypairs.list(args.gid)
    securitygroups = cs.securitygroups.list(args.gid)
    networks = cs.networks.list(args.gid)
    processes = cs.processes.list(args.gid)
    try:
        proxy = cs.proxy.get(args.gid)
    except Exception:
        proxy = None
    d = group._info
    d.update({
        "keypairs": ','.join([x.keypair_id for x in keypairs]),
        "securitygroups": ','.join([x.securitygroup_id for x in securitygroups]),
        "networks": ','.join([x.network_id for x in networks]),
        "processes (pid)": ','.join([x.pid for x in processes]),
        "proxy (pid)": proxy.pid if proxy else ''
    })
    print_dict(d)


@cliutils.arg(
    'name',
    metavar='<name>',
    help=_("Name of the new group"))
@cliutils.arg(
    '--description',
    metavar='<description>',
    help=_("Details of the new group"))
def do_group_create(cs, args):
    """
    Create a new group.
    """
    group = cs.groups.create(args.name, args.description)
    d = group._info
    print_dict(d)


@cliutils.arg(
    'gid',
    metavar='<gid>',
    help=_("Group id"))
@cliutils.arg(
    '--name',
    metavar='<name>',
    help=_("Name of the group"))
@cliutils.arg(
    '--description',
    metavar='<description>',
    help=_("Details of the group"))
def do_group_update(cs, args):
    """
    Update the specified group.
    """
    group = cs.groups.update(args.gid, args.name, args.description)
    d = group._info
    print_dict(d)


@cliutils.arg(
    'gid',
    metavar='<gid>',
    help=_("Group id"))
def do_group_delete(cs, args):
    """
    Delete the specified group.
    """
    cs.groups.delete(args.gid)


def do_keypair_list(cs, args):
    """
    Print a list of all keypairs in the specified group. 
    """
    keypairs = cs.keypairs.list(args.gid)
    fields = ['keypair_id', 'name', 'is_default', 'status']
    print_list(keypairs, fields, sortby='keypair_id')


@cliutils.arg(
    'keypair_id',
    metavar='<keypair_id>',
    help=_("Keypair ID"))
def do_keypair_show(cs, args):
    """
    Show details about the given keypair. 
    """
    keypair = cs.keypairs.get(args.gid, args.keypair_id)
    d = keypair._info
    print_dict(d)


@cliutils.arg(
    '--name',
    metavar='<name>',
    help=_("Name of the new keypair"))
@cliutils.arg(
    '--is_default',
    metavar='<is_default>',
    help=_("Defaults to the default keypair of the group"),
    type=lambda v: strutils.bool_from_string(v, True),
    default=False)
def do_keypair_create(cs, args):
    """
    Create a new keypair.
    """
    keypair = cs.keypairs.create(args.gid, args.name, args.is_default)
    d = keypair._info
    print_dict(d)


@cliutils.arg(
    'keypair_id',
    metavar='<keypair_id>',
    help=_("Keypair id"))
@cliutils.arg(
    '--is_default',
    metavar='<is_default>',
    help=_("Defaults to the default keypair of the group"),
    type=lambda v: strutils.bool_from_string(v, True),
    default=True)
def do_keypair_update(cs, args):
    """
    Update the specified keypair.
    """
    keypair = cs.keypairs.update(args.gid, args.keypair_id, args.is_default)
    d = keypair._info
    print_dict(d)


@cliutils.arg(
    'keypair_id',
    metavar='<keypair_id>',
    help=_("Keypair id"))
def do_keypair_delete(cs, args):
    """
    Delete the specified keypair.
    """
    cs.keypairs.delete(args.gid, args.keypair_id)


def do_securitygroup_list(cs, args):
    """
    Print a list of all security groups in the specified group.
    """
    securitygroups = cs.securitygroups.list(args.gid)
    fields = [
        'securitygroup_id', 'name', 'is_default', 'status'
    ]
    print_list(securitygroups, fields, sortby='securitygroup_id')


@cliutils.arg(
    'securitygroup_id',
    metavar='<securitygroup_id>',
    help=_("Securitygroup id"))
def do_securitygroup_show(cs, args):
    """
    Show details about the given security group.
    """
    securitygroup = cs.securitygroups.get(args.gid, args.securitygroup_id)
    d = securitygroup._info
    print_dict(d)


@cliutils.arg(
    '--name',
    metavar='<name>',
    help=_("Name of the new securitygroup"))
@cliutils.arg(
    '--is_default',
    metavar='<is_default>',
    help=_("Defaults to the default securitygroup of the group"),
    type=lambda v: strutils.bool_from_string(v, True),
    default=False)
@cliutils.arg(
    '--rule',
    metavar="<protocol=tcp|udp|icmp,port_range_max=integer,"
            "port_range_min=integer,remote_ip_prefix=cidr,"
            "remote_securitygroup_id=securitygroup_uuid>",
    action='append',
    type=_keyvalue_to_dict,
    dest='rules',
    default=[],
    help=_("Securitygroup rules. "
           "protocol: Protocol of packet, "
           "port_range_max: Starting port range, "
           "port_range_min: Ending port range, "
           "remote_ip_prefix: CIDR to match on, "
           "remote_securitygroup_id: Remote securitygroup id to apply rule. "
           "(Can be repeated)"))
def do_securitygroup_create(cs, args):
    """
    Create a new security group.
    """
    securitygroup = cs.securitygroups.create(args.gid,
                                             args.name,
                                             args.is_default,
                                             args.rules)
    d = securitygroup._info
    print_dict(d)


@cliutils.arg(
    'securitygroup_id',
    metavar='<securitygroup_id>',
    help=_("Securitygroup id"))
@cliutils.arg(
    '--is_default',
    metavar='<is_default>',
    help=_("Defaults to the default securitygroup of the group"),
    type=lambda v: strutils.bool_from_string(v, True),
    default=True)
def do_securitygroup_update(cs, args):
    """
    Update the specified security group.
    """
    securitygroup = cs.securitygroups.update(args.gid,
                                             args.securitygroup_id,
                                             args.is_default)
    d = securitygroup._info
    print_dict(d)


@cliutils.arg(
    'securitygroup_id',
    metavar='<securitygroup_id>',
    help=_("Securitygroup id"))
def do_securitygroup_delete(cs, args):
    """
    Delete the specified security group.
    """
    cs.securitygroups.delete(args.gid, args.securitygroup_id)


def do_network_list(cs, args):
    """
    Print a list of all networks in the specified group.
    """
    networks = cs.networks.list(args.gid)
    fields = [
        'network_id', 'name', 'is_admin', 'status'
    ]
    print_list(networks, fields, sortby='network_id')


@cliutils.arg(
    'network_id',
    metavar='<network_id>',
    help=_("network id"))
def do_network_show(cs, args):
    """
    Show details about the given network.
    """
    network = cs.networks.get(args.gid, args.network_id)
    d = network._info
    print_dict(d)


@cliutils.arg(
    'cidr',
    metavar='<cidr>',
    help=_("CIDR of the new network"))
@cliutils.arg(
    '--name',
    metavar='<name>',
    help=_("Name of the new network"))
@cliutils.arg(
    '--is_admin',
    metavar='<is_admin>',
    help=_(""),
    type=lambda v: strutils.bool_from_string(v, True),
    default=False)
@cliutils.arg(
    '--gateway_ip',
    metavar='<gateway_ip>',
    help=_("Gateway ip address of the new network"))
@cliutils.arg(
    '--dns_nameserver',
    metavar='<dns_nameserver>',
    dest='dns_nameservers',
    action='append',
    help=_("DNS server for the new network (Can be repeated)"))
@cliutils.arg(
    '--ext_router_id',
    metavar='<ext_router_id>',
    help=_("Router id the new network connects to"))
def do_network_create(cs, args):
    """
    Create a network.
    """
    network = cs.networks.create(args.gid,
                                 args.cidr,
                                 args.name,
                                 args.is_admin,
                                 args.gateway_ip,
                                 args.dns_nameservers,
                                 args.ext_router_id)
    d = network._info
    print_dict(d)


@cliutils.arg(
    'network_id',
    metavar='<network_id>',
    help=_("network id"))
def do_network_delete(cs, args):
    """
    Delete the specified network.
    """
    cs.networks.delete(args.gid, args.network_id)


def do_process_list(cs, args):
    """
    Print a list of all processes in the specified group.
    """
    processes = cs.processes.list(args.gid)
    fields = [
        'pid', 'ppid', 'name', 'status'
    ]
    print_list(processes, fields, sortby='pid')


@cliutils.arg(
    'pid',
    metavar='<pid>',
    help=_("process ID"))
def do_process_show(cs, args):
    """
    Show details about the given process.
    """
    process = cs.processes.get(args.gid, args.pid)
    d = process._info
    print_process(d)


@cliutils.arg(
    '--ppid',
    metavar='<ppid>',
    help=_("Parent process id of the new process"))
@cliutils.arg(
    '--name',
    metavar='<name>',
    help=_("Name of the new process"))
@cliutils.arg(
    '--nova_flavor_id',
    metavar='<nova_flavor_id>',
    help=_("Flavor id of the new process"))
@cliutils.arg(
    '--glance_image_id',
    metavar='<glance_image_id>',
    help=_("Image id that registered on Glance of the new process"))
@cliutils.arg(
    '--keypair_id',
    metavar='<keypair_id>',
    help=_("Keypair id of the new process uses"))
@cliutils.arg(
    '--securitygroup_id',
    metavar='<securitygroup_id>',
    dest='securitygroup_ids',
    action='append',
    default=[],
    help=_("Securitygroup id the new process belongs to (Can be repeated)"))
@cliutils.arg(
    '--userdata',
    metavar='<userdata>',
    help=_("Userdata file to pass"))
@cliutils.arg(
    '--args',
    metavar='<key1=value1,key2=value2 or a file including key=value lines>',
    help=_("Key-value pairs to be passed to metadata server"))
def do_process_create(cs, args):
    """
    Create a new process.
    """
    if args.userdata:
        try:
            userdata = open(args.userdata)
        except IOError as e:
            raise exceptions.CommandError(
                _("Can't open '%s'") % args.userdata)
    else:
        userdata = None

    if args.args:
        if os.path.exists(args.args):
            try:
                f = open(args.args)
                options = {}
                for line in f:
                    k, v = line.split('=', 1)
                    options.update({k.strip(): v.strip()})
            except IOError as e:
                raise exceptions.CommandError(
                    _("Can't open '%s'") % args.args)
            except ValueError:
                raise exceptions.CommandError(
                    _("%s is not the format of key=value lines") % args.args)
        else:
            try:
                options = _keyvalue_to_dict(args.args)
            except argparse.ArgumentTypeError as e:
                raise exceptions.CommandError(e)
    else:
        options = None

    process = cs.processes.create(args.gid,
                                  ppid=args.ppid,
                                  name=args.name,
                                  nova_flavor_id=args.nova_flavor_id,
                                  glance_image_id=args.glance_image_id,
                                  keypair_id=args.keypair_id,
                                  securitygroup_ids=args.securitygroup_ids,
                                  userdata=userdata,
                                  args=options)
    d = process._info
    print_process(d)


@cliutils.arg(
    'pid',
    metavar='<pid>',
    help=_("Process id"))
@cliutils.arg(
    '--app_status',
    metavar='<app_status>',
    help=_("Application layer status of the process"))
def do_process_update(cs, args):
    """
    Update the specified process.
    """
    process = cs.processes.update(args.gid, args.pid, args.app_status)
    d = process._info
    print_process(d)


@cliutils.arg(
    'pid',
    metavar='<pid>',
    help=_("Process id"))
def do_process_delete(cs, args):
    """
    Delete the specified process.
    """
    cs.processes.delete(args.gid, args.pid)


def do_proxy_show(cs, args):
    """
    Show details about the given rack-proxy process.
    """
    proxy = cs.proxy.get(args.gid)
    d = proxy._info
    print_process(d)


@cliutils.arg(
    '--name',
    metavar='<name>',
    help=_("Name of the new process"))
@cliutils.arg(
    '--nova_flavor_id',
    metavar='<nova_flavor_id>',
    help=_("Flavor id of the new process"))
@cliutils.arg(
    '--glance_image_id',
    metavar='<glance_image_id>',
    help=_("Image id that registered on Glance of the new process"))
@cliutils.arg(
    '--keypair_id',
    metavar='<keypair_id>',
    help=_("Keypair id of the new process uses"))
@cliutils.arg(
    '--securitygroup_id',
    metavar='<securitygroup_id>',
    dest='securitygroup_ids',
    action='append',
    default=[],
    help=_("Securitygroup id the new process belongs to (Can be repeated)"))
@cliutils.arg(
    '--userdata',
    metavar='<userdata>',
    help=_("Userdata file to pass"))
@cliutils.arg(
    '--args',
    metavar='<key1=value1,key2=value2 or a file including key=value lines>',
    help=_("Key-value pairs to be passed to metadata server"))
def do_proxy_create(cs, args):
    """
    Create a new rack-proxy process.
    """
    if args.userdata:
        try:
            userdata = open(args.userdata)
        except IOError as e:
            raise exceptions.CommandError(
                _("Can't open '%s'") % args.userdata)
    else:
        userdata = None

    if args.args:
        if os.path.exists(args.args):
            try:
                f = open(args.args)
                options = {}
                for line in f:
                    k, v = line.split('=', 1)
                    options.update({k.strip(): v.strip()})
            except IOError as e:
                raise exceptions.CommandError(
                    _("Can't open '%s'") % args.args)
            except ValueError:
                raise exceptions.CommandError(
                    _("%s is not the format of key=value lines") % args.args)
        else:
            try:
                options = _keyvalue_to_dict(args.args)
            except argparse.ArgumentTypeError as e:
                raise exceptions.CommandError(e)
    else:
        options = None

    proxy = cs.proxy.create(args.gid,
                            name=args.name,
                            nova_flavor_id=args.nova_flavor_id,
                            glance_image_id=args.glance_image_id,
                            keypair_id=args.keypair_id,
                            securitygroup_ids=args.securitygroup_ids,
                            userdata=userdata,
                            args=options)
    d = proxy._info
    print_process(d)


@cliutils.arg(
    '--shm_endpoint',
    metavar='<shm_endpoint>',
    help=_("Endpoint of the shared memory service"))
@cliutils.arg(
    '--ipc_endpoint',
    metavar='<ipc_endpoint>',
    help=_("Endpoint of the IPC service"))
@cliutils.arg(
    '--fs_endpoint',
    metavar='<fs_endpoint>',
    help=_("Endpoint of the file system service"))
@cliutils.arg(
    '--app_status',
    metavar='<app_status>',
    help=_("Application layer status of the proxy"))
def do_proxy_update(cs, args):
    """
    Update the specified rack-proxy process.
    """
    proxy = cs.proxy.update(args.gid,
                            args.shm_endpoint,
                            args.ipc_endpoint,
                            args.fs_endpoint,
                            args.app_status)
    d = proxy._info
    print_process(d)


def print_process(d):
    securitygroup_ids = d.get('securitygroup_ids')
    if securitygroup_ids:
        d['securitygroup_ids'] = ','.join(securitygroup_ids)

    network_ids = d.get('network_ids')
    if network_ids:
        d['network_ids'] = ','.join(network_ids)

    args = d.get('args')
    if args:
        s = ''
        for k, v in args.items():
            s += k + '=' + v + '\n'
        d['args'] = s.rstrip('\n')

    print_dict(d)


def print_list(objects, fields, sortby=None):
    pt = prettytable.PrettyTable(fields)
    pt.align = 'l'
    for o in objects:
        row = []
        for f in fields:
            row.append(getattr(o, f, ''))
        pt.add_row(row)
    print(pt.get_string(sortby=sortby))


def print_dict(d):
    pt = prettytable.PrettyTable(['Property', 'Value'])
    pt.align = 'l'
    for k, v in sorted(d.items()):
        pt.add_row([k, v])
    print(pt.get_string())


@cliutils.arg(
    'config',
    metavar='<config-file>',
    help=_("Configuration file included parameters of the new group"))
def do_group_init(cs, args):
    """
    Create a group, a keypair, a security group, a network and 
    a rack-proxy based on the specified configuration file.
    """
    config = ConfigParser()
    config.read(args.config)

    # Create a group
    try:
        name = config.get('group', 'name')
    except NoOptionError:
        raise exceptions.CommandError(_("Group name is required."))
    try:
        description = config.get('group', 'description')
    except NoOptionError:
        description = None

    group = cs.groups.create(name, description)
    d = group._info
    print_dict(d)

    gid = group.gid

    # Create a keypair
    try:
        name = config.get('keypair', 'name')
    except NoOptionError:
        name = None
    try:
        is_default = config.get('keypair', 'is_default')
    except NoOptionError:
        is_default = False

    keypair = cs.keypairs.create(gid, name, is_default)
    d = keypair._info
    print_dict(d)

    # Create a securitygroup
    try:
        name = config.get('securitygroup', 'name')
    except NoOptionError:
        name = None
    try:
        is_default = config.get('securitygroup', 'is_default')
    except NoOptionError:
        is_default = False
    try:
        rules = config.get('securitygroup', 'rules').split()
        for i in range(len(rules)):
            rules[i] = _keyvalue_to_dict(rules[i])
    except NoOptionError:
        rules = []
    except argparse.ArgumentTypeError as e:
        raise exceptions.CommandError(
            _("Could not create a securitygroup: "
              "securitygroup rules are not valid formart: %s") % e.message)

    securitygroup = cs.securitygroups.create(gid, name, is_default, rules)
    d = securitygroup._info
    print_dict(d)

    # Create a network
    try:
        cidr = config.get('network', 'cidr')
    except NoOptionError:
        raise exceptions.CommandError(_("Network cidr is required."))
    try:
        name = config.get('network', 'name')
    except NoOptionError:
        name = None
    try:
        is_admin = config.get('network', 'is_admin')
    except NoOptionError:
        is_admin = False
    try:
        gateway_ip = config.get('network', 'gateway_ip')
    except NoOptionError:
        gateway_ip = None
    try:
        dns_nameservers = config.get('network', 'dns_nameservers').split()
    except NoOptionError:
        dns_nameservers = []
    try:
        ext_router_id = config.get('network', 'ext_router_id')
    except NoOptionError:
        ext_router_id = None

    network = cs.networks.create(gid, cidr, name, is_admin,
                                 gateway_ip, dns_nameservers, ext_router_id)
    d = network._info
    print_dict(d)

    # Create a proxy
    try:
        name = config.get('proxy', 'name')
    except NoOptionError:
        name = None
    try:
        nova_flavor_id = config.get('proxy', 'nova_flavor_id')
    except NoOptionError:
        raise exceptions.CommandError(_("Flavor id is required."))
    try:
        glance_image_id = config.get('proxy', 'glance_image_id')
    except NoOptionError:
        raise exceptions.CommandError(_("Image id is required."))
    keypair_id = keypair.keypair_id
    securitygroup_ids = [securitygroup.securitygroup_id]
    try:
        userdata = config.get('proxy', 'userdata')
        userdata = open(userdata)
    except NoOptionError:
        userdata = None
    except IOError:
        raise exceptions.CommandError(
            _("Can't open %s.") % userdata)
    try:
        proxy_args = config.get('proxy', 'args')
        proxy_args = _keyvalue_to_dict(proxy_args)
    except NoOptionError:
        proxy_args = None
    except argparse.ArgumentTypeError as e:
        raise exceptions.CommandError(e)

    proxy = cs.proxy.create(gid, name=name,
                            nova_flavor_id=nova_flavor_id,
                            glance_image_id=glance_image_id,
                            keypair_id=keypair_id,
                            securitygroup_ids=securitygroup_ids,
                            userdata=userdata,
                            args=proxy_args)
    d = proxy._info
    print_process(d)

    result_dict = {
        "gid": gid,
        "keypair_id": keypair_id,
        "securitygroup_id": securitygroup.securitygroup_id,
        "network_id": network.network_id,
        "proxy pid": proxy.pid
    }
    print_dict(result_dict)
