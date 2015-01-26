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
from rackclient import process_context
from rackclient.v1.syscall.default import messaging
from rackclient import exceptions

PCTXT = process_context.PCTXT


def _is_exist():
    try:
        PCTXT.client.processes.get(PCTXT.gid, PCTXT.pid)
    except exceptions.NotFound:
        msg = "This process is not recognized by RACK"
        raise exceptions.InvalidProcessError(msg)


def init():
    try:
        process_context.init()
        _is_exist()
        messaging.init()
    except Exception as e:
        msg = "Failed to initialize the process: %s." % e.message
        raise exceptions.ProcessInitError(msg)
