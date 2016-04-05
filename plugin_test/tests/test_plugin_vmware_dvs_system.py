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

from devops.error import TimeoutError

from devops.helpers.helpers import wait

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


@test(groups=["plugins", 'dvs_vcenter_system'])
class TestDVSSystem(TestBasic):
    """System test suite.

    The goal of integration and system testing is to ensure that new or
    modified components of Fuel and MOS work effectively with Fuel VMware
    DVS plugin without gaps in dataflow.
    """

    def node_name(self, name_node):
        """Get node by name."""
        return self.fuel_web.get_nailgun_node_by_name(name_node)['hostname']

    # constants
    net_data = [{'net_1': '192.168.112.0/24'},
                {'net_2': '192.168.113.0/24'}]

    # defaults
    ext_net_name = openstack.get_defaults()['networks']['floating']['name']
    inter_net_name = openstack.get_defaults()['networks']['internal']['name']
    instance_creds = (
        openstack.get_defaults()['os_credentials']['cirros']['user'],
        openstack.get_defaults()['os_credentials']['cirros']['password'])
    # security group rules
    tcp = {
        "security_group_rule":
            {"direction": "ingress",
             "port_range_min": "22",
             "ethertype": "IPv4",
             "port_range_max": "22",
             "protocol": "TCP",
             "security_group_id": "",
             "remote_group_id": None,
             "remote_ip_prefix": None}}
    icmp = {
        "security_group_rule":
            {"direction": "ingress",
             "ethertype": "IPv4",
             "protocol": "icmp",
             "security_group_id": "",
             "remote_group_id": None,
             "remote_ip_prefix": None}}

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_systest_setup", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_systest_setup(self):
        """Deploy cluster with plugin and vmware datastore backend.

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 2 node with compute role.
            6. Add 1 node with compute-vmware role.
            7. Deploy the cluster.
            8. Run OSTF.
            9. Create snapshot.

        Duration: 1.8 hours
        Snapshot: dvs_vcenter_systest_setup

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        self.show_step(1)
        self.show_step(2)
        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        self.show_step(3)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'images_vcenter': True
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web)

        self.show_step(4)
        self.show_step(5)
        self.show_step(6)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute-vmware'],
             'slave-03': ['compute'],
             'slave-04': ['compute']
             }
        )

        # Configure VMWare vCenter settings
        target_node_2 = self.node_name('slave-02')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_2=target_node_2,
            multiclusters=True,
            vc_glance=True
        )

        self.show_step(7)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(8)
        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        self.show_step(9)
        self.env.make_snapshot("dvs_vcenter_systest_setup", is_make=True)

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_networks", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_networks(self):
        """Check abilities to create and terminate networks on DVS.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Add 2 private networks net_1 and net_2.
            3. Check that networks are created.
            4. Delete net_1.
            5. Check that net_1 is deleted.
            6. Add net_1 again.

        Duration: 15 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        self.show_step(2)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        subnets = []
        networks = []
        tenant = os_conn.get_tenant(SERVTEST_TENANT)

        for net in self.net_data:
            logger.info('Create network {}'.format(net.keys()[0]))
            network = os_conn.create_network(
                network_name=net.keys()[0],
                tenant_id=tenant.id)['network']

            logger.info('Create subnet {}'.format(net.keys()[0]))
            subnet = os_conn.create_subnet(
                subnet_name=net.keys()[0],
                network_id=network['id'],
                cidr=net[net.keys()[0]],
                ip_version=4)

            subnets.append(subnet)
            networks.append(network)

        self.show_step(3)
        for network in networks:
            assert_true(
                os_conn.get_network(network['name'])['id'] == network['id']
            )

        self.show_step(4)
        logger.info('Delete network net_1')
        os_conn.neutron.delete_subnet(subnets[0]['id'])
        os_conn.neutron.delete_network(networks[0]['id'])

        self.show_step(5)
        assert_true(
            os_conn.get_network(networks[0]) is None
        )

        self.show_step(6)
        network = os_conn.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        logger.info('Create subnet {}'.format(net.keys()[0]))
        subnet = os_conn.create_subnet(
            subnet_name=self.net_data[0].keys()[0],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )
        logger.info('Networks net_1 and net_2 are present.')

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_ping_public", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_ping_public(self):
        """Check connectivity instances to public network with floating ip.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create private networks net01 with subnet.
            3. Add one  subnet (net01_subnet01: 192.168.101.0/24
            4. Create Router_01, set gateway and add interface
               to external network.
            5. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            6. Launch instances VM_3 and VM_4 in the net01
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            7. Send ping from instances to 8.8.8.8
               or other outside ip.

        Duration: 15 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = os_conn.get_tenant(SERVTEST_TENANT)

        self.show_step(2)
        network = os_conn.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        self.show_step(3)
        subnet = os_conn.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # Check that network are created.
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )

        self.show_step(4)
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        os_conn.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        # create security group with rules for ssh and ping
        security_group = os_conn.create_sec_group_for_ssh()

        self.show_step(5)
        self.show_step(6)
        instances = openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        # Get floating ip of instances.
        fip = openstack.create_and_assign_floating_ips(os_conn, instances)

        self.show_step(7)
        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        with self.fuel_web.get_ssh_for_node(controller.name) as ssh_contr:
            openstack.check_connection_vms(
                os_conn, fip, remote=ssh_contr,
                command='pingv4', destination_ip=['8.8.8.8'])

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_instances_one_group", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_instances_one_group(self):
        """Check creation instance in the one group simultaneously.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Launch few instances simultaneously with image TestVM
               and flavor m1.micro in nova availability zone
               in default internal network.
            3. Launch few instances simultaneously with image TestVM-VMDK
               and flavor m1.micro in vcenter availability zone in default
               internal network.
            4. Check connection between instances (ping, ssh).
            5. Delete all instances from horizon simultaneously.

        Duration: 15 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        logger.info(
            "Launch few instances in nova and vcenter availability zone"
        )
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        network = os_conn.nova.networks.find(label=self.inter_net_name)

        # create security group with rules for ssh and ping
        security_group = os_conn.create_sec_group_for_ssh()

        # Get max count of instance which we can create according to resource
        # limit
        vm_count = min(
            [os_conn.nova.hypervisors.resource_class.to_dict(h)['vcpus']
             for h in os_conn.nova.hypervisors.list()]
        )

        self.show_step(2)
        self.show_step(3)
        openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network.id}],
            vm_count=vm_count, security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        self.show_step(4)
        srv_list = os_conn.nova.servers.list()
        fip = openstack.create_and_assign_floating_ips(os_conn, srv_list)

        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0])

        with self.fuel_web.get_ssh_for_node(controller.name) as ssh_contr:
            openstack.check_connection_vms(
                os_conn, fip, remote=ssh_contr,
                command='pingv4')

        ip_pair = [
            (ip_1, ip_2)
            for ip_1 in fip
            for ip_2 in fip
            if ip_1 != ip_2]

        for ips in ip_pair:
            openstack.remote_execute_command(ips[0], ips[1], ' ')

        self.show_step(5)
        for srv in srv_list:
            os_conn.nova.servers.delete(srv)

        logger.info("Check that all instances were deleted.")
        for srv in srv_list:
            assert_true(
                os_conn.verify_srv_deleted(srv),
                "Verify server was deleted")

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_security", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_security(self):
        """Check abilities to create and delete security group.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create non default network with subnet net01.
            3. Launch 2 instances  of vcenter and 2 instances of nova
               in the tenant network net_01
            4. Launch 2 instances  of vcenter and 2 instances of nova
               in the default tenant network
            5. Create security group SG_1 to allow ICMP traffic.
            6. Add Ingress rule for ICMP protocol to SG_1
            7. Create security groups SG_2 to allow TCP traffic 22 port.
            8. Add Ingress rule for TCP protocol to SG_2
            9. Check ping is available between instances.
            10. Check ssh connection is available between instances.
            11. Delete all rules from SG_1 and SG_2
            12. Check that ssh aren't available to instances.
            13. Add Ingress and egress rules for TCP protocol to SG_2
            14. Check ssh connection is available between instances.
            15. Check ping is not available between instances.
            16. Add Ingress and egress rules for ICMP protocol to SG_1
            17. Check ping is available between instances.
            18. Delete Ingress rule for ICMP protocol from SG_1
                (if OS cirros skip this step)
            19. Add Ingress rule for ICMP ipv6 to SG_1
                (if OS cirros skip this step)
            20. Check ping6 between VM_1 and VM_2 and vice versa
                (if OS cirros skip this step)
            21. Delete SG1 and SG2 security groups.
            22. Attach instances to default security group.
            23. Check ping is available between instances.
            24. Check ssh is available between instances.

        Duration: 30 min

        """
        # constants
        wait_to_update_rules_on_dvs_ports = 30

        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = os_conn.get_tenant(SERVTEST_TENANT)

        self.show_step(2)
        network = os_conn.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet = os_conn.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0]['net_1'],
            ip_version=4)

        logger.info("Check that network are created.")
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )

        logger.info("Add net_1 to default router")
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        os_conn.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        self.show_step(3)
        openstack.create_instances(
            os_conn=os_conn,
            nics=[{'net-id': network['id']}],
            vm_count=1
        )
        openstack.verify_instance_state(os_conn)

        self.show_step(4)
        network = os_conn.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=os_conn,
            nics=[{'net-id': network.id}],
            vm_count=1
        )
        openstack.verify_instance_state(os_conn)

        # Remove default security group
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv.remove_security_group(srv.security_groups[0]['name'])
        os_conn.goodbye_security()

        self.show_step(5)
        sg1 = os_conn.nova.security_groups.create(
            'SG1', "descr")
        self.show_step(6)
        self.tcp["security_group_rule"]["security_group_id"] = sg1.id
        os_conn.neutron.create_security_group_rule(self.tcp)

        self.show_step(7)
        sg2 = os_conn.nova.security_groups.create(
            'SG2', "descr")
        self.show_step(8)
        self.icmp["security_group_rule"]["security_group_id"] = sg2.id
        os_conn.neutron.create_security_group_rule(self.icmp)

        logger.info("""Attach SG_1 and SG2 to instances""")
        for srv in srv_list:
            srv.add_security_group(sg1.id)
            srv.add_security_group(sg2.id)

        floating_ip = openstack.create_and_assign_floating_ips(
            os_conn, srv_list)

        self.show_step(9)
        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0])

        with self.fuel_web.get_ssh_for_node(controller.name) as ssh_contr:
            openstack.check_connection_vms(
                os_conn, floating_ip, remote=ssh_contr,
                command='pingv4')

            self.show_step(10)
            ip_pair = [(ip_1, ip_2)
                       for ip_1 in floating_ip
                       for ip_2 in floating_ip
                       if ip_1 != ip_2]

            for ips in ip_pair:
                openstack.remote_execute_command(ips[0], ips[1], ' ')

            self.show_step(11)
            sg_rules = [
                sg_rule for sg_rule
                in os_conn.neutron.list_security_group_rules()[
                    'security_group_rules']
                if sg_rule['security_group_id'] in [sg1.id, sg2.id]]
            for rule in sg_rules:
                os_conn.neutron.delete_security_group_rule(rule['id'])

            time.sleep(wait_to_update_rules_on_dvs_ports)

            self.show_step(12)
            for ip in floating_ip:
                try:
                    openstack.get_ssh_connection(
                        ip, self.instance_creds[0],
                        self.instance_creds[1])
                except Exception as e:
                    logger.info('{}'.format(e))

            self.show_step(13)
            self.tcp["security_group_rule"]["security_group_id"] = sg2.id
            os_conn.neutron.create_security_group_rule(self.tcp)
            self.tcp["security_group_rule"]["direction"] = "egress"
            os_conn.neutron.create_security_group_rule(self.tcp)

            time.sleep(wait_to_update_rules_on_dvs_ports)

            self.show_step(14)
            for ips in ip_pair:
                openstack.remote_execute_command(ips[0], ips[1], ' ')

            self.show_step(15)
            openstack.check_connection_vms(
                os_conn, floating_ip, remote=ssh_contr,
                command='pingv4', result_of_command=1)

            self.show_step(16)
            logger.info(
                "Add Ingress and egress rules for ICMP protocol to SG_1")
            self.icmp["security_group_rule"]["security_group_id"] = sg1.id
            os_conn.neutron.create_security_group_rule(self.icmp)
            self.icmp["security_group_rule"]["direction"] = "egress"
            os_conn.neutron.create_security_group_rule(self.icmp)

            time.sleep(wait_to_update_rules_on_dvs_ports)
            self.show_step(17)
            openstack.check_connection_vms(
                os_conn, floating_ip, remote=ssh_contr,
                command='pingv4')

            self.show_step(21)
            srv_list = os_conn.get_servers()
            for srv in srv_list:
                for sg in srv.security_groups:
                    srv.remove_security_group(sg['name'])
            self.show_step(22)
            for srv in srv_list:
                srv.add_security_group('default')

            time.sleep(wait_to_update_rules_on_dvs_ports)

            self.show_step(23)
            openstack.check_connection_vms(
                os_conn, floating_ip, remote=ssh_contr,
                command='pingv4')

            self.show_step(24)
            for ips in ip_pair:
                openstack.remote_execute_command(ips[0], ips[1], ' ')

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_tenants_isolation", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_tenants_isolation(self):
        """Connectivity between instances in different tenants.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create non-admin tenant.
            3. Create network net01 with subnet in non-admin tenant
            4. Create Router_01, set gateway and add interface
               to external network.
            5. Launch 2 instances in the net01(non-admin network)
               in nova and vcenter az.
            6. Launch 2 instances in the default internal
               admin network in nova and vcenter az.
            7. Verify that instances on different tenants should not
               communicate between each other via no floating ip.
               Send icmp ping from VM_3, VM_4 of admin tenant to VM_3 VM_4
               of test_tenant and vice versa.

        Duration: 30 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        self.show_step(2)
        admin.create_user_and_tenant('test', 'test', 'test')
        openstack.add_role_to_user(admin, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, 'test', 'test', 'test')

        tenant = test.get_tenant('test')

        self.show_step(3)
        network_test = test.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet_test = test.create_subnet(
            subnet_name=network_test['name'],
            network_id=network_test['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # create security group with rules for ssh and ping
        security_group_test = test.create_sec_group_for_ssh()

        self.show_step(4)
        router = test.create_router('router_1', tenant=tenant)
        test.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet_test["id"])

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        self.show_step(5)
        network = admin.nova.networks.find(label=self.inter_net_name)
        srv_1 = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network.id}], vm_count=1,
            security_groups=[security_group.name])
        openstack.verify_instance_state(admin)

        self.show_step(6)
        srv_2 = openstack.create_instances(
            os_conn=test, vm_count=1,
            nics=[{'net-id': network_test['id']}],
            security_groups=[security_group_test.name]
        )
        openstack.verify_instance_state(test)

        self.show_step(7)
        fip_1 = openstack.create_and_assign_floating_ips(admin, srv_1)
        ips_1 = []
        for srv in srv_1:
            ips_1.append(admin.get_nova_instance_ip(
                srv, net_name=self.inter_net_name))

        fip_2 = openstack.create_and_assign_floating_ips(test, srv_2)
        ips_2 = []
        for srv in srv_2:
            ips_2.append(test.get_nova_instance_ip(
                srv, net_name=network_test['name']))

        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        with self.fuel_web.get_ssh_for_node(controller.name) as ssh_contr:
            openstack.check_connection_vms(
                admin, fip_1, remote=ssh_contr,
                command='pingv4', destination_ip=ips_2, result_of_command=1)
            openstack.check_connection_vms(
                admin, fip_2, remote=ssh_contr,
                command='pingv4', destination_ip=ips_1, result_of_command=1)

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_same_ip", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_same_ip(self):
        """Connectivity between instances with same ip in different tenants.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create non-admin tenant.
            3. Create private network net01 with subnet in non-admin tenant.
            4. Create Router_01, set gateway and add interface
               to external network.
            5. Launch instances VM_1 and VM_2
               in the net01(non-admin tenant)
               with image TestVM and flavor m1.micro in nova az.
            6. Launch instances VM_3 and VM_4 in the net01(non-admin tenant)
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            7. Create private network net01 with subnet in default admin tenant
            8. Create Router_01, set gateway and add interface
               to external network.
            9. Launch instances VM_5 and VM_6
               in the net01(default admin tenant)
               with image TestVM and flavor m1.micro in nova az.
            10. Launch instances VM_7 and VM_8
               in the net01(default admin tenant)
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            11. Verify that VM_1, VM_2, VM_3 and VM_4 should communicate
               between each other via no floating ip.
            12. Verify that VM_5, VM_6, VM_7 and VM_8 should communicate
               between each other via no floating ip.

        Duration: 30 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant_admin = admin.get_tenant(SERVTEST_TENANT)

        self.show_step(2)
        admin.create_user_and_tenant('test', 'test', 'test')
        openstack.add_role_to_user(admin, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, 'test', 'test', 'test')

        tenant = test.get_tenant('test')

        self.show_step(3)
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = test.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet = test.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        self.show_step(4)
        router = test.create_router('router_1', tenant=tenant)
        test.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        # create security group with rules for ssh and ping
        security_group = test.create_sec_group_for_ssh()

        self.show_step(5)
        self.show_step(6)
        srv_1 = openstack.create_instances(
            os_conn=test, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(test)

        fip_1 = openstack.create_and_assign_floating_ips(test, srv_1)
        ips_1 = []
        for srv in srv_1:
            ips_1.append(test.get_nova_instance_ip(
                srv, net_name=network['name']))

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        self.show_step(7)
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = admin.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant_admin.id)['network']

        subnet = admin.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        self.show_step(8)
        router = admin.create_router('router_1', tenant=tenant_admin)
        admin.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        self.show_step(9)
        self.show_step(10)
        srv_2 = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name])
        openstack.verify_instance_state(admin)

        self.show_step(11)
        self.show_step(12)
        fip_2 = openstack.create_and_assign_floating_ips(admin, srv_2)
        ips_2 = []
        for srv in srv_2:
            ips_2.append(admin.get_nova_instance_ip(
                srv, net_name=network['name']))

        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )

        with self.fuel_web.get_ssh_for_node(controller.name) as ssh_contr:
            openstack.check_connection_vms(
                test, fip_1, remote=ssh_contr,
                command='pingv4', destination_ip=ips_1)
            openstack.check_connection_vms(
                admin, fip_2, remote=ssh_contr,
                command='pingv4', destination_ip=ips_2)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_volume", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_volume(self):
        """Deploy cluster with plugin and vmware datastore backend.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin on master node.
            3. Create a new environment with following parameters:
                    * Compute: KVM/QEMU with vCenter
                    * Networking: Neutron with VLAN segmentation
                    * Storage: default
                    * Additional services: default
            4. Add nodes with following roles:
                    * Controller
                    * Compute
                    * Cinder
                    * CinderVMware
                    * Compute-VMware
            5. Configure interfaces on nodes.
            6. Configure network settings.
            7. Enable and configure DVS plugin.
            8. Configure VMware vCenter Settings. Add 2 vSphere clusters
               and configure Nova Compute instances on conroller
               and compute-vmware
            9. Verify networks.
            10. Deploy cluster.
            11. Create instances for each of hypervisor's type.
            12. Create 2 volumes each in his own availability zone.
            13. Attach each volume to his instance.
            14. Check that each volume is attached to its instance.


        Duration: 1.8 hours

        """
        self.show_step(1)
        self.show_step(2)
        self.env.revert_snapshot("ready_with_5_slaves")
        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        self.show_step(3)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web)

        self.show_step(4)
        self.show_step(5)
        self.show_step(6)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute'],
             'slave-03': ['cinder'],
             'slave-04': ['cinder-vmware'],
             'slave-05': ['compute-vmware']
             }
        )

        self.show_step(8)
        logger.info('Configure VMware vCenter Settings.')
        target_node_2 = self.node_name('slave-05')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_2=target_node_2,
            multiclusters=True
        )

        self.show_step(10)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        # Create connection to openstack
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Get default security group
        default_sg = [
            sg
            for sg in admin.neutron.list_security_groups()['security_groups']
            if sg['tenant_id'] == admin.get_tenant(SERVTEST_TENANT).id
            if sg['name'] == 'default'][0]

        self.show_step(11)
        network = admin.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network.id}], vm_count=1,
            security_groups=[default_sg['name']])
        openstack.verify_instance_state(admin)

        self.show_step(12)
        volume_vcenter = openstack.create_volume(admin, 'vcenter-cinder')
        volume_nova = openstack.create_volume(admin, 'nova')
        instances = admin.nova.servers.list()
        instance_vcenter = [
            inst
            for inst in instances
            if inst.to_dict()['OS-EXT-AZ:availability_zone'] == 'vcenter'][0]
        instance_nova = [
            inst
            for inst in instances
            if inst.to_dict()['OS-EXT-AZ:availability_zone'] == 'nova'][0]

        self.show_step(13)
        admin.attach_volume(volume_vcenter, instance_vcenter)
        admin.attach_volume(volume_nova, instance_nova)

        self.show_step(14)
        assert_true(
            admin.cinder.volumes.get(volume_nova.id).status == 'in-use')

        assert_true(
            admin.cinder.volumes.get(volume_vcenter.id).status == 'in-use')

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_connect_default_net"])
    @log_snapshot_after_test
    def dvs_connect_default_net(self):
        """Check connectivity between VMs with same ip in different tenants.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Launch instances with image TestVM
               and flavor m1.micro in nova availability zone.
            3. Launch instances with image TestVM-VMDK
               and flavor m1.micro in vcenter availability zone.
            4. Verify that instances on different hypervisors
               should communicate between each other.
               Send icmp ping from VM_1 instances of vCenter to instances
               from Qemu/KVM and vice versa.

        Duration: 15 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")
        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        default_sg = [
            sg
            for sg in admin.neutron.list_security_groups()['security_groups']
            if sg['tenant_id'] == admin.get_tenant(SERVTEST_TENANT).id
            if sg['name'] == 'default'][0]

        network = admin.nova.networks.find(label=self.inter_net_name)

        # create access point server
        access_point, access_point_ip = openstack.create_access_point(
            os_conn=admin, nics=[{'net-id': network.id}],
            security_groups=[security_group.name, default_sg['name']])

        self.show_step(2)
        self.show_step(3)
        openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network.id}],
            vm_count=1,
            security_groups=[default_sg['name']])
        openstack.verify_instance_state(admin)

        # Get private ips of instances
        instances = [instance
                     for instance in admin.get_servers()
                     if instance.id != access_point.id]
        ips = []
        for instance in instances:
            ips.append(admin.get_nova_instance_ip(
                instance, net_name=self.inter_net_name))
        self.show_step(4)
        for ip in ips:
            for ip_2 in ips:
                if ip_2 != ip:
                    ping_result = openstack.remote_execute_command(
                        access_point_ip, ip, "ping -c 5 {}".format(ip_2))
                    assert_true(
                        ping_result['exit_code'] == 0,
                        "Ping isn't available from {0} to {1}".format(ip, ip_2)
                    )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_connect_nodefault_net"])
    @log_snapshot_after_test
    def dvs_connect_nodefault_net(self):
        """Check connectivity between VMs with same ip in different tenants.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create tenant net_01 with subnet.
            3. Launch instances with image TestVM
               and flavor m1.micro in nova availability zone in net_01.
            4. Launch instances with image TestVM-VMDK
               and flavor m1.micro in vcenter availability zone in net_01.
            5. Verify that instances on different hypervisors
               should communicate between each other.
               Send icmp ping from VM_1 instances of vCenter to instances
               from Qemu/KVM and vice versa.

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")
        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = admin.get_tenant(SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        default_sg = [
            sg
            for sg in admin.neutron.list_security_groups()['security_groups']
            if sg['tenant_id'] == admin.get_tenant(SERVTEST_TENANT).id
            if sg['name'] == 'default'][0]

        self.show_step(2)
        network = admin.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet = admin.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # Check that network are created.
        assert_true(
            admin.get_network(network['name'])['id'] == network['id']
        )
        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = admin.create_router(
            'router_1',
            tenant=tenant)

        # Add net_1 to router_1
        admin.add_router_interface(
            router_id=router_1["id"],
            subnet_id=subnet["id"])

        access_point, access_point_ip = openstack.create_access_point(
            os_conn=admin, nics=[{'net-id': network['id']}],
            security_groups=[security_group.name, default_sg['name']])

        self.show_step(3)
        self.show_step(4)
        openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}],
            vm_count=1,
            security_groups=[default_sg['name']])
        openstack.verify_instance_state(admin)

        # Get private ips of instances
        instances = [instance
                     for instance in admin.get_servers()
                     if instance.id != access_point.id]
        ips = []
        for instance in instances:
            ips.append(admin.get_nova_instance_ip(
                instance, net_name=network['name']))

        self.show_step(5)
        for ip in ips:
            for ip_2 in ips:
                if ip_2 != ip:
                    ping_result = openstack.remote_execute_command(
                        access_point_ip, ip, "ping -c 5 {}".format(ip_2))
                    assert_true(
                        ping_result['exit_code'] == 0,
                        "Ping isn't available from {0} to {1}".format(ip, ip_2)
                    )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_ping_without_fip"])
    @log_snapshot_after_test
    def dvs_ping_without_fip(self):
        """Check connectivity instances to public network without floating ip.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create private networks net01 with subnet.
            3. Add one  subnet (net01_subnet01: 192.168.101.0/24
            4. Create Router_01, set gateway and add interface to external net.
            5. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            6. Launch instances VM_3 and VM_4 in the net01
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            7. Send ping from instances to 8.8.8.8
               or other outside ip.

        Duration: 15 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")
        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = admin.get_tenant(SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        default_sg = [
            sg
            for sg in admin.neutron.list_security_groups()['security_groups']
            if sg['tenant_id'] == admin.get_tenant(SERVTEST_TENANT).id
            if sg['name'] == 'default'][0]

        self.show_step(2)
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = admin.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        self.show_step(3)
        subnet = admin.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # Check that network are created.
        assert_true(
            admin.get_network(network['name'])['id'] == network['id']
        )
        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = admin.create_router(
            'router_1',
            tenant=tenant)

        self.show_step(4)
        admin.add_router_interface(
            router_id=router_1["id"],
            subnet_id=subnet["id"])

        access_point, access_point_ip = openstack.create_access_point(
            os_conn=admin, nics=[{'net-id': network['id']}],
            security_groups=[security_group.name, default_sg['name']])

        self.show_step(5)
        self.show_step(6)
        openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}],
            vm_count=1,
            security_groups=[default_sg['name']])
        openstack.verify_instance_state(admin)

        # Get private ips of instances
        instances = [instance
                     for instance in admin.get_servers()
                     if instance.id != access_point.id]
        ips = []
        for instance in instances:
            ips.append(admin.get_nova_instance_ip(
                instance, net_name=network['name']))

        self.show_step(7)
        ip_2 = '8.8.8.8'
        for ip in ips:
            ping_result = openstack.remote_execute_command(
                access_point_ip, ip, "ping -c 5 {}".format(ip_2))
            assert_true(
                ping_result['exit_code'] == 0,
                "Ping isn't available from {0} to {1}".format(ip, ip_2)
            )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_different_networks"])
    @log_snapshot_after_test
    def dvs_different_networks(self):
        """Check connectivity between instances from different networks.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create private networks net01 and net02 with subnets.
            3. Create Router_01, set gateway and add interface to
               external network.
            4. Create Router_02, set gateway and add interface to
               external network.
            5. Attach private networks to Router_01.
            6. Attach private networks to Router_02.
            7. Launch instances in the net01
               with image TestVM and flavor m1.micro in nova az.
            8. Launch instances in the net01
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            9. Launch instances in the net02
               with image TestVM and flavor m1.micro in nova az.
            10. Launch instances in the net02
                with image TestVM-VMDK and flavor m1.micro in vcenter az.
            11. Verify that instances of same networks should communicate
                between each other via private ip.
                Send icmp ping between instances.
            12. Verify that instances of different networks should not
                communicate between each other via private ip.
            13. Delete net_02 from Router_02 and add it to the Router_01.
            14. Verify that instances of different networks should communicate
                between each other via private ip.
                Send icmp ping between instances.

        Duration: 15 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = admin.get_tenant(SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        default_sg = [
            sg
            for sg in admin.neutron.list_security_groups()['security_groups']
            if sg['tenant_id'] == admin.get_tenant(SERVTEST_TENANT).id
            if sg['name'] == 'default'][0]

        instances_group = []
        networks = []
        map_router_subnet = []
        step = 2
        self.show_step(step)
        for net in self.net_data:
            network = admin.create_network(
                network_name=net.keys()[0],
                tenant_id=tenant.id)['network']

            logger.info('Create subnet {}'.format(net.keys()[0]))
            subnet = admin.create_subnet(
                subnet_name=net.keys()[0],
                network_id=network['id'],
                cidr=net[net.keys()[0]],
                ip_version=4)

            # Check that network are created.
            assert_true(
                admin.get_network(network['name'])['id'] == network['id']
            )
            self.show_step(step + 1)
            router = admin.create_router(
                'router_0{}'.format(self.net_data.index(net) + 1),
                tenant=tenant)

            self.show_step(step + 3)
            admin.add_router_interface(
                router_id=router["id"],
                subnet_id=subnet["id"])

            access_point, access_point_ip = openstack.create_access_point(
                admin, [{'net-id': network['id']}],
                [security_group.name, default_sg['name']])
            if step == 3:
                step += 1
            self.show_step(step + 5)
            self.show_step(step + 6)
            openstack.create_instances(
                os_conn=admin, nics=[{'net-id': network['id']}],
                vm_count=1,
                security_groups=[default_sg['name']])
            openstack.verify_instance_state(admin)

            instances = [
                instance for instance in admin.get_servers()
                if network['name'] == instance.networks.keys()[0]
                if instance.id != access_point.id]

            private_ips = []
            for instance in instances:
                private_ips.append(admin.get_nova_instance_ip(
                    instance, net_name=network['name']))

            instances_group.append(
                {'access_point': access_point,
                 'access_point_ip': access_point_ip,
                 'private_ips': private_ips}
            )

            networks.append(network)
            map_router_subnet.append(
                {'subnet': subnet['id'], 'router': router['id']})
            step = 3
        self.show_step(11)

        for group in instances_group:
            for ip in group['private_ips']:
                for ip_2 in group['private_ips']:
                    if ip_2 != ip:
                        ping_result = openstack.remote_execute_command(
                            group['access_point_ip'],
                            ip, "ping -c 5 {}".format(ip_2))
                        assert_true(
                            ping_result['exit_code'] == 0,
                            "Ping isn't available from {0} to {1}".format(
                                ip, ip_2)
                        )

        self.show_step(12)
        for ip in instances_group[0]['private_ips']:
            for ip_2 in instances_group[1]['private_ips']:
                ping_result = openstack.remote_execute_command(
                    instances_group[0]['access_point_ip'],
                    ip, "ping -c 5 {}".format(ip_2))
                assert_true(
                    ping_result['exit_code'] == 1,
                    "Ping isn't available from {0} to {1}".format(ip, ip_2)
                )

        self.show_step(13)

        access_point_fip = instances_group[1]['access_point_ip']
        fip_id = [
            fip['id']
            for fip in admin.neutron.list_floatingips()['floatingips']
            if fip['floating_ip_address'] == access_point_fip][0]

        admin.neutron.delete_floatingip(fip_id)

        admin.neutron.remove_interface_router(
            map_router_subnet[1]['router'],
            {"subnet_id": map_router_subnet[1]['subnet']})

        admin.add_router_interface(
            router_id=map_router_subnet[0]['router'],
            subnet_id=map_router_subnet[1]['subnet'])
        time.sleep(20)  # need wait to port state update
        self.show_step(14)
        for ip in instances_group[1]['private_ips']:
            for ip_2 in instances_group[0]['private_ips']:
                ping_result = openstack.remote_execute_command(
                    instances_group[0]['access_point_ip'],
                    ip, "ping -c 5 {}".format(ip_2))
                assert_true(
                    ping_result['exit_code'] == 0,
                    "Ping isn't available from {0} to {1}".format(ip, ip_2)
                )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_heat"])
    @log_snapshot_after_test
    def dvs_heat(self):
        """Check connectivity between instances from different networks.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create stack with heat template.
            3. Check that stack was created.

        Duration: 15 min

        """
        # constants
        expect_state = 'CREATE_COMPLETE'
        boot_timeout = 300
        template_path = 'plugin_test/templates/dvs_stack.yaml'

        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        with open(template_path) as f:
            template = f.read()

        self.show_step(2)
        stack_id = os_conn.heat.stacks.create(
            stack_name='dvs_stack',
            template=template,
            disable_rollback=True
        )['stack']['id']

        self.show_step(3)
        try:
            wait(
                lambda:
                os_conn.heat.stacks.get(stack_id).stack_status == expect_state,
                timeout=boot_timeout)
        except TimeoutError:
            current_state = os_conn.heat.stacks.get(stack_id).stack_status
            assert_true(
                current_state == expect_state,
                "Timeout is reached. Current state of stack is {}".format(
                    current_state)
            )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_remote_sg_simple"])
    @log_snapshot_after_test
    def dvs_remote_sg_simple(self):
        """Simple remote security group rules.

        Verify that network traffic is allowed/prohibited to instances
        according security groups rules.

        Scenario:
            1. Setup for system tests.
            2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to
               the router01.
            3. Create security groups: SG1, SG2
            4. Delete all defaults egress rules of SG1 and SG2.
            5. Add icmp rule to SG1:
               Ingress rule with ip protocol 'icmp ', port range any, SG group
               'SG1'
               Egress rule with ip protocol 'icmp ', port range any, SG group
               'SG1'
            6. Add icmp rule to SG2:
               Ingress rule with ip protocol 'icmp ', port range any, SG group
               'SG2'
               Egress rule with ip protocol 'icmp ', port range any, SG group
               'SG2'
            7. Launch 2 instance of vcenter az with SG1 in net1.
               Launch 2 instance of nova az with SG1 in net1.
            8. Launch 2 instance of vcenter az with SG2 in net1.
               Launch 2 instance of nova az with SG2 in net1.
            9. Verify that icmp ping is enabled between VMs from SG1.
            10. Verify that icmp ping is enabled between instances from SG2.
            11. Verify that icmp ping is not enabled between instances from SG1
                and VMs from SG2.

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")
        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = admin.get_tenant(SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        self.show_step(2)
        network = admin.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet = admin.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # Check that network are created.
        assert_true(
            admin.get_network(network['name'])['id'] == network['id']
        )
        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = admin.create_router(
            'router_1',
            tenant=tenant)

        # Add net_1 to router_1
        admin.add_router_interface(
            router_id=router_1["id"],
            subnet_id=subnet["id"])

        self.show_step(3)
        sg1 = admin.nova.security_groups.create(
            'SG1', "descr")
        sg2 = admin.nova.security_groups.create(
            'SG2', "descr")

        self.show_step(4)
        sg_rules = [
            sg_rule for sg_rule
            in admin.neutron.list_security_group_rules()[
                'security_group_rules']
            if sg_rule['security_group_id'] in [sg1.id, sg2.id]]
        for rule in sg_rules:
            admin.neutron.delete_security_group_rule(rule['id'])
        self.show_step(5)
        self.show_step(6)
        for sg in [sg1, sg2]:
            for rule in [self.icmp, self.tcp]:
                rule["security_group_rule"]["security_group_id"] = sg.id
                rule["security_group_rule"]["remote_group_id"] = sg.id
                rule["security_group_rule"]["direction"] = "ingress"
                admin.neutron.create_security_group_rule(rule)
                rule["security_group_rule"]["direction"] = "egress"
                admin.neutron.create_security_group_rule(rule)

        # create access_point to instances from SG1 and SG2
        access_point, access_point_ip = openstack.create_access_point(
            os_conn=admin, nics=[{'net-id': network['id']}],
            security_groups=[security_group.name, sg1.name, sg2.name])

        self.show_step(7)
        istances_sg1 = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}],
            vm_count=1,
            security_groups=[sg1.name])

        self.show_step(8)
        istances_sg2 = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}],
            vm_count=1,
            security_groups=[sg2.name])
        openstack.verify_instance_state(admin)

        # Get private ips of instances
        ips = {}
        ips['SG1'] = [
            admin.get_nova_instance_ip(instance, net_name=network['name'])
            for instance in istances_sg1]
        ips['SG2'] = [
            admin.get_nova_instance_ip(instance, net_name=network['name'])
            for instance in istances_sg2]

        self.show_step(9)
        self.show_step(10)
        for group in ips:
            for ip_1 in ips[group]:
                for ip_2 in ips[group]:
                    if ip_2 != ip_1:
                        ping_result = openstack.remote_execute_command(
                            access_point_ip, ip_1, "ping -c 5 {}".format(ip_2),
                            wait=60 * 4)
                        assert_true(
                            ping_result['exit_code'] == 0,
                            "Ping isn't available from {0} to {1}".format(
                                ip_1, ip_2)
                        )

        self.show_step(11)
        for ip_1 in ips['SG1']:
            for ip_2 in ips['SG2']:
                ping_result = openstack.remote_execute_command(
                    access_point_ip, ip_1, "ping -c 5 {}".format(ip_2))
                assert_true(
                    ping_result['exit_code'] == 1,
                    "Ping is available from {0} to {1}".format(ip_1, ip_2)
                )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_remote_ip_prefix"])
    @log_snapshot_after_test
    def dvs_remote_ip_prefix(self):
        """Security group rules with remote ip prefix.

        Check connection between instances,
        according security group rules with remote ip prefix.

        Scenario:
            1. Setup for system tests.
            2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to
               the router01.
            3. Create instance 'VM1' of any availability zone in the
               default internal network. Associate floating ip.
            4. Create instance 'VM2' of any availability zone in the
               default internal network. Associate floating ip.
            5. Create security groups: SG1 SG2
            6. Delete all defaults egress rules of SG1 and SG2.
            7. Add icmp rule to SG1:
               Ingress rule with ip protocol 'icmp ', port range any,
               remote ip prefix <floating ip of VM1>
               Egress rule with ip protocol 'icmp ', port range any,
               remote ip prefix <floating ip of VM1>
            8. Add ssh rule to SG2:
               Ingress rule with ip protocol tcp ', port range any,
               <internal ip of VM2>
               Egress rule with ip protocol 'tcp ', port range any,
               <internal ip of VM2>
            9. Launch 2 instance 'VM3' and 'VM4' of vcenter az with SG1 and
               SG2 in net1.
               Launch 2 instance 'VM5' and 'VM6' of nova az with SG1 and SG2
               in net1.
            10. Verify that icmp ping is enabled from 'VM3', 'VM4', 'VM5' and
               'VM6' to VM1 and vice versa.
            11. Verify that icmp ping is blocked between 'VM3', 'VM4', 'VM5'
                and 'VM6' and vice versa.
            12. Verify that ssh is enabled from 'VM3', 'VM4', 'VM5' and 'VM6'
                to VM2 and vice versa.
            13. Verify that ssh is blocked between 'VM3', 'VM4', 'VM5' and
                'VM6' and vice versa.

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_vcenter_systest_setup")
        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        tenant = admin.get_tenant(SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        self.show_step(2)
        network = admin.create_network(
            network_name=self.net_data[0].keys()[0],
            tenant_id=tenant.id)['network']

        subnet = admin.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]],
            ip_version=4)

        # Check that network are created.
        assert_true(
            admin.get_network(network['name'])['id'] == network['id']
        )
        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = admin.create_router(
            'router_1',
            tenant=tenant)

        # Add net_1 to router_1
        admin.add_router_interface(
            router_id=router_1["id"],
            subnet_id=subnet["id"])

        self.show_step(5)
        sg1 = admin.nova.security_groups.create(
            'SG1', "descr")
        sg2 = admin.nova.security_groups.create(
            'SG2', "descr")

        self.show_step(3)
        access_point_1, access_point_ip_1 = openstack.create_access_point(
            os_conn=admin, nics=[{'net-id': network['id']}],
            security_groups=[security_group.name, sg1.name])

        self.show_step(4)
        access_point_2, access_point_ip_2 = openstack.create_access_point(
            os_conn=admin, nics=[{'net-id': network['id']}],
            security_groups=[security_group.name, sg2.name])

        self.show_step(6)
        sg_rules = [
            sg_rule for sg_rule
            in admin.neutron.list_security_group_rules()[
                'security_group_rules']
            if sg_rule['security_group_id'] in [sg1.id, sg2.id]]
        for rule in sg_rules:
            admin.neutron.delete_security_group_rule(rule['id'])

        self.show_step(7)
        for rule in [self.icmp, self.tcp]:
            rule["security_group_rule"]["security_group_id"] = sg1.id
            rule["security_group_rule"]["remote_ip_prefix"] = access_point_ip_1
            rule["security_group_rule"]["direction"] = "ingress"
            admin.neutron.create_security_group_rule(rule)
            rule["security_group_rule"]["direction"] = "egress"
            admin.neutron.create_security_group_rule(rule)

        # get private ip of access_point_2
        private_ip = admin.get_nova_instance_ip(
            access_point_2, net_name=network['name'])

        self.show_step(8)
        self.tcp["security_group_rule"]["security_group_id"] = sg2.id
        self.tcp["security_group_rule"]["remote_ip_prefix"] = private_ip
        admin.neutron.create_security_group_rule(self.tcp)
        self.tcp["security_group_rule"]["direction"] = "ingress"
        admin.neutron.create_security_group_rule(self.tcp)

        self.show_step(9)
        istances_sg1 = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}],
            vm_count=1,
            security_groups=[sg1.name])

        istances_sg2 = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}],
            vm_count=1,
            security_groups=[sg2.name])
        openstack.verify_instance_state(admin)

        # Get private ips of instances
        ips = {}
        ips['SG1'] = [
            admin.assign_floating_ip(instance).ip
            for instance in istances_sg1]
        ips['SG2'] = [
            admin.get_nova_instance_ip(instance, net_name=network['name'])
            for instance in istances_sg2]

        self.show_step(10)
        for ip in ips['SG1']:
            ping_result = openstack.remote_execute_command(
                access_point_ip_1, ip, "ping -c 5 {}".format(
                    access_point_ip_1), wait=60 * 4)
            assert_true(
                ping_result['exit_code'] == 0,
                "Ping isn't available from {0} to {1}".format(
                    ip, access_point_ip_1)
            )

        self.show_step(11)
        for ip_1 in ips['SG1']:
            for ip_2 in ips['SG1']:
                if ip_1 != ip_2:
                    ping_result = openstack.remote_execute_command(
                        access_point_ip_1, ip_1, "ping -c 5 {}".format(ip_2))
                    assert_true(
                        ping_result['exit_code'] == 1,
                        "Ping is available from {0} to {1}".format(
                            ip_1, ip_2)
                    )

        self.show_step(12)
        self.show_step(13)
        for ip_1 in ips['SG2']:
            for ip_2 in ips['SG2']:
                if ip_1 != ip_2:
                    try:
                        openstack.remote_execute_command(
                            access_point_ip_2, ip_1,
                            " ")
                    except Exception as e:
                        logger.info('{}'.format(e))
