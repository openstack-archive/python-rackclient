import logging
import redis

from rackclient import process_context


LOG = logging.getLogger(__name__)

FIFO = 3
PORT = 6379

def get_host():
    return process_context.PCTXT.proxy_ip


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

