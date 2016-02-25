#    Copyright 2014 Mirantis, Inc.
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
import time


from proboscis import test
from proboscis.asserts import assert_true


from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test import logger
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import NEUTRON_SEGMENT_TYPE
from fuelweb_test.settings import SERVTEST_USERNAME
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic
from fuelweb_test.helpers import os_actions


from helpers import plugin
from helpers import openstack


@test(groups=["plugins", 'dvs_vcenter_system'])
class TestDVSPlugin(TestBasic):

    # constants
    node_name = lambda self, name_node: self.fuel_web. \
        get_nailgun_node_by_name(name_node)['hostname']

    net_data = [{'net_1': '192.168.112.0/24'},
                {'net_2': '192.168.113.0/24'}]

    # defaults
    ext_net_name = openstack.get_defaults()['networks']['floating']['name']
    inter_net_name = openstack.get_defaults()['networks']['internal']['name']
    instance_creds = (
        openstack.get_defaults()['os_credentials']['cirros']['user'],
        openstack.get_defaults()['os_credentials']['cirros']['password'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_systest_setup", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_systest_setup(self):
        """Deploy cluster with plugin and vmware datastore backend

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 2 node with compute role.
            6. Add 1 node with compute-vmware role.
            7. Deploy the cluster.
            8. Run OSTF.
            9. Create snapshot.

        Duration 1.8 hours
        Snapshot dvs_vcenter_systest_setup

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(
            self.env.d_env.get_admin_remote())

        # Configure cluster with 2 vcenter clusters and vcenter glance
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

        # Assign role to node
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

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

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

        Duration 15 min

        """
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Create new network
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        subnets = []
        networks = []

        for net in self.net_data:
            logger.info('Create network {}'.format(net.keys()[0]))
            network = openstack.create_network(
                os_conn,
                net.keys()[0], tenant_name=SERVTEST_TENANT
            )

            logger.info('Create subnet {}'.format(net.keys()[0]))
            subnet = openstack.create_subnet(
                os_conn,
                network,
                net[net.keys()[0]], tenant_name=SERVTEST_TENANT
            )

            subnets.append(subnet)
            networks.append(network)

        # Check that networks are created.
        for network in networks:
            assert_true(
                os_conn.get_network(network['name'])['id'] == network['id']
            )

        #  Delete net_1.
        logger.info('Delete network net_1')
        os_conn.neutron.delete_subnet(subnets[0]['id'])
        os_conn.neutron.delete_network(networks[0]['id'])
        # Check that net_1 is deleted.
        assert_true(
            os_conn.get_network(networks[0]) is None
        )
        logger.info('Networks net_1 is removed.')
        logger.info('Created net_1 again.')
        network = openstack.create_network(
            os_conn,
            self.net_data[0].keys()[0])
        subnet = openstack.create_subnet(
            os_conn,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name=SERVTEST_TENANT
        )
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
            2. Create private networks net01 with sunet.
            3. Add one  subnet (net01_subnet01: 192.168.101.0/24
            4. Create Router_01, set gateway and add interface
               to external network.
            5. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            6. Launch instances VM_3 and VM_4 in the net01
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            7. Send ping from instances to 8.8.8.8
               or other outside ip.

        Duration 15 min

        """

        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Create new network
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Create non default network with subnet.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = openstack.create_network(
            os_conn,
            self.net_data[0].keys()[0], tenant_name=SERVTEST_TENANT
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

        # create security group with rules for ssh and ping
        security_group = os_conn.create_sec_group_for_ssh()

        # Launch instance VM_1, VM_2 in the tenant network net_01
        # with image TestVMDK and flavor m1.micro in the nova az.
        # Launch instances VM_3 and VM_4 in the net01
        # with image TestVM-VMDK and flavor m1.micro in vcenter az.
        openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        # Add net_1 to default router
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        openstack.add_subnet_to_router(
            os_conn,
            router['id'], subnet['id'])

        openstack.create_and_assign_floating_ip(os_conn=os_conn)

        # Send ping from instances VM_1 and VM_2 to 8.8.8.8
        # or other outside ip.
        srv_list = os_conn.get_servers()
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name)
        openstack.check_connection_vms(
            os_conn=os_conn, srv_list=srv_list, command='pingv4',
            remote=ssh_controller,
            destination_ip=['8.8.8.8']
        )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_instances_one_group", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_instances_one_group(self):
        """Check creation instance in the one group simultaneously

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

        Duration 15 min

        """
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
        # limitdos.py revert-resume dvs_570 error_dvs_instances_batch
        vm_count = min(
            [os_conn.nova.hypervisors.resource_class.to_dict(h)['vcpus']
             for h in os_conn.nova.hypervisors.list()]
        )

        logger.info(security_group)

        openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network.id}],
            vm_count=vm_count, security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        logger.info("Check ping is available between instances.")
        openstack.create_and_assign_floating_ip(os_conn=os_conn)

        srv_list = os_conn.nova.servers.list()

        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0])

        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name)

        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       command='pingv4', remote=ssh_controller)

        logger.info("Check ssh connection is available between instances.")
        floating_ip = []
        for srv in srv_list:
            floating_ip.append(
                [add['addr']
                 for add in srv.addresses[srv.addresses.keys()[0]]
                 if add['OS-EXT-IPS:type'] == 'floating'][0])
        ip_pair = [
            (ip_1, ip_2)
            for ip_1 in floating_ip
            for ip_2 in floating_ip
            if ip_1 != ip_2]

        for ips in ip_pair:
            openstack.check_ssh_between_instances(ips[0], ips[1])

        logger.info("Delete all instances from horizon simultaneously.")
        for srv in srv_list:
            os_conn.nova.servers.delete(srv)

        logger.info("Check that all instances were deleted.")
        for srv in srv_list:
            assert_true(os_conn.verify_srv_deleted(srv),
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

        Duration 30 min

        """

        # security group rules
        tcp = {
            "security_group_rule":
                {"direction": "ingress",
                 "port_range_min": "22",
                 "ethertype": "IPv4",
                 "port_range_max": "22",
                 "protocol": "TCP",
                 "security_group_id": ""}}
        icmp = {
            "security_group_rule":
                {"direction": "ingress",
                 "ethertype": "IPv4",
                 "protocol": "icmp",
                 "security_group_id": ""}}

        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        logger.info("Create non default network with subnet.")
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

        logger.info("Check that network are created.")
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )

        logger.info("Add net_1 to default router")
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        openstack.add_subnet_to_router(
            os_conn,
            router['id'], subnet['id'])

        logger.info("""Launch 2 instances of vcenter and 2 instances of nova
                       in the tenant network net_01.""")
        openstack.create_instances(
            os_conn=os_conn,
            nics=[{'net-id': network['id']}],
            vm_count=1
        )
        openstack.verify_instance_state(os_conn)

        logger.info("""Launch 2 instances of vcenter and
                       2 instances of nova
                       in the  default tenant network.""")
        network = os_conn.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=os_conn,
            nics=[{'net-id': network.id}],
            vm_count=1
        )
        openstack.verify_instance_state(os_conn)

        openstack.create_and_assign_floating_ip(os_conn=os_conn)

        logger.info("""Create security groups SG_1 to allow ICMP traffic.
            Add Ingress rule for ICMP protocol to SG_1
            Create security groups SG_2 to allow TCP traffic 22 port.
            Add Ingress rule for TCP protocol to SG_2.""")

        sec_name = ['SG1', 'SG2']
        sg1 = os_conn.nova.security_groups.create(
            sec_name[0], "descr")
        sg2 = os_conn.nova.security_groups.create(
            sec_name[1], "descr")

        tcp["security_group_rule"]["security_group_id"] = sg1.id
        os_conn.neutron.create_security_group_rule(tcp)
        icmp["security_group_rule"]["security_group_id"] = sg2.id
        os_conn.neutron.create_security_group_rule(icmp)

        logger.info("""Remove default security group
                       and attach SG_1 and SG2 to instances""")
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv.remove_security_group(srv.security_groups[0]['name'])
            srv.add_security_group(sg1.id)
            srv.add_security_group(sg2.id)

        time.sleep(20)  # need wait to update rules on dvs

        logger.info("Check ping between instances.")
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name)

        logger.info("Check ping is available between instances.")
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       command='pingv4', remote=ssh_controller)

        logger.info("Check ssh connection is available between instances.")
        floating_ip = []
        for srv in srv_list:
            floating_ip.append(
                [add['addr']
                 for add in srv.addresses[srv.addresses.keys()[0]]
                 if add['OS-EXT-IPS:type'] == 'floating'][0])

        ip_pair = [(ip_1, ip_2)
                   for ip_1 in floating_ip
                   for ip_2 in floating_ip
                   if ip_1 != ip_2]

        for ips in ip_pair:
            openstack.check_ssh_between_instances(ips[0], ips[1])

        logger.info("Delete all rules from SG_1 and SG_2")
        sg_rules = os_conn.neutron.list_security_group_rules()[
            'security_group_rules']
        sg_rules = [
            sg_rule for sg_rule
            in os_conn.neutron.list_security_group_rules()[
                'security_group_rules']
            if sg_rule['security_group_id'] in [sg1.id, sg2.id]]
        for rule in sg_rules:
            os_conn.neutron.delete_security_group_rule(rule['id'])

        time.sleep(20)  # need wait to update rules on dvs

        logger.info("Check  ssh are not available to instances")
        for ip in floating_ip:
            try:
                openstack.get_ssh_connection(
                    ip, self.instance_creds[0],
                    self.instance_creds[1])
            except Exception as e:
                logger.info('{}'.format(e))

        logger.info("Add Ingress and egress rules for TCP protocol to SG_2")
        tcp["security_group_rule"]["security_group_id"] = sg2.id
        os_conn.neutron.create_security_group_rule(tcp)
        tcp["security_group_rule"]["direction"] = "egress"
        os_conn.neutron.create_security_group_rule(tcp)

        time.sleep(20)  # need wait to update rules on dvs ports

        logger.info("Check ssh connection is available between instances.")
        for ips in ip_pair:
            openstack.check_ssh_between_instances(ips[0], ips[1])

        logger.info("Check ping is not available between instances.")
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       command='pingv4', remote=ssh_controller,
                                       result_of_command=1)

        logger.info("Add Ingress and egress rules for ICMP protocol to SG_1")
        icmp["security_group_rule"]["security_group_id"] = sg1.id
        os_conn.neutron.create_security_group_rule(icmp)
        icmp["security_group_rule"]["direction"] = "egress"
        os_conn.neutron.create_security_group_rule(icmp)

        time.sleep(20)  # need wait to update rules on dvs ports

        logger.info("Check ping is available between instances.")
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       command='pingv4', remote=ssh_controller)

        logger.info("""Delete SG1 and SG2 security groups.
                     Attach instances to default security group.""")
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            for sg in srv.security_groups:
                srv.remove_security_group(sg['name'])
            srv.add_security_group('default')
        # need add tcp rule for ssh to instances
        tcp["security_group_rule"]["security_group_id"] = \
            [
                sg['id']
                for sg in os_conn.neutron.list_security_groups()[
                    'security_groups']
                if sg['tenant_id'] == os_conn.get_tenant(SERVTEST_TENANT).id
                if sg['name'] == 'default'][0]
        tcp["security_group_rule"]["direction"] = "ingress"
        os_conn.neutron.create_security_group_rule(tcp)
        time.sleep(20)  # need wait to update rules on dvs ports

        logger.info("Check ping is available between instances.")
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       command='pingv4', remote=ssh_controller)

        logger.info("Check ssh connection is available between instances.")
        for ips in ip_pair:
            openstack.check_ssh_between_instances(ips[0], ips[1])

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_tenants_isolation", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_tenants_isolation(self):
        """Verify that instances on different tenants should not communicate
            between each other. Send icmp ping from instances
            of admin tenant to instances of test_tenant and vice versa.

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
              Send icmp ping from VM_3,
              VM_4 of admin tenant to VM_3 VM_4 of test_tenant and vice versa.

        Duration 30 min

        """

        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Create new network
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Create non-admin tenant.
        admin.create_user_and_tenant('test', 'test', 'test')
        openstack.add_role_to_user(admin, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, 'test', 'test', 'test')

        # Create non default network with subnet in test tenant.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = openstack.create_network(
            test,
            self.net_data[0].keys()[0], tenant_name='test'
        )

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = openstack.create_subnet(
            test,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name='test'
        )

        # create security group with rules for ssh and ping
        security_group = test.create_sec_group_for_ssh()

        #  Launch 2 instances in the est tenant network net_01
        openstack.create_instances(
            os_conn=test, vm_count=1,
            nics=[{'net-id': network['id']}],
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(test)

        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = openstack.add_router(
            test,
            'router_1'
        )

        # Add net_1 to router_1
        openstack.add_subnet_to_router(
            test,
            router_1['id'], subnet['id'])

        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()

        # Launch 2 instances in the admin tenant net04
        network = admin.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network.id}], vm_count=1,
            security_groups=[security_group.name])
        openstack.verify_instance_state(admin)

        # Send ping from instances VM_1 and VM_2 to VM_3 and VM_4
        # via no floating ip
        srv_1 = admin.get_servers()
        srv_2 = test.get_servers()
        openstack.create_and_assign_floating_ip(os_conn=admin, srv_list=srv_1)
        openstack.create_and_assign_floating_ip(
            os_conn=test,
            srv_list=srv_2,
            ext_net=None,
            tenant_id=test.get_tenant('test').id)

        srv_1 = admin.get_servers()
        srv_2 = test.get_servers()

        ips = []
        for srv in srv_2:
            ip = srv.networks[srv.networks.keys()[0]][0]
            ips.append(ip)

        logger.info(ips)
        logger.info(srv_1)
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name)
        openstack.check_connection_vms(
            os_conn=admin, srv_list=srv_1, command='pingv4',
            result_of_command=1,
            remote=ssh_controller, destination_ip=ips
        )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_same_ip", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_same_ip(self):
        """Check connectivity between instances with same ip
           in different tenants.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Create non-admin tenant.
            3. Create private network net01 with sunet in non-admin tenant.
            4. Create Router_01, set gateway and add interface
               to external network.
            5. Create private network net01 with sunet in default admin tenant
            6. Create Router_01, set gateway and add interface
               to external network.
            7. Launch instances VM_1 and VM_2
               in the net01(non-admin tenant)
               with image TestVM and flavor m1.micro in nova az.
            8. Launch instances VM_3 and VM_4 in the net01(non-admin tenant)
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
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

        Duration 30 min

        """

        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        admin = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Create non-admin tenant.
        admin.create_user_and_tenant('test', 'test', 'test')
        openstack.add_role_to_user(admin, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, 'test', 'test', 'test')

        # Create non default network with subnet in test tenant.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = openstack.create_network(
            test,
            self.net_data[0].keys()[0], tenant_name='test'
        )

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = openstack.create_subnet(
            test,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name='test'
        )

        # create security group with rules for ssh and ping
        security_group = test.create_sec_group_for_ssh()

        # Launch instances VM_1 and VM_2 in the net01(non-admin tenant)
        # with image TestVM and flavor m1.micro in nova az.
        # Launch instances VM_3 and VM_4 in the net01(non-admin tenant)
        # with image TestVM-VMDK and flavor m1.micro in vcenter az.
        openstack.create_instances(
            os_conn=test, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(test)

        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = openstack.add_router(
            test,
            'router_1',
            ext_net_name=self.ext_net_name, tenant_name='test'
        )

        # Add net_1 to router_1
        openstack.add_subnet_to_router(
            test,
            router_1['id'], subnet['id'])

        srv_1 = test.get_servers()
        openstack.create_and_assign_floating_ip(
            os_conn=test,
            srv_list=srv_1,
            ext_net=None,
            tenant_id=test.get_tenant('test').id)
        srv_1 = test.get_servers()
        # create security group with rules for ssh and ping
        security_group = admin.create_sec_group_for_ssh()
        # Create non default network with subnet in admin tenant.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = openstack.create_network(
            admin,
            self.net_data[0].keys()[0])

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = openstack.create_subnet(
            admin,
            network,
            self.net_data[0][self.net_data[0].keys()[0]])

        # Launch instances VM_5 and VM_6
        # in the net01(default admin tenant)
        # with image TestVM and flavor m1.micro in nova az.
        # Launch instances VM_7 and VM_8
        # in the net01(default admin tenant)
        # with image TestVM-VMDK and flavor m1.micro in vcenter az.
        openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name])
        openstack.verify_instance_state(admin)

        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = openstack.add_router(
            admin,
            'router_1')

        # Add net_1 to router_1
        openstack.add_subnet_to_router(
            admin,
            router_1['id'], subnet['id'])

        # Send ping between instances
        # via no floating ip
        srv_2 = admin.get_servers()
        openstack.create_and_assign_floating_ip(
            os_conn=admin,
            srv_list=srv_2)
        srv_2 = admin.get_servers()

        # Verify that VM_1, VM_2, VM_3 and VM_4 should communicate
        # between each other via fixed ip.
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name)
        openstack.check_connection_vms(
            os_conn=test, srv_list=srv_1, remote=ssh_controller)

        # Verify that VM_5, VM_6, VM_7 and VM_8 should communicate
        # between each other via fixed ip.
        openstack.check_connection_vms(os_conn=admin, srv_list=srv_2,
                                       remote=ssh_controller)
