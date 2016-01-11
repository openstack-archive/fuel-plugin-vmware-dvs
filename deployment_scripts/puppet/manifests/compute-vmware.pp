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

notice('MODULAR: fuel-plugin-vmware-dvs/compute-vmware')

$neutron_config     = hiera_hash('neutron_config')
$nova_hash          = hiera_hash('nova')

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

class {'::vmware_dvs::compute':
  admin_password      => $admin_password,
  admin_tenant_name   => $admin_tenant_name,
  region_name         => $region_name,
  admin_username      => $admin_username,
  admin_auth_url      => $admin_auth_url,
  neutron_url         => $neutron_url,
  neutron_url_timeout => '3600',
}
