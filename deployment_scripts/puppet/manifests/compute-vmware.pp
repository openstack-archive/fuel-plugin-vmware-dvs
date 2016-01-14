notice('MODULAR: fuel-plugin-vmware-dvs/compute-vmware')

include ::nova::params

$neutron          = hiera_hash('neutron_config')
$nova_hash        = hiera_hash('nova')

$management_vip   = hiera('management_vip')
$service_endpoint = hiera('service_endpoint', $management_vip)
$neutron_endpoint = hiera('neutron_endpoint', $management_vip)
$adm_password     = try_get_value($neutron, 'keystone/admin_password')
$adm_tenant_name  = try_get_value($neutron, 'keystone/admin_tenant', 'services')
$adm_username     = try_get_value($neutron,'keystone/admin_user','neutron')
$region_name      = hiera('region', 'RegionOne')
$auth_api_version = 'v2.0'
$adm_identity_uri = "http://${service_endpoint}:35357"
$adm_auth_url     = "${admin_identity_uri}/${auth_api_version}"
$neutron_url      = "http://${neutron_endpoint}:9696"
$py_root          = '/usr/lib/python2.7/dist-packages'

class {'::nova::network::neutron':
  neutron_admin_password    => $adm_password,
  neutron_admin_tenant_name => $adm_tenant_name,
  neutron_region_name       => $region_name,
  neutron_admin_username    => $adm_username,
  neutron_admin_auth_url    => $adm_auth_url,
  neutron_url               => $neutron_url,
  neutron_url_timeout       => '3600',
  neutron_timeout           => '3600',
}

file {"${py_root}/nova.patch":
  source => 'puppet:///modules/vmware_dvs/nova.patch',
  notify => Exec['apply-nova-patch'],
}
exec {'apply-nova-patch':
  path        => '/usr/bin:/usr/sbin:/bin',
  command     => "patch -d ${py_root} -N -p1 < ${py_root}/nova.patch",
  refreshonly => true,
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
