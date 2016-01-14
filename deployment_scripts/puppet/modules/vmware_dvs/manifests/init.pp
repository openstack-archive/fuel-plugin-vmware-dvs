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

# == Class: ::vmware_dvs
#
# edit /etc/neutron/neturon.conf and /etc/neutron/plugin.ini
#
# === Parameters
#
# [*vsphere_hostname*]
#   (required) String. This is the name or ip of VMware vSphere server
#
# [*vsphere_login*]
#   (required) String. This is the name of VMware vSphere user
#
# [*vsphere_password*]
#   (required) String. This is the password of VMware vSphere user
#
# [*network_maps*]
#   (required) String. This is a name of distributed vSwitch
#
# [*neutron_physnet*]
#   (required) String. This is a name of physnet of neutron.
#
# [*driver_name*]
#   (optional) String. This is the name of installed driver.
#
# [*neutron_url_timeout*]
#   (optional) String. This is the url timeout for neutron
#
# [*neutron_timeout*]
#   (optional) String. This is the timeout for neutron
#
# [*py_root*]
#   (optional) String. This is the path to the python's dist-packages dir.


class vmware_dvs(
  $vsphere_hostname,
  $vsphere_login,
  $vsphere_password,
  $network_maps,
  $neutron_physnet,
  $driver_name      = 'vmware_dvs',
  $neutron_timeout  = '3600',
  $py_root          = '/usr/lib/python2.7/dist-packages',
)
{
  $true_network_maps  = get_network_maps($network_maps, $neutron_physnet)

  Exec { path => '/usr/bin:/usr/sbin:/bin:/sbin' }

  package {['python-suds','python-mech-vmware-dvs']:
    ensure => present,
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

  file_line { 'neutron_timeout':
    path  => '/etc/haproxy/conf.d/085-neutron.cfg',
    line  => '  timeout server 1h',
    after => 'listen neutron',
  }

  service { 'neutron-server':
    ensure    => running,
    enable    => true,
    subscribe => [[Package['python-suds','python-mech-vmware-dvs']]],
  }

  service {'haproxy':
    ensure     => running,
    hasrestart => true,
    restart    => '/sbin/ip netns exec haproxy service haproxy reload',
    subscribe  => File_Line['neutron_timeout'],
  }

  nova_config {'neutron/timeout': value => $neutron_timeout}

  file {"${py_root}/nova.patch":
    source => 'puppet:///modules/vmware_dvs/nova.patch',
    notify => Exec['apply-nova-patch'],
  }
  exec {'apply-nova-patch':
    path        => '/usr/bin:/usr/sbin:/bin:/sbin',
    command     => "patch -d ${py_root} -N -p1 < ${py_root}/nova.patch",
    refreshonly => true,
  }
}
