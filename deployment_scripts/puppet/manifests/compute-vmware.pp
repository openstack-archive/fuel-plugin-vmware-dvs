notice('MODULAR: fuel-plugin-vmware-dvs/compute-vmware')

include nova::params

$neutron_config = hiera_hash('neutron_config')
$nova_hash = hiera_hash('nova')

$management_vip     = hiera('management_vip')
$service_endpoint   = hiera('service_endpoint', $management_vip)
$neutron_endpoint   = hiera('neutron_endpoint', $management_vip)
$admin_password     = try_get_value($neutron_config, 'keystone/admin_password')
$admin_tenant_name  = try_get_value($neutron_config,
                                  'keystone/admin_tenant', 'services')
$admin_username     = try_get_value($neutron_config,
                                  'keystone/admin_user', 'neutron')
$region_name        = hiera('region', 'RegionOne')
$auth_api_version   = 'v2.0'
$admin_identity_uri = "http://${service_endpoint}:35357"
$admin_auth_url     = "${admin_identity_uri}/${auth_api_version}"
$neutron_url        = "http://${neutron_endpoint}:9696"

class {'nova::network::neutron':
  neutron_admin_password    => $admin_password,
  neutron_admin_tenant_name => $admin_tenant_name,
  neutron_region_name       => $region_name,
  neutron_admin_username    => $admin_username,
  neutron_admin_auth_url    => $admin_auth_url,
  neutron_url               => $neutron_url,
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
