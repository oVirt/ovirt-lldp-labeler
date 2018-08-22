# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import print_function

import getopt
import logging
import sys

import labeler.labeler as labeler

_ARGUMENTS = 'hu:p:'
_ARGUMENTS_LONG = ['help', 'username=', 'password=']


def main(args):
    logging.basicConfig(level=logging.INFO)
    if len(args) > 0:
        _parse_arguments(args)
    else:
        labeler.init_labeler()
    labeler.run_labeler()
    labeler.clear_labeler()


def _parse_arguments(args):
    username = None
    password = None
    try:
        opts, args = getopt.getopt(args, _ARGUMENTS, _ARGUMENTS_LONG)
    except getopt.GetoptError as err:
        print(str(err))
        _handle_err()
    for option, argument in opts:
        if option in ('-h', '--help'):
            _handle_help()
        elif option in ('-u', '--username'):
            username = argument
        elif option in ('-p', '--password'):
            password = argument
        else:
            print('Wrong arguments')
    labeler.init_labeler(username, password)


def _handle_help():
    print('Usage: [-h] [-u username] [-p password] \n'
          '\n'
          '-h, --help Display help message \n'
          '-u USERNAME, --username=USERNAME Engine login username \n'
          '-p PASSWORD, --password=PASSWORD Engine login password')
    sys.exit(1)


def _handle_err():
    print("Use -h or --help for more information")
    sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
