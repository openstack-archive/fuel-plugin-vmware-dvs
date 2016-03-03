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
import time


from fuelweb_test import logger
from fuelweb_test.helpers import os_actions
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import NEUTRON_SEGMENT_TYPE
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic


from helpers import openstack
from helpers import plugin

from proboscis import test
from proboscis.asserts import assert_true


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

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_regression"])
    @log_snapshot_after_test
    def dvs_regression(self):
        """Deploy cluster with plugin and vmware datastore backend.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller+mongo+cinder-vmware role.
            5. Add 2 node with compute role.
            6. Add 1 node with compute-vmware role.
            7. Deploy the cluster.
            8. Run OSTF.
            9. Create non default network.
            10. Create Security groups
            11. Launch instances with created network in nova and vcenter az.
            12. Attached created security groups to instances.
            13. Check connection between instances from different az.

        Duration: 1.8 hours
        """
        self.env.revert_snapshot("ready_with_9_slaves")
        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())
        # Configure cluster with 2 vcenter clusters and vcenter glance
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                "images_vcenter": True
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web)
        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller', 'mongo', 'cinder-vmware'],
             'slave-02': ['controller', 'mongo', 'cinder-vmware'],
             'slave-03': ['controller', 'mongo', 'cinder-vmware'],
             'slave-04': ['compute'],
             'slave-05': ['compute'],
             'slave-06': ['compute-vmware']}
        )
        # Configure VMWare vCenter settings
        target_node_2 = self.node_name('slave-06')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_2=target_node_2,
            multiclusters=True,
            vc_glance=True
        )
        self.fuel_web.deploy_cluster_wait(cluster_id)
        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke', 'tests_platform'])

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)
        # Create non default network with subnet.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = openstack.create_network(
            os_conn,
            self.net_data[0].keys()[0],
            tenant_name=SERVTEST_TENANT
        )
        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = openstack.create_subnet(
            os_conn,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name=SERVTEST_TENANT
        )
        # Check that network are created.
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )
        # Add net_1 to default router
        # Add net_1 to default router
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        openstack.add_subnet_to_router(
            os_conn,
            router['id'], subnet['id'])
        # Launch instance 2 VMs of vcenter and 2 VMs of nova
        # in the tenant network net_01
        openstack.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network['id']}]
        )
        # Launch instance 2 VMs of vcenter and 2 VMs of nova
        # in the default network
        network = os_conn.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}])
        openstack.verify_instance_state(os_conn)
        openstack.create_and_assign_floating_ip(os_conn=os_conn)
        # Create security groups SG_1 to allow ICMP traffic.
        # Add Ingress rule for ICMP protocol to SG_1
        # Create security groups SG_2 to allow TCP traffic 22 port.
        # Add Ingress rule for TCP protocol to SG_2
        sec_name = ['SG1', 'SG2']
        sg1 = os_conn.nova.security_groups.create(
            sec_name[0], "descr")
        sg2 = os_conn.nova.security_groups.create(
            sec_name[1], "descr")
        rulesets = [
            {
                # ssh
                'ip_protocol': 'tcp',
                'from_port': 22,
                'to_port': 22,
                'cidr': '0.0.0.0/0',
            },
            {
                # ping
                'ip_protocol': 'icmp',
                'from_port': -1,
                'to_port': -1,
                'cidr': '0.0.0.0/0',
            }
        ]
        os_conn.nova.security_group_rules.create(
            sg1.id, **rulesets[0]
        )
        os_conn.nova.security_group_rules.create(
            sg2.id, **rulesets[1]
        )
        # Remove default security group and attach SG_1 and SG2 to VMs
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv.remove_security_group(srv.security_groups[0]['name'])
            srv.add_security_group(sg1.id)
            srv.add_security_group(sg2.id)
        time.sleep(20)  # need wait to update rules on dvs
        # SSh to VMs
        # Check ping between VMs
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name)
        openstack.check_connection_vms(
            os_conn=os_conn, srv_list=srv_list,
            remote=ssh_controller)
