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
import Queue
import threading

from rackclient import exceptions
from rackclient.v1 import processes
from rackclient.lib import RACK_CTX
from rackclient.lib.syscall.default import messaging
from rackclient.lib.syscall.default import pipe as rackpipe
from rackclient.lib.syscall.default import file as rackfile


LOG = logging.getLogger(__name__)


def fork(opt_list, timeout_limit=180):
    LOG.debug("start fork")
    LOG.debug("fork create processes count: %s", len(opt_list))

    return_process_list = []
    while True:
        try:
            child_list = _bulk_fork(RACK_CTX.pid, opt_list)
            success_list, error_list = _check_connection(RACK_CTX.pid,
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


def _bulk_fork(pid, args_list):
    LOG.debug("start bulk_fork")
    q = Queue.Queue()

    def _fork(pid, **kwargs):
        try:
            child = RACK_CTX.client.processes.create(gid=RACK_CTX.gid,
                                                     ppid=pid,
                                                     **kwargs)
            q.put(child)
        except Exception as e:
            attr = dict(args=kwargs, error=e)
            q.put(processes.Process(RACK_CTX.client, attr))

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
            RACK_CTX.client.processes.delete(RACK_CTX.gid, process.pid)
            inactives.append(process)

    LOG.debug("_check_connection active processes count: %s", len(actives))
    LOG.debug("_check_connection inactive processes count: %s", len(inactives))

    if not actives:
        msg = "No child process is active."
        raise Exception(msg)

    return actives, inactives


def kill(pid):
    RACK_CTX.client.processes.delete(RACK_CTX.gid, pid)


def pipe(name=None):
    p = rackpipe.Pipe(name)
    return p


def fopen(file_path, mode="r"):
    return rackfile.File(file_path, mode)
