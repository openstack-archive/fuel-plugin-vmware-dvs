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

# edit /etc/neutron/neturon.conf and /etc/neutron/plugin.ini
# recreate net04 and net04_ext on primary-controller
# restart the neutron-server
class vmware_dvs(
  $vsphere_hostname,
  $vsphere_login,
  $vsphere_password,
  $network_maps,
  $neutron_physnet,
  $primary_controller,
  $nets,
  $keystone_admin_tenant,
  $driver_name         = 'vmware_dvs',
)
{
  $true_network_maps = get_network_maps($network_maps, $neutron_physnet)

  neutron_config {
    'DEFAULT/notification_driver': value => 'messagingv2';
    'DEFAULT/notification_topics': value => 'vmware_dvs';
  }

  neutron_plugin_ml2 {
    'ml2_vmware/vsphere_hostname': value => $vsphere_hostname;
    'ml2_vmware/vsphere_login':    value => $vsphere_login;
    'ml2_vmware/vsphere_password': value => $vsphere_password;
    'ml2_vmware/network_maps':     value => $true_network_maps;
  }

  ini_subsetting {'vmware_dvs_driver':
    path                 => '/etc/neutron/plugin.ini',
    section              => 'ml2',
    setting              => 'mechanism_drivers',
    subsetting           => $driver_name,
    subsetting_separator => ','
  }
  if $primary_controller {

    Service<| title == 'neutron-server' |> ->
    Openstack::Network::Create_network <||>

    Service<| title == 'neutron-server' |> ->
    Openstack::Network::Create_router <||>

    openstack::network::create_network{'net04':
      netdata => $nets['net04']
      } ->
      openstack::network::create_network{'net04_ext':
        netdata => $nets['net04_ext']
        } ->
        openstack::network::create_router{'router04':
          internal_network => 'net04',
          external_network => 'net04_ext',
          tenant_name      => $keystone_admin_tenant
        }
  }
}
