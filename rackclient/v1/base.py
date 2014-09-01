from rackclient.openstack.common.apiclient import base

Resource = base.Resource


class Manager(object):

    resource_class = None

    def __init__(self, api):
        self.api = api

    def _list(self, url, response_key, obj_class=None):
        _resp, body = self.api.client.get(url)

        if obj_class is None:
            obj_class = self.resource_class

        data = body[response_key]

        objs = []
        for res in data:
            if res:
                obj = obj_class(self, res, loaded=True)
                objs.append(obj)

        return objs

    def _get(self, url, response_key):
        _resp, body = self.api.client.get(url)
        obj = self.resource_class(self, body[response_key], loaded=True)
        return obj

    def _create(self, url, body, response_key):
        _resp, body = self.api.client.post(url, body=body)
        obj = self.resource_class(self, body[response_key])
        return obj

    def _delete(self, url):
        _resp, _body = self.api.client.delete(url)

    def _update(self, url, body, response_key):
        _resp, body = self.api.client.put(url, body=body)
        if body:
            return self.resource_class(self, body[response_key])
