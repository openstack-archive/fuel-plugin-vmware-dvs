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
#
# == Class: ::vmware_dvs
#
# edit /etc/neutron/neturon.conf and /etc/neutron/plugin.ini
# recreate net04 and net04_ext on primary-controller
# restart the neutron-server
#
# === Parameters
#
# [*vsphere_hostname*]
#   (required) String. This is a name or ip of VMware vSphere server.
#
# [*vsphere_login*]
#   (required) String. This is a name of VMware vSphere user.
#
# [*vsphere_password*]
#   (required) String. This is a password of VMware vSphere user.
#
# [*network_maps*]
#   (required) String. This is a name of DVS.
#
# [*neutron_physnet*]
#   (required) String. This is a name of physnet of neutron.
#
# [*nets*]
#   (required) String. This is a name of network in the admin's tenant.
#
# [*keystone_admin_tenant*]
#   (required) String. This is the admin tenant's name.
#
# [*driver_name*]
#   (optional) String. This is the name of installed driver.
#
# [*neutron_url_timeout*]
#   (optional) String. This is the timeout for neutron
#
# [*primary_controller*]
#   (optional) Boolean. Yes if its primary controller.
#

class vmware_dvs(
  $vsphere_hostname,
  $vsphere_login,
  $vsphere_password,
  $network_maps,
  $neutron_physnet,
  $nets,
  $keystone_admin_tenant,
  $driver_name         = 'vmware_dvs',
  $neutron_url_timeout = '3600',
  $primary_controller  = hiera('primary_controller')
)
{
  $true_network_maps = get_network_maps($network_maps, $neutron_physnet)

  package { 'yunesj-suds':
    ensure => present,
    name   => 'python-suds',
  }->
  package { 'install-dvs':
    ensure => present,
    name   => 'python-mech-vmware-dvs',
  }

  neutron_config {
    'DEFAULT/notification_driver': value => 'messagingv2';
    'DEFAULT/notification_topics': value => 'notifications,vmware_dvs';
  } ->

  neutron_plugin_ml2 {
    'ml2_vmware/vsphere_hostname': value => $vsphere_hostname;
    'ml2_vmware/vsphere_login':    value => $vsphere_login;
    'ml2_vmware/vsphere_password': value => $vsphere_password;
    'ml2_vmware/network_maps':     value => $true_network_maps;
  } ->

  ini_subsetting {'vmware_dvs_driver':
    path                 => '/etc/neutron/plugin.ini',
    section              => 'ml2',
    setting              => 'mechanism_drivers',
    subsetting           => $driver_name,
    subsetting_separator => ','
    }

    file_line { 'neutron_timeout':
      path  => '/etc/haproxy/conf.d/085-neutron.cfg',
      line  => '  timeout server 1h',
      after => 'listen neutron',
    }

  service { 'neutron-server':
    ensure    => running,
    enable    => true,
    subscribe => [Package['install-dvs'],Ini_Subsetting['vmware_dvs_driver']],
  }

  service {'haproxy':
    ensure     => running,
    hasrestart => true,
    restart    => '/sbin/ip netns exec haproxy service haproxy reload',
    subscribe  => File_Line['neutron_timeout'],
  }


  if $primary_controller and $nets and !empty($nets) {

    openstack::network::create_network{'net04':
      netdata => $nets['net04'],
      require => Service['neutron-server'],
      } ->
      openstack::network::create_network{'net04_ext':
        netdata => $nets['net04_ext'],
        } ->
        openstack::network::create_router{'router04':
          internal_network => 'net04',
          external_network => 'net04_ext',
          tenant_name      => $keystone_admin_tenant
        }
  }
}
