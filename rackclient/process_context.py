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
import json
import requests
from rackclient import client
from rackclient.exceptions import MetadataAccessError

METADATA_URL = 'http://169.254.169.254/openstack/latest/meta_data.json'


class ProcessContext(object):

    def __init__(self):
        self.gid = None
        self.pid = None
        self.ppid = None
        self.proxy_ip = None
        self.proxy_url = None
        self.fs_endpoint = None
        self.shm_endpoint = None
        self.ipc_endpoint = None
        self.client = None

    def add_args(self, args):
        if isinstance(args, dict):
            for (k, v) in args.items():
                try:
                    setattr(self, k, v)
                except AttributeError:
                    pass


PCTXT = ProcessContext()


def _get_metadata(metadata_url):
    try:
        resp = requests.get(metadata_url)
    except Exception as e:
        msg = "Could not get the metadata: %s" % e.message
        raise MetadataAccessError(msg)

    body = json.loads(resp.text)
    return body['meta']


def init(client_version='1', proxy_port=8088, api_version='v1'):
    metadata = _get_metadata(METADATA_URL)

    PCTXT.gid = metadata.pop('gid')
    PCTXT.pid = metadata.pop('pid')
    PCTXT.ppid = metadata.pop('ppid') if 'ppid' in metadata else None
    PCTXT.proxy_ip = metadata.pop('proxy_ip')
    PCTXT.proxy_url = 'http://%s:%d/%s' % \
                      (PCTXT.proxy_ip, proxy_port, api_version)
    PCTXT.client = client.Client(client_version, rack_url=PCTXT.proxy_url)
    PCTXT.add_args(metadata)

    proxy_info = PCTXT.client.proxy.get(PCTXT.gid)
    PCTXT.fs_endpoint = proxy_info.fs_endpoint
    PCTXT.shm_endpoint = proxy_info.shm_endpoint
    PCTXT.ipc_endpoint = proxy_info.ipc_endpoint
