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
import argparse


def keyvalue_to_dict(string):
    """
    Return a dict made from comma separated key-value strings

    :param string: comma separated key-value pairs
                   like 'key1=value1,key2=value2'
    :return: dict
    """
    try:
        d = {}
        pairs = string.split(',')
        for pair in pairs:
            (k, v) = pair.split('=', 1)
            d.update({k: v})
        return d
    except ValueError:
        msg = "%r is not in the format of key=value" % string
        raise argparse.ArgumentTypeError(msg)
