#    Copyright 2015 Mirantis, Inc.
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

notice('MODULAR: fuel-plugin-vmware-dvs')

$vcenter          = hiera_hash('vcenter', {})
$computes         = $vcenter['computes'][0]
$vsphere_hostname = $computes['vc_host']
$vsphere_login    = $computes['vc_user']
$vsphere_password = $computes['vc_password']

$neutron          = hiera_hash('neutron_config', {})
$py_root          = '/usr/lib/python2.7/dist-packages'
$ml2_driver_path  = 'neutron/plugins/ml2/drivers/mech_vmware_dvs'
$ml2_plugin_path  = 'neutron/cmd/eventlet/plugins/dvs_neutron_agent.py'
$driver_path      = "${py_root}/${ml2_driver_path}"
$plugin_path      = "${py_root}/${ml2_plugin_path}"

class {'::vmware_dvs':
  vsphere_hostname => $vsphere_hostname,
  vsphere_login    => $vsphere_login,
  vsphere_password => $vsphere_password,
  driver_path      => $driver_path,
  plugin_path      => $plugin_path,
}
