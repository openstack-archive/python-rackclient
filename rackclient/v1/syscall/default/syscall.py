from rackclient import process_context
from rackclient.v1.syscall.default import pipe as rackpipe, file as rackfile

PCTXT = process_context.PCTXT


def fork(pid=PCTXT.pid, **kwargs):
    child = PCTXT.client.processes.create(gid=PCTXT.gid, ppid=pid, **kwargs)
    rackpipe.Pipe.share(pid, child.pid)
    return child


def pipe(name=None):
    p = rackpipe.Pipe(name)
    return p


def fopen(container, file_name, mode="r"):
    return rackfile.File(container, file_name, mode)
