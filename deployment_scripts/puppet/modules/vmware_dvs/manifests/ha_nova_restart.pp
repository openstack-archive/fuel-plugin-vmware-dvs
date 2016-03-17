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

define vmware_dvs::ha_nova_restart(
  $availability_zone_name,
  $vc_cluster,
  $vc_host,
  $vc_user,
  $vc_password,
  $service_name,
  $current_node,
  $target_node,
  $role,
  $datastore_regex    = undef,
  $api_retry_count    = 5,
  $maximum_objects    = 100,
  $nova_compute_conf  = '/etc/nova/nova-compute.conf',
  $task_poll_interval = 5.0,
  $use_linked_clone   = true,
  $wsdl_location      = undef,
  $service_enabled    = false,
)
{
  if $target_node =~ /controller/ and $role =~ /controller/ {

    $res = "p_nova_compute_vmware_${availability_zone_name}-${service_name}"
    exec {$res:
      path    => '/usr/bin:/usr/sbin:/bin:/sbin',
      command => "crm resource restart ${res}",
    }
  }

  if $target_node in $current_node {
    exec { 'nova-compute-restart':
      path    => '/usr/bin:/usr/sbin:/bin:/sbin',
      command => 'service nova-compute restart',
    }
  }

}
