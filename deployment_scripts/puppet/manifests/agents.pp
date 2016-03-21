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

notice('MODULAR: fuel-plugin-vmware-dvs/agent')

$vcenter    = hiera_hash('vcenter', {})
$vmware_dvs = hiera_hash('fuel-plugin-vmware-dvs', {})
$neutron    = hiera_hash('neutron_config', {})
$n_fqdn     = hiera('fqdn')
$roles      = hiera_array('roles', {})
$agents     = get_agents_data($vcenter, $neutron, $vmware_dvs, $n_fqdn, $roles)

$defaults   = {
  'neutron_url_timeout' => '3600',
  'py_root'             => '/usr/lib/python2.7/dist-packages',
}

create_resources(vmware_dvs::agent, $agents, $defaults)
