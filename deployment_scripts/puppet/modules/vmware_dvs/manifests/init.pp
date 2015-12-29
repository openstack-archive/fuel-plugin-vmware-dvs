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
# install the vmware_dvs neutron ml2 driver and configure the neutron for it
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
# [*neutron_url_timeout*]
#   (optional) String. This is the timeout for neutron

class vmware_dvs(
  $vsphere_hostname    = '192.168.0.1',
  $vsphere_login       = 'administrator@vsphere.loc',
  $vsphere_password    = 'StrongPassword!',
  $network_maps        = 'physnet2:dvSwitch1',
  $neutron_url_timeout = '3600',
)
{
  $py_root = '/usr/lib/python2.7/dist-packages'
  neutron_config {
    'DEFAULT/notification_driver': value => 'messagingv2';
    'DEFAULT/notification_topics': value => 'notifications,vmware_dvs';
    }->
    neutron_plugin_ml2 {
      'ml2_vmware/vsphere_hostname': value => $vsphere_hostname;
      'ml2_vmware/vsphere_login':    value => $vsphere_login;
      'ml2_vmware/vsphere_password': value => $vsphere_password;
      'ml2_vmware/network_maps':     value => $network_maps;
      } ->
      package { ['python-suds','python-mech-vmware-dvs']:
        ensure => present,
        }->
        file {"${py_root}/neutron/plugins/ml2/drivers/mech_vmware_dvs":
          ensure => 'link',
          target => '/usr/local/lib/python2.7/dist-packages/mech_vmware_dvs',
        }

  service { 'neutron-server':
    ensure    => running,
    enable    => true,
    subscribe => File["${py_root}/neutron/plugins/ml2/drivers/mech_vmware_dvs"],
  }

  file_line { 'neutron_timeout':
    path  => '/etc/haproxy/conf.d/085-neutron.cfg',
    line  => '  timeout server 1h',
    after => 'listen neutron',
  }

  service {'haproxy':
    ensure     => running,
    hasrestart => true,
    restart    => '/sbin/ip netns exec haproxy service haproxy reload',
    subscribe  => File_Line['neutron_timeout'],
  }

  nova_config {'neutron/url_timeout': value => $neutron_url_timeout}

  file {"${py_root}/nova.patch":
    source => 'puppet:///modules/vmware_dvs/nova.patch',
    notify => Exec['apply-nova-patch'],
  }
  exec {'apply-nova-patch':
    path        => '/usr/bin:/usr/sbin:/bin:/sbin',
    command     => "patch -d ${py_root} -N -p1 < ${py_root}/nova.patch",
    refreshonly => true,
  }

  file {'dvs_neutron_agent.py':
    path   => "${py_root}/neutron/cmd/eventlet/plugins/dvs_neutron_agent.py",
    source => 'puppet:///modules/vmware_dvs/dvs_neutron_agent.py',
  }

  file {'neutron-dvs-agent':
    path    => '/usr/local/bin/neutron-dvs-agent',
    source  => 'puppet:///modules/vmware_dvs/neutron-dvs-agent',
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
    require => Package['python-mech-vmware-dvs'],
  }
}
