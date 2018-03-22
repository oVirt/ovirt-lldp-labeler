# Copyright 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
# Refer to the README and COPYING files for full details of the license
from __future__ import print_function

import sys
import getopt

import labeler.labeler as labeler

_ARGUMENTS = 'hu:p:'
_ARGUMENTS_LONG = ['help', 'username=', 'password=']


def main(args):
    if len(args) > 0:
        _parse_arguments(args)
    else:
        labeler.init_labeler()
    labeler.run_labeler()


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
