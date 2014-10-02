import json
import requests


def headers():
    return {"content-type": "application/json",
            "accept": "application/json"}


def request(url, method, body=None):
    res = getattr(requests,method)(url, headers=headers(), data=json.dumps(body))
    return res.json()


def get_metadata(resource):
    url = 'http://169.254.169.254/openstack/latest/meta_data.json'
    metadata = request(url, "get")["meta"].get(resource)
    return metadata