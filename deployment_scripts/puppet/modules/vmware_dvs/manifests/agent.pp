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

# === Parameters
#
# [*host*]
#   (required) String. The host parameter for nova-compute process
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
#   (required) String. This is the timeout for neutron.
#
# [*py_root*]
#   (required) String. Path for python's dist-packages.


define vmware_dvs::agent(
  $host                = 'vcenter-servicename',
  $vsphere_hostname    = '192.168.0.1',
  $vsphere_login       = 'administrator@vsphere.local',
  $vsphere_password    = 'StrongPassword!',
  $network_maps        = 'physnet1:dvSwitch1',
  $neutron_url_timeout = '3600',
  $py_root             = '/usr/lib/python2.7/dist-packages',
)
{

  $agent_config = "/etc/neutron/plugins/ml2/vmware_dvs-${host}.ini"
  $agent_name   = "neutron-plugin-vmware-dvs-agent-${host}"
  $agent_init   = "/etc/init/${agent_name}.conf"
  $agent_log    = "/var/log/neutron/vmware-dvs-agent-${host}.log"

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

  file {$agent_config:
    ensure  => present,
    content => template('vmware_dvs/agent_config.erb'),
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
  }

  file {$agent_init:
    ensure  => present,
    content => template('vmware_dvs/agent_init.erb'),
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
  }->
  exec {"start_${agent_name}":
    path    => '/usr/sbin:/sbin:/usr/bin:/bin',
    command => "service ${agent_name} restart",
  }
}
