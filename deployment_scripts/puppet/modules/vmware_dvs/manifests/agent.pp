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
  $use_fw_driver       = true,
  $neutron_url_timeout = '3600',
  $py_root             = '/usr/lib/python2.7/dist-packages',
  $ha_enabled          = true,
  $primary             = false,
)
{
  $neutron_conf = '/etc/neutron/neutron.conf'
  $ml2_conf     = '/etc/neutron/plugin.ini'
  $ocf_dvs_name = 'ocf-neutron-dvs-agent'
  $ocf_dvs_res  = "/usr/lib/ocf/resource.d/fuel/${ocf_dvs_name}"
  $agent_config = "/etc/neutron/plugins/ml2/vmware_dvs-${host}.ini"
  $agent_name   = "neutron-plugin-vmware-dvs-agent-${host}"
  $agent_init   = "/etc/init/${agent_name}.conf"
  $agent_initd  = "/etc/init.d/${agent_name}"
  $agent_log    = "/var/log/neutron/vmware-dvs-agent-${host}.log"
  $ocf_pid_dir  = '/var/run/resource-agents/ocf-neutron-dvs-agent'
  $ocf_pid      = "${ocf_pid_dir}/${agent_name}.pid"

  if $use_fw_driver {
    $fw_driver = 'mech_vmware_dvs.agentDVS.vCenter_firewall.DVSFirewallDriver'
  }
  else {
    $fw_driver = 'mech_vmware_dvs.agentDVS.noop.vCenterNOOP'
  }


  if ! defined(Nova_config['neutron/url_timeout']) {
    nova_config {'neutron/url_timeout': value => $neutron_url_timeout}
  }

  if ! defined(File["${py_root}/nova.patch"]) {
    file {"${py_root}/nova.patch":
      source => 'puppet:///modules/vmware_dvs/nova.patch',
      notify => Exec['apply-nova-patch'],
    }
  }
  if ! defined(Exec['apply-nova-patch']) {
    exec {'apply-nova-patch':
      path        => '/usr/bin:/usr/sbin:/bin:/sbin',
      command     => "patch -d ${py_root} -N -p1 < ${py_root}/nova.patch",
      refreshonly => true,
    }
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
  }

  file {$agent_initd:
    ensure  => present,
    content => template('vmware_dvs/agent_init.d.erb'),
    owner   => 'root',
    group   => 'root',
    mode    => '0755',
  }

  if $ha_enabled {
    if ! defined(File[$ocf_dvs_res]) {
      file {$ocf_dvs_res:
        source => "puppet:///modules/vmware_dvs/${ocf_dvs_name}",
        owner  => 'root',
        group  => 'root',
        mode   => '0755',
      }
    }

    service {$agent_name: }

    cluster::corosync::cs_service{$agent_name:
      ocf_script       => $ocf_dvs_name,
      csr_complex_type => 'clone',
      csr_ms_metadata  => {
        'interleave' => true
      },
      csr_parameters   => {
        'plugin_config'         => $ml2_conf,
        'additional_parameters' => "--config-file=${agent_config}",
        'log_file'              => $agent_log,
        'pid'                   => $ocf_pid,
      },
      csr_mon_intr     => '20',
      csr_mon_timeout  => '10',
      csr_timeout      => '80',
      service_name     => $agent_name,
      package_name     => $agent_name,
      service_title    => $agent_name,
      primary          => $primary,
      hasrestart       => false,
    }
  }
  else {
      exec {"start_${agent_name}":
        path    => '/usr/sbin:/sbin:/usr/bin:/bin',
        command => "service ${agent_name} restart",
      }
  }

}
