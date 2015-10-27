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

$vc_hash               = hiera('vcenter', {})
$dvs_hash              = hiera('fuel-plugin-vmware-dvs', {})
$neutron_hash          = hiera('quantum_settings', {})
$vsphere_hostname      = inline_template('<%= @vc_hash["computes"][0]["vc_host"] %>')
$vsphere_login         = inline_template('<%= @vc_hash["computes"][0]["vc_user"] %>')
$vsphere_password      = inline_template('<%= @vc_hash["computes"][0]["vc_password"] %>')
$dvs_network_maps      = inline_template('<%= @dvs_hash["vmware_dvs_net_maps"] %>')
$neutron_physnet       = inline_template('<%= @neutron_hash["predefined_networks"]["net04"]["L2"]["physnet"] %>')

class {'vmware_dvs':
  vsphere_hostname      => $vsphere_hostname,
  vsphere_login         => $vsphere_login,
  vsphere_password      => $vsphere_password,
  network_maps          => $dvs_network_maps,
  neutron_physnet       => $neutron_physnet,
  driver_name           => 'vmware_dvs',
  neutron_url_timeout   => '3600',
}
