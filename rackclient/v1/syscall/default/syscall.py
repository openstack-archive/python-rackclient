import logging
import Queue
import threading

from rackclient import exceptions
from rackclient import process_context
from rackclient.v1 import processes
from rackclient.v1.syscall.default import messaging
from rackclient.v1.syscall.default import pipe as rackpipe
from rackclient.v1.syscall.default import file as rackfile

LOG = logging.getLogger(__name__)
PCTXT = process_context.PCTXT


def fork(opt_list, timeout_limit=180):
    LOG.debug("start fork")
    LOG.debug("fork create processes count: %s", len(opt_list))

    return_process_list = []
    while True:
        try:
            child_list = _bulk_fork(PCTXT.pid, opt_list)
            success_list, error_list = _check_connection(PCTXT.pid,
                                                         child_list,
                                                         timeout_limit)
        except Exception as e:
            raise exceptions.ForkError(e)

        return_process_list += success_list
        if error_list:
            opt_list = []
            for error_process in error_list:
                args = error_process.args
                args.pop('gid')
                args.pop('pid')
                args.pop('ppid')
                args.pop('proxy_ip')
                opt_list.append(dict(args=args))
        else:
            break

    return return_process_list


def pipe(name=None):
    p = rackpipe.Pipe(name)
    return p


def fopen(file_path, mode="r"):
    return rackfile.File(file_path, mode)


def _bulk_fork(pid, args_list):
    LOG.debug("start bulk_fork")
    q = Queue.Queue()

    def _fork(pid, **kwargs):
        try:
            child = PCTXT.client.processes.create(gid=PCTXT.gid,
                                                  ppid=pid,
                                                  **kwargs)
            q.put(child)
        except Exception as e:
            attr = dict(args=kwargs, error=e)
            q.put(processes.Process(PCTXT.client, attr))

    tg = []
    process_list = []
    while True:
        for args in args_list:
            t = threading.Thread(target=_fork, args=(pid,), kwargs=args)
            t.start()
            tg.append(t)

        for t in tg:
            t.join()

        args_list = []
        success_processes = []
        for i in range(q.qsize()):
            process = q.get()
            if hasattr(process, "error"):
                args_list.append(process.args)
            else:
                success_processes.append(process)

        process_list += success_processes
        LOG.debug("bulk_fork success processes count: %s", len(process_list))
        if not success_processes:
            msg = "No child process is created."
            raise Exception(msg)
        elif not args_list:
            break
    return process_list


def _check_connection(pid, process_list, timeout):
    LOG.debug("start check_connection")
    msg = messaging.Messaging()
    msg_list = msg.receive_all_msg(timeout_limit=timeout,
                                   msg_limit_count=len(process_list))

    pid_list = []
    for message in msg_list:
        if message.get('pid'):
            pid_list.append(message.get('pid'))

    actives = []
    inactives = []
    for process in process_list:
        if pid_list and process.pid in pid_list:
            rackpipe.Pipe.share(pid, process.pid)
            msg.send_msg(target=process.pid, message="start")
            actives.append(process)
            pid_list.remove(process.pid)
        else:
            PCTXT.client.processes.delete(PCTXT.gid, process.pid)
            inactives.append(process)

    LOG.debug("_check_connection active processes count: %s", len(actives))
    LOG.debug("_check_connection inactive processes count: %s", len(inactives))

    if not actives:
        msg = "No child process is active."
        raise Exception(msg)

    return actives, inactives