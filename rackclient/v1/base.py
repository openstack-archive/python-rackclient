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
