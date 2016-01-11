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
# [*path*]
#   (required) String. The path to the mech_vmware_dvs ml2 driver.
#

class vmware_dvs::neutron_server(
  $path = 'filepath',
)
{
  service { 'neutron-server':
    ensure    => running,
    enable    => true,
    subscribe => File[$path],
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
}
