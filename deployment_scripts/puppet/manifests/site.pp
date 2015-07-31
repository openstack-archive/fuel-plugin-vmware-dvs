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

$vc_hash = hiera('vcenter', {})
$vsphere_hostname  = inline_template('<%= @vc_hash["computes"][0]["vc_host"] %>')
$vsphere_login     = inline_template('<%= @vc_hash["computes"][0]["vc_user"] %>')
$vsphere_password  = inline_template('<%= @vc_hash["computes"][0]["vc_password"] %>')

class {'vmware_dvs':
  vsphere_hostname => $vsphere_hostname,
  vsphere_login    => $vsphere_login,
  vsphere_password => $vsphere_password,
  driver_name      => 'vmware_dvs'
}
