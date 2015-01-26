import logging
import time
from datetime import datetime
import redis
from rackclient import process_context

LOG = logging.getLogger(__name__)

PCTXT = process_context.PCTXT


class EndOfFile(Exception):
    message = 'EOF'


class NoDescriptor(Exception):
    message = 'Descriptor Not Found'

    def __init__(self, message=None):
        self.message = message or self.__class__.message

    def __str__(self):
        formatted_string = self.message
        return formatted_string


class NoReadDescriptor(NoDescriptor):
    message = 'Read Descriptor Not Found'


class NoWriteDescriptor(NoDescriptor):
    message = 'Write Descriptor Not Found'


def eof():
    raise EndOfFile()


def no_reader():
    raise NoReadDescriptor()


def no_writer():
    raise NoWriteDescriptor()


def read_state_key(name):
    return name + "_read"


def write_state_key(name):
    return name + "_write"


def reference_key_pattern(name="*", pid="*"):
    return name + ":" + pid


PIPE = 1
FIFO = 2
PORT = 6379


class Pipe:
    def __init__(self, name=None, read=None, write=None):
        now = datetime.now()
        self.host = PCTXT.proxy_ip
        self.port = PORT
        if name:
            self.is_named = True
            self.r = redis.StrictRedis(host=self.host, port=self.port, db=FIFO)
            self.name = name
            read_state = now
            write_state = now
        else:
            self.is_named = False
            self.r = redis.StrictRedis(host=self.host, port=self.port, db=PIPE)
            parent_pipe = self.r.keys(reference_key_pattern(pid=PCTXT.pid))
            if parent_pipe:
                self.name = self.r.get(parent_pipe[0])
            else:
                self.name = PCTXT.pid
            read_state = self.r.hget(read_state_key(self.name), PCTXT.pid) or now
            write_state = self.r.hget(write_state_key(self.name), PCTXT.pid) or now
        if read is not None:
            if read:
                read_state = now
            else:
                read_state = "close"
        if write is not None:
            if write:
                write_state = now
            else:
                write_state = "close"
        self.read_state = read_state
        self.write_state = write_state
        self.r.hset(read_state_key(self.name), PCTXT.pid, self.read_state)
        self.r.hset(write_state_key(self.name), PCTXT.pid, self.write_state)

    def read(self):
        if self.read_state == "close":
            no_reader()
        data = self._read()
        while data is None:
            data = self._read()
            time.sleep(0.1)
        return data

    def _read(self):
        data = self.r.lpop(self.name)
        if data is None and not self.has_writer():
            self.flush()
            eof()
        else:
            return data

    def write(self, data):
        if self.write_state == "close":
            no_writer()
        self.r.rpush(self.name, data)
        if self.has_reader():
            return True
        else:
            no_reader()

    def close_reader(self):
        self.read_state = "close"
        self.r.hset(read_state_key(self.name), PCTXT.pid, self.read_state)

    def close_writer(self):
        self.write_state = "close"
        self.r.hset(write_state_key(self.name), PCTXT.pid, self.write_state)

    def has_reader(self):
        read_states = self.r.hvals(read_state_key(self.name))
        if len(read_states) <= 1:
            return True
        for state in read_states:
            if not state == "close":
                return True
        return False

    def has_writer(self):
        write_states = self.r.hvals(write_state_key(self.name))
        if len(write_states) <= 1:
            return True
        for state in write_states:
            if not state == "close":
                return True
        return False

    def flush(self):
        keys = [self.name,
                read_state_key(self.name),
                write_state_key(self.name)]
        if not self.is_named:
            keys = keys + self.r.keys(reference_key_pattern(name=self.name))
        self.r.delete(*tuple(keys))

    @classmethod
    def flush_by_pid(cls, pid, host=None):
        if not host:
            host = PCTXT.proxy_ip

        r = redis.StrictRedis(host=host, port=PORT, db=PIPE)
        keys = [pid,
                read_state_key(pid),
                write_state_key(pid)]
        keys = keys + r.keys(reference_key_pattern(name=pid))
        r.delete(*tuple(keys))

    @classmethod
    def flush_by_name(cls, name, host=None):
        if not host:
            host = PCTXT.proxy_ip

        r = redis.StrictRedis(host=host, port=PORT, db=FIFO)
        keys = [name,
                read_state_key(name),
                write_state_key(name)]
        r.delete(*tuple(keys))

    @classmethod
    def share(cls, ppid, pid, host=None):
        if not host:
            host = PCTXT.proxy_ip
        
        now = datetime.now()
        r = redis.StrictRedis(host=host, port=PORT, db=PIPE)
        keys = r.keys(reference_key_pattern(pid=ppid))
        if keys:
            name = r.get(keys[0])
        else:
            if r.keys(read_state_key(ppid)):
                name = ppid
            else:
                return False
        reference_key = reference_key_pattern(name, pid)
        r.set(reference_key, name)
        current_read_state = r.hget(read_state_key(name), name)
        current_write_state = r.hget(write_state_key(name), name)
        if not current_read_state == "close":
            current_read_state = now
        if not current_write_state == "close":
            current_write_state = now
        r.hset(read_state_key(name), pid, current_read_state)
        r.hset(write_state_key(name), pid, current_write_state)
        return True
