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
# [*vsphere_insecure*]
#   (optional) If true, the ESX/vCenter server certificate is not verified.
#   If false, then the default CA truststore is used for verification.
#   Defaults to 'True'.
#
# [*vsphere_ca_file*]
#   (optional) The hash name of the CA bundle file and data in format of:
#   Example:
#   "{"vc_ca_file"=>{"content"=>"RSA", "name"=>"vcenter-ca.pem"}}"
#   Defaults to undef.
#
# [*network_maps*]
#   (required) String. This is a name of DVS.
#
# [*neutron_url_timeout*]
#   (required) String. This is the timeout for neutron.
#
# [*use_fw_driver*]
#   (optional) Boolean. Use firewall driver or mock.
#
# [*py_root*]
#   (optional) String. Path for python's dist-packages.
#
# [*ha_enabled*]
#   (optional) Boolean. True for Corosync using.
#
# [*primary*]
#   (optional) Boolean. Parameter for using that cs_service.


define vmware_dvs::agent(
  $host                = 'vcenter-servicename',
  $vsphere_hostname    = '192.168.0.1',
  $vsphere_login       = 'administrator@vsphere.local',
  $vsphere_password    = 'StrongPassword!',
  $vsphere_insecure    = true,
  $vsphere_ca_file     = undef,
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

  $vcenter_ca_file     = pick($vsphere_ca_file, {})
  $vcenter_ca_content  = pick($vcenter_ca_file['content'], {})
  $vcenter_ca_filepath = "/etc/neutron/vmware-${host}-ca.pem"


  if $use_fw_driver {
    $fw_driver = 'networking_vsphere.agent.firewalls.vcenter_firewall.DVSFirewallDriver'
  }
  else {
    $fw_driver = 'networking_vsphere.agent.firewalls.noop_firewall.NoopvCenterFirewallDriver'
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

  if ! empty($vcenter_ca_content) and ! $vsphere_insecure {
    $agent_vcenter_ca_filepath   = $vcenter_ca_filepath
    $agent_vcenter_insecure_real = false

    file { $vcenter_ca_filepath:
      ensure  => file,
      content => $vcenter_ca_content,
      mode    => '0644',
      owner   => 'root',
      group   => 'root',
    }
  } else {
    $agent_vcenter_ca_filepath   = $::os_service_default
    $agent_vcenter_insecure_real = $vsphere_insecure
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

    $primitive_name     = "p_neutron_plugin_vmware_dvs_agent_${host}"
    $metadata           = {
      'resource-stickiness' => '1'
    }
    $parameters         = {
      'plugin_config'         => $ml2_conf,
      'additional_parameters' => "--config-file=${agent_config}",
      'log_file'              => $agent_log,
      'pid'                   => $ocf_pid,
    }
    $operations         = {
      'monitor'  => {
        'timeout' => '10',
        'interval' => '20',
      },
      'start'    => {
        'timeout' => '30',
        },
        'stop'     => {
          'timeout' => '30',
        }
      }
    exec {"clear_${primitive_name}":
      path    => '/usr/sbin:/sbin:/usr/bin:/bin',
      command => "crm_mon -1|grep ${primitive_name} && \
      pcs resource delete ${primitive_name} || \
      echo There is no ${primitive_name} here.",
    }

    pacemaker::service { $primitive_name :
      prefix             => false,
      primitive_class    => 'ocf',
      primitive_provider => 'fuel',
      primitive_type     => $ocf_dvs_name,
      metadata           => $metadata,
      parameters         => $parameters,
      operations         => $operations,
    }

    service { $primitive_name :
      ensure => 'running',
      enable => true,
    }

    Exec["clear_${primitive_name}"]->
    File[$agent_config]->
    File[$ocf_dvs_res]->
    Pcmk_resource[$primitive_name]->
    Service[$primitive_name]

  }
  else {
      exec {"start_${agent_name}":
        path    => '/usr/sbin:/sbin:/usr/bin:/bin',
        command => "service ${agent_name} restart",
      }
  }

}
