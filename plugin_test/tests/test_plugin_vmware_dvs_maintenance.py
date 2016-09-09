"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

from proboscis import test
from proboscis.asserts import assert_true

import fuelweb_test.tests.base_test_case
from fuelweb_test import logger
from fuelweb_test.helpers import os_actions
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
from helpers import openstack

from tests.test_plugin_vmware_dvs_smoke import TestDVSBVT


TestBasic = fuelweb_test.tests.base_test_case.TestBasic


@test(groups=["plugins"])
class TestDVSMaintenance(TestBasic):
    """Test suite for check functional of DVS plugin after FUEL/MOS updates."""

    # constants
    net_data = [{'net_1': '192.168.112.0/24'},
                {'net_2': '192.168.113.0/24'}]

    # defaults
    ext_net_name = openstack.get_defaults()['networks']['floating']['name']
    inter_net_name = openstack.get_defaults()['networks']['internal']['name']

    def node_name(self, name_node):
        """Get node by name."""
        return self.fuel_web.get_nailgun_node_by_name(name_node)['hostname']

    @test(depends_on=[TestDVSBVT.dvs_vcenter_bvt],
          groups=["dvs_regression"])
    @log_snapshot_after_test
    def dvs_regression(self):
        """Deploy cluster with plugin and vmware datastore backend.

        Scenario:
            1. Revert to dvs_bvt snapshot.
            2. Create non default network net_1.
            3. Launch instances with created network in nova and vcenter az.
            4. Create Security groups.
            5. Attached created security groups to instances.
            6. Check connection between instances from different az.

        Duration: 1.8 hours
        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_bvt")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = os_conn.get_tenant(SERVTEST_TENANT)

        # Create non default network with subnet
        self.show_step(2)

        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        net_1 = os_conn.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet = os_conn.create_subnet(
            subnet_name=net_1['name'],
            network_id=net_1['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # Check that network are created
        assert_true(os_conn.get_network(net_1['name'])['id'] == net_1['id'])

        # Add net_1 to default router
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        os_conn.add_router_interface(router_id=router["id"],
                                     subnet_id=subnet["id"])

        self.show_step(3)

        # Launch 2 vcenter VMs and 2 nova VMs in the tenant network net_01
        openstack.create_instances(os_conn=os_conn,
                                   vm_count=1,
                                   nics=[{'net-id': net_1['id']}])

        # Launch 2 vcenter VMs and 2 nova VMs in the default network
        net_1 = os_conn.nova.networks.find(label=self.inter_net_name)
        instances = openstack.create_instances(os_conn=os_conn,
                                               vm_count=1,
                                               nics=[{'net-id': net_1.id}])
        openstack.verify_instance_state(os_conn)

        self.show_step(4)

        # Create security groups SG_1 to allow ICMP traffic.
        # Add Ingress rule for ICMP protocol to SG_1
        # Create security groups SG_2 to allow TCP traffic 22 port.
        # Add Ingress rule for TCP protocol to SG_2
        sec_name = ['SG1', 'SG2']
        sg1 = os_conn.nova.security_groups.create(sec_name[0], "descr")
        sg2 = os_conn.nova.security_groups.create(sec_name[1], "descr")
        rulesets = [{
            # ssh
            'ip_protocol': 'tcp',
            'from_port': 22,
            'to_port': 22,
            'cidr': '0.0.0.0/0',
        }, {
            # ping
            'ip_protocol': 'icmp',
            'from_port': -1,
            'to_port': -1,
            'cidr': '0.0.0.0/0',
        }]
        os_conn.nova.security_group_rules.create(sg1.id, **rulesets[0])
        os_conn.nova.security_group_rules.create(sg2.id, **rulesets[1])

        # Remove default security group and attach SG_1 and SG2 to VMs
        self.show_step(5)

        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv.remove_security_group(srv.security_groups[0]['name'])
            srv.add_security_group(sg1.id)
            srv.add_security_group(sg2.id)
        fip = openstack.create_and_assign_floating_ips(os_conn, instances)

        # Check ping between VMs
        self.show_step(6)

        ip_pair = dict.fromkeys(fip)
        for key in ip_pair:
            ip_pair[key] = [value for value in fip if key != value]
        openstack.check_connection_vms(ip_pair)
