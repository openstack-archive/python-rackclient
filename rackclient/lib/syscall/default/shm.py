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
import logging
import redis

from rackclient.lib import RACK_CTX


LOG = logging.getLogger(__name__)

FIFO = 3
PORT = 6379


def get_host():
    return RACK_CTX.proxy_ip


class Shm(object):
    def __init__(self):
        self.host = get_host()
        self.port = PORT
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=FIFO)

    def read(self, key):
        data = self.r.get(key)
        return data

    def write(self, key, value):
        return self.r.set(key, value)

    def list_read(self, key):
        count = self.r.llen(key)
        return self.r.lrange(key, 0, count)

    def list_write(self, key, value):
        return self.r.rpush(key, value)

    def list_delete_value(self, key, value):
        return self.r.lrem(key, 1, value)

    def delete(self, key):
        return self.r.delete(key)
