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
from mock import patch
from rackclient.tests import utils
from rackclient.lib.syscall.default import shm


class ShmTest(utils.LibTestCase):

    def target_context(self):
        return "syscall.default.shm"

    def setUp(self):
        super(ShmTest, self).setUp()
        patcher = patch('redis.StrictRedis')
        self.addCleanup(patcher.stop)
        self.mock_redis = patcher.start()

    def test_read(self):
        ins_redis = self.mock_redis.return_value
        ins_redis.get.return_value = 'value'
        real = shm.Shm()
        self.assertEquals('value', real.read("key"))
        ins_redis.get.assert_called_once_with("key")

    def test_write(self):
        ins_redis = self.mock_redis.return_value
        ins_redis.set.return_value = 'value'
        real = shm.Shm()
        self.assertEquals('value', real.write("key", "value"))
        ins_redis.set.assert_called_once_with("key", "value")

    def test_list_read(self):
        ins_redis = self.mock_redis.return_value
        ins_redis.llen.return_value = 1
        ins_redis.lrange.return_value = "value"
        real = shm.Shm()
        self.assertEquals('value', real.list_read("key"))
        ins_redis.lrange.assert_called_once_with("key", 0, 1)

    def test_list_write(self):
        ins_redis = self.mock_redis.return_value
        ins_redis.rpush.return_value = 'value'
        real = shm.Shm()
        self.assertEquals('value', real.list_write("key", "value"))
        ins_redis.rpush.assert_called_once_with("key", "value")

    def test_list_delete_value(self):
        ins_redis = self.mock_redis.return_value
        ins_redis.lrem.return_value = 'value'
        real = shm.Shm()
        self.assertEquals('value', real.list_delete_value("key", "value"))
        ins_redis.lrem.assert_called_once_with("key", 1, "value")

    def test_delete(self):
        ins_redis = self.mock_redis.return_value
        ins_redis.delete.return_value = 'value'
        real = shm.Shm()
        self.assertEquals('value', real.delete("key"))
        ins_redis.delete.assert_called_once_with("key")
