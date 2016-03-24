"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import subprocess

from fuelweb_test import logger

from proboscis.asserts import assert_true


class Vmrun(object):
    """Vmrun utilite wrapper."""

    def __init__(
            self, host_type, path_to_vmx_file, host_port=None, host_name=None,
            username=None, password=None, guest_password=None,
            guest_username=None):
        """Create Vmrun object."""
        self.username = username
        self.password = password
        self.path = path_to_vmx_file
        self.host_type = host_type
        self.host_name = host_name
        self.host_port = host_port
        self.guest_password = guest_password
        self.guest_username = guest_username
        super(Vmrun, self).__init__()

    def set_path_to_vmx_file(self, path_to_vmx_file):
        """Set new path to vmx_file."""
        self.path = path_to_vmx_file

    def __create_vrun_command(self):
        """Add to vmrun command AUTHENTICATION-FLAGS."""
        cmd = ['vmrun -T {0}'.format(self.host_type)]
        if self.host_port:
            cmd.append('-P {}'.format(self.host_port))
        if self.host_name:
            cmd.append('-h {}'.format(self.host_name))
        if self.username:
            cmd.append('-u {}'.format(self.username))
            assert_true(self.password is not None)
            cmd.append('-p {}'.format(self.password))
        if self.guest_password:
            cmd.append('-vp {}'.format(self.guest_password))
            assert_true(self.guest_username is not None)
            cmd.append('-gu {}'.format(self.guest_username))
        return cmd

    def __execute(self, command):
        """Execute command.

        :param command: type string
        """
        cmd = self.__create_vrun_command()
        cmd.extend([command, self.path])
        command_to_run = ' '.join(cmd)
        logger.info('{}'.format(command_to_run))
        subprocess.check_call(command_to_run, shell=True)

    # Power actions
    def start(self):
        """Start a virtual machine on an ESXI host."""
        self.__execute('start')

    def stop(self):
        """Stopping a virtual machine on an ESXI host."""
        self.__execute('stop')

    def reset(self):
        """Reset a virtual machine on an ESXI host."""
        self.__execute('reset')
