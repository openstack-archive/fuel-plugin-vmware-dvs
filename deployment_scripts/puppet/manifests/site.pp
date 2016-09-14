#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

notice('MODULAR: fuel-plugin-vmware-dvs/site')

$py_root          = '/usr/lib/python2.7/dist-packages'
$ml2_plugin_path  = 'neutron/cmd/eventlet/plugins/dvs_neutron_agent.py'
$plugin_path      = "${py_root}/${ml2_plugin_path}"

class {'::vmware_dvs':
  plugin_path => $plugin_path,
}
