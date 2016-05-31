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

notice('MODULAR: fuel-plugin-vmware-dvs/restart-nova-compute')

$vcenter    = hiera('vcenter_hash')
$vc_setting = parse_vcenter_settings($vcenter['computes'])

$defaults   = {
  'current_node'   => hiera('fqdn'),
  'role'           => inline_template('<% if File.exist?("/etc/controller.yaml") or File.exist?("/etc/primary-controller.yaml") -%>controller<% end -%>'),
}

create_resources(vmware_dvs::ha_nova_restart, $vc_setting, $defaults)
