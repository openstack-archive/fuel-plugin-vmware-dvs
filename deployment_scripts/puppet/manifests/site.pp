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
$physnet          = $neutron["predefined_networks"]["admin_internal_net"]["L2"]["physnet"]

$vmware_dvs       = hiera_hash('fuel-plugin-vmware-dvs', {})
$vds              = $vmware_dvs['vmware_dvs_net_maps']
$network_maps     = "${physnet}:${vds}"

class {'::vmware_dvs':
  vsphere_hostname    => $vsphere_hostname,
  vsphere_login       => $vsphere_login,
  vsphere_password    => $vsphere_password,
  network_maps        => $network_maps,
  neutron_url_timeout => '3600',
}
