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

# === Parameters
#
# [*admin_password*]
#   (required) String. The admin's password
#
# [*admin_tenant_name*]
#   (required) String. Name of the tenant's admin
#
# [*region_name*]
#   (required) String.
#
# [*admin_username*]
#   (required) String.
#
# [*admin_auth_url*]
#   (required) String.
#
# [*neutron_url*]
#   (required) String.
#
# [*neutron_url_timeout*]
#   (optional) String.
#

class vmware_dvs::compute(
  $admin_password,
  $admin_tenant_name,
  $region_name,
  $admin_username,
  $admin_auth_url,
  $neutron_url,
  $neutron_url_timeout = '3600',
)
{
  include ::nova::params

  class {'::nova::network::neutron':
    neutron_admin_password    => $admin_password,
    neutron_admin_tenant_name => $admin_tenant_name,
    neutron_region_name       => $region_name,
    neutron_admin_username    => $admin_username,
    neutron_admin_auth_url    => $admin_auth_url,
    neutron_url               => $neutron_url,
    neutron_url_timeout       => $neutron_url_timeout,
  }

  augeas { 'sysctl-net.bridge.bridge-nf-call-arptables':
    context => '/files/etc/sysctl.conf',
    changes => "set net.bridge.bridge-nf-call-arptables '1'",
  }
  augeas { 'sysctl-net.bridge.bridge-nf-call-iptables':
    context => '/files/etc/sysctl.conf',
    changes => "set net.bridge.bridge-nf-call-iptables '1'",
  }
  augeas { 'sysctl-net.bridge.bridge-nf-call-ip6tables':
    context => '/files/etc/sysctl.conf',
    changes => "set net.bridge.bridge-nf-call-ip6tables '1'",
  }

  service { 'nova-compute':
    ensure => 'running',
    name   => $::nova::params::compute_service_name,
  }
  Nova_config<| |> ~> Service['nova-compute']

  if($::operatingsystem == 'Ubuntu') {
    tweaks::ubuntu_service_override { 'nova-network':
      package_name => 'nova-network',
    }
  }

}
