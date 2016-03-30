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
# [*driver_path*]
#   (required) String. This is the ml2 driver's path.
#
# [*plugin_path*]
#   (required) String. This is the ml2 plugin's path.

class vmware_dvs(
  $vsphere_hostname = '192.168.0.1',
  $vsphere_login    = 'administrator@vsphere.loc',
  $vsphere_password = 'StrongPassword!',
  $plugin_path      = 'neutron/cmd/eventlet/plugins/dvs_neutron_agent.py',
)
{
  package { ['python-suds','python-networking-vsphere']:
    ensure => present,
    }->
    file {'/usr/lib/python2.7/dist-packages/neutron/plugins/ml2/drivers/networking_vsphere':
      ensure => 'link',
      target => '/usr/lib/python2.7/dist-packages/networking_vsphere'
    }

  file {'dvs_neutron_agent.py':
    path   => $plugin_path,
    source => 'puppet:///modules/vmware_dvs/dvs_neutron_agent.py',
  }
  neutron_config {
    'oslo_messaging_notifications/driver': value => 'messagingv2';
  }
  neutron_plugin_ml2 {
    'ml2_vmware/vsphere_hostname': value => $vsphere_hostname;
    'ml2_vmware/vsphere_login':    value => $vsphere_login;
    'ml2_vmware/vsphere_password': value => $vsphere_password;
  }
  file {'/etc/neutron/plugin.ini':
    ensure => 'link',
    target => '/etc/neutron/plugins/ml2/ml2_conf.ini',
  }
}
