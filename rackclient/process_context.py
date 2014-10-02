import json
import requests
from rackclient import exceptions
from rackclient.v1 import client

METADATA_URL = 'http://169.254.169.254/openstack/latest/meta_data.json'


class ProcessContext(object):

    def __init__(self, gid=None, ppid=None, pid=None, proxy_ip=None,
                 proxy_port=8088, api_version='v1', args=None):
        self.gid = gid
        self.ppid = ppid
        self.pid = pid
        self.proxy_ip = proxy_ip
        url = 'http://%s:%d/%s' % (proxy_ip, proxy_port, api_version)
        self.proxy_url = url
        self._add_args(args)
        self.client = client.Client(rack_url=self.proxy_url)

    def _add_args(self, args):
        for (k, v) in args.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                pass

    def _get_process_list(self):
        return self.client.processes.list(self.gid)

    def __getattr__(self, k):
        if k == 'process_list':
            return self._get_process_list()


def _get_metadata(metadata_url):
    resp = requests.get(metadata_url)

    if resp.text:
        try:
            body = json.loads(resp.text)
        except ValueError:
            body = None
    else:
        body = None

    if body:
        return body['meta']
    else:
        return None


def _get_process_context():
    try:
        metadata = _get_metadata(METADATA_URL)
        pctxt = ProcessContext(
            gid=metadata.pop('gid'),
            ppid=metadata.pop('ppid') if "ppid" in metadata else None,
            pid=metadata.pop('pid'),
            proxy_ip=metadata.pop('proxy_ip'),
            args=metadata)

        proxy_info = pctxt.client.proxy.get(pctxt.gid)
        endpoints = {
            "fs_endpoint": proxy_info.fs_endpoint,
            "shm_endpoint": proxy_info.shm_endpoint,
            "ipc_endpoint": proxy_info.ipc_endpoint
        }
        pctxt._add_args(endpoints)
        return pctxt
    except Exception:
        raise exceptions.GetProcessContextError()


try:
    PCTXT = _get_process_context()
except exceptions.GetProcessContextError as e:
    PCTXT = None
