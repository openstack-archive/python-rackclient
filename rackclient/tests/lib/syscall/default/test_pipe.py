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
import datetime

from rackclient import exceptions
from mock import patch
from rackclient.tests import utils
from rackclient.lib.syscall.default import pipe


class PipeTest(utils.LibTestCase):

    def target_context(self):
        return "syscall.default.pipe"

    def setUp(self):
        super(PipeTest, self).setUp()
        patcher = patch('redis.StrictRedis')
        self.addCleanup(patcher.stop)
        self.mock_redis=patcher.start()
        self.ins_redis = self.mock_redis.return_value
   
    def test_init_default(self):
        self.ins_redis.keys.return_value = "data"
        self.ins_redis.get.return_value = "parent"
        self.ins_redis.hget.side_effect = ["r","w"]
        real = pipe.Pipe()
        self.assertEqual("10.0.0.2", real.host)
        self.assertEqual(6379, real.port)
        self.assertEqual("parent", real.name)
        self.assertFalse(real.is_named)
        self.assertEqual("r",real.read_state)
        self.assertEqual("w", real.write_state)
        self.assertTrue(self.ins_redis.hset.call_count == 2)
   
    def test_init_param_read_write_child(self):
        self.ins_redis.keys.return_value = ""
        real = pipe.Pipe(read="read",write="write")
        self.assertEqual("10.0.0.2", real.host)
        self.assertEqual(6379, real.port)
        self.assertEqual("pid", real.name)
        self.assertFalse(real.is_named)
        self.assertTrue(isinstance(real.read_state, datetime.datetime))
        self.assertTrue(isinstance(real.write_state, datetime.datetime))
        self.assertTrue(self.ins_redis.hset.call_count == 2)
   
    def test_init_param_read_write_parent(self):
        self.ins_redis.keys.return_value = "data"
        self.ins_redis.get.return_value = "parent"
        real = pipe.Pipe(read="read",write="write")
        self.assertEqual("10.0.0.2", real.host)
        self.assertEqual(6379, real.port)
        self.assertEqual("parent", real.name)
        self.assertFalse(real.is_named)
        self.assertTrue(isinstance(real.read_state, datetime.datetime))
        self.assertTrue(isinstance(real.write_state, datetime.datetime))
        self.assertTrue(self.ins_redis.hset.call_count == 2)
   
    def test_init_param_read_write_not_none(self):
        self.ins_redis.keys.return_value = "data"
        self.ins_redis.get.return_value = "parent"
        real = pipe.Pipe(read="",write="")
        self.assertEqual("10.0.0.2", real.host)
        self.assertEqual(6379, real.port)
        self.assertEqual("parent", real.name)
        self.assertFalse(real.is_named)
        self.assertEqual("close", real.read_state)
        self.assertEqual("close", real.write_state)
        self.assertTrue(self.ins_redis.hset.call_count == 2)
   
    def test_init_param_name(self):
        real = pipe.Pipe("test")
        self.assertEqual("10.0.0.2", real.host)
        self.assertEqual(6379, real.port)
        self.assertTrue(real.is_named)
        self.assertEqual("test", real.name)
        self.assertTrue(isinstance(real.read_state, datetime.datetime))
        self.assertTrue(isinstance(real.write_state, datetime.datetime))
        self.assertTrue(self.ins_redis.hset.call_count == 2)
   
    def test_read(self):
        self.ins_redis.lpop.return_value = "data"
        real = pipe.Pipe(read="read", write="write")
        self.assertEqual("data", real.read())
   
    def test_read_none(self):
        self.ins_redis.lpop.side_effect = [None,"data"]
        real = pipe.Pipe(read="read", write="write")
        self.assertEqual("data", real.read())
           
    def test_read_EndOfFile(self):
        self.ins_redis.lpop.return_value = None
        self.ins_redis.hvals.return_value = ["close","close"]
        real = pipe.Pipe(read="read", write="write")
        self.assertRaises(exceptions.EndOfFile, real.read)
   
    def test_read_NoReadDescriptor(self):
        self.ins_redis.lpop.return_value = None
        self.ins_redis.hvals.return_value = ["close","close"]
        real = pipe.Pipe(read="", write="")
        self.assertRaises(exceptions.NoReadDescriptor, real.read)
   
    def test_write(self):
        real = pipe.Pipe(read="read",write="write")
        self.ins_redis.hvals.return_value = []
        self.assertTrue("data", real.write("data"))
        self.assertTrue(self.ins_redis.rpush.call_count == 1)
   
    def test_write_NoReadDescriptor(self):
        real = pipe.Pipe(read="read",write="write")
        self.ins_redis.hvals.return_value = ["close","close"]
        self.assertRaises(exceptions.NoReadDescriptor, real.write, "data")
        self.assertTrue(self.ins_redis.rpush.call_count == 1)
   
    def test_write_NoWriteDescriptor(self):
        real = pipe.Pipe(read="",write="")
        self.ins_redis.hvals.return_value = ["close","close"]
        self.assertRaises(exceptions.NoWriteDescriptor, real.write, "data")
        self.assertTrue(self.ins_redis.rpush.call_count == 0)
   
    def test_close_reader(self):
        self.ins_redis.keys.return_value = ""
        real = pipe.Pipe(read="read", write="write")
        real.close_reader()
        self.ins_redis.hset.assert_any_call("pid_read", "pid", "close")
   
    def test_close_write(self):
        self.ins_redis.keys.return_value = ""
        real = pipe.Pipe(read="read", write="write")
        real.close_writer()
        self.ins_redis.hset.assert_any_call("pid_write", "pid", "close")
   
    def test_has_reader_no_states(self):
        self.ins_redis.keys.return_value = ""
        self.ins_redis.hvals.return_value= []
        real = pipe.Pipe(read="read", write="write")
        self.assertTrue(real.has_reader())
   
    def test_has_reader_states_not_close(self):
        self.ins_redis.keys.return_value = ""
        self.ins_redis.hvals.return_value= ["open", "opne"]
        real = pipe.Pipe(read="read", write="write")
        self.assertTrue(real.has_reader())
   
    def test_has_reader_false(self):
        self.ins_redis.keys.return_value = ""
        self.ins_redis.hvals.return_value= ["close", "close"]
        real = pipe.Pipe(read="read", write="write")
        self.assertFalse(real.has_reader())
   
    def test_has_writer_no_states(self):
        self.ins_redis.keys.return_value = ""
        self.ins_redis.hvals.return_value= []
        real = pipe.Pipe(read="read", write="write")
        self.assertTrue(real.has_writer())
   
    def test_has_writer_states_not_close(self):
        self.ins_redis.keys.return_value = ""
        self.ins_redis.hvals.return_value= ["open", "opne"]
        real = pipe.Pipe(read="read", write="write")
        self.assertTrue(real.has_writer())
   
    def test_has_write_false(self):
        self.ins_redis.keys.return_value = ""
        self.ins_redis.hvals.return_value= ["close", "close"]
        real = pipe.Pipe(read="read",write="write")
        self.assertFalse(real.has_writer())
   
    def test_flush_not_named(self):
        self.ins_redis.keys.side_effect = ["", ["abc"]]
        real = pipe.Pipe(read="read", write="write")
        real.flush()
        keys = ["pid", "pid_read", "pid_write", "abc"]
        self.ins_redis.delete.assert_any_call(*tuple(keys))
   
    def test_flush_named(self):
        self.ins_redis.keys.return_value = ""
        real = pipe.Pipe(name="name", read="read",write="write")
        real.flush()
        keys = ["name", "name_read", "name_write"]
        self.ins_redis.delete.assert_any_call(*tuple(keys))
   
    def test_flush_by_pid(self):
        self.ins_redis.keys.return_value = ["abc"]
        pipe.Pipe.flush_by_pid("pid")
        keys = ["pid", "pid_read", "pid_write", "abc"]
        self.ins_redis.delete.assert_any_call(*tuple(keys))

    def test_flush_by_name(self):
        pipe.Pipe.flush_by_name("name")
        keys = ["name", "name_read", "name_write"]
        self.ins_redis.delete.assert_any_call(*tuple(keys))
   
    def test_share_keys_exitst_states_close(self):
        self.ins_redis.keys.return_value = ["value"]
        self.ins_redis.get.return_value = "name"
        self.ins_redis.hget.side_effect = ["close", "close"]
        self.assertTrue(pipe.Pipe.share("ppid", "pid"))
        self.ins_redis.set.assert_any_call("name:pid", "name")
        self.ins_redis.hset.assert_any_call("name_read", "pid", "close")
        self.ins_redis.hset.assert_any_call("name_write", "pid", "close")
   
    def test_share_keys_not_exist_states_not_close_ppid_exsits(self):
        mydatetime = datetime.datetime(2015, 1, 1, 0, 0)
        class FakeDateTime(datetime.datetime):
            @classmethod
            def now(cls):
                return mydatetime
        patcher = patch("rackclient.lib.syscall.default.pipe.datetime", FakeDateTime)
        patcher.start()
        self.ins_redis.keys.side_effect = [[], ["data"]]
        self.ins_redis.hget.side_effect = ["read", "write"]
        self.assertTrue(pipe.Pipe.share("ppid", "pid"))
        self.ins_redis.set.assert_any_call("ppid:pid", "ppid")
        self.ins_redis.hset.assert_any_call("ppid_read", "pid", mydatetime)
        self.ins_redis.hset.assert_any_call("ppid_write", "pid", mydatetime)
   
    def test_share_false(self):
        self.ins_redis.keys.side_effect = [[], []]
        self.assertFalse(pipe.Pipe.share("ppid", "pid"))

    def test_NoDescriptor_str_(self):
        self.assertEqual("Descriptor Not Found", exceptions.NoDescriptor().__str__())
        
