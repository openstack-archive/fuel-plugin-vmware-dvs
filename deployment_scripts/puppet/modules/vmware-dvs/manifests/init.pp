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


class vmware-dvs(
  $vsphere_hostname,
  $vsphere_login,
  $vsphere_password,
  $driver_name,
  $network_maps = "physnet2:dvSwitch",
)
{
  neutron_config {
    'DEFAULT/notification_driver': value => 'messagingv2';
    'DEFAULT/notification_topics': value => 'vmware_dvs';
  }

  neutron_plugin_ml2 {
    'ml2_vmware/vsphere_hostname': value => $vsphere_hostname;
    'ml2_vmware/vsphere_login':    value => $vsphere_login;
    'ml2_vmware/vsphere_password': value => $vsphere_password;
    'ml2_vmware/network_maps':     value => 'physnet2:dvSwitch';
  }

  ini_subsetting {'vmware_dvs_driver':
    path       => '/etc/neutron/plugin.ini',
    section    => 'ml2',
    setting    => 'mechanism_drivers',
    subsetting => $driver_name,
    subsetting_separator => ','
  }
}
