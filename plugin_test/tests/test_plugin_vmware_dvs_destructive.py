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

import os
import time

from devops.helpers.helpers import icmp_ping
from devops.helpers.helpers import wait
from proboscis import test
from proboscis.asserts import assert_true

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
from helpers import vmrun
from tests.test_plugin_vmware_dvs_system import TestDVSSystem


@test(groups=["plugins", 'dvs_vcenter_plugin', 'dvs_vcenter_system'])
class TestDVSDestructive(TestBasic):
    """Failover test suite.

    Destructive(Failover) and recovery testing ensures that the
    target-of-test can successfully failover and recover from a variety of
    hardware, software, or network malfunctions with undue loss of data or
    data integrity.
    """

    def node_name(self, name_node):
        """Get node by name."""
        return self.fuel_web.get_nailgun_node_by_name(name_node)['hostname']

    # constants
    cmds = ['nova-manage service list | grep vcenter-vmcluster1',
            'nova-manage service list | grep vcenter-vmcluster2']

    net_data = [{'net_1': '192.168.112.0/24'},
                {'net_2': '192.168.113.0/24'}]
    # defaults
    inter_net_name = openstack.get_defaults()['networks']['internal']['name']
    ext_net_name = openstack.get_defaults()['networks']['floating']['name']
    host_type = 'ws-shared'
    path_to_vmx_file = '"[standard] {0}/{0}.vmx"'
    host_name = 'https://localhost:443/sdk'
    WORKSTATION_NODES = os.environ.get('WORKSTATION_NODES').split(' ')
    WORKSTATION_USERNAME = os.environ.get('WORKSTATION_USERNAME')
    WORKSTATION_PASSWORD = os.environ.get('WORKSTATION_PASSWORD')
    VCENTER_IP = os.environ.get('VCENTER_IP')

    def extended_tests_reset_vcenter(self, openstack_ip):
        """Common verification of dvs_reboot_vcenter* test cases.

        :param openstack_ip: type string, openstack ip
        """
        admin = os_actions.OpenStackActions(
            openstack_ip, SERVTEST_USERNAME,
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

        self.show_step(13)
        self.show_step(14)
        instances = openstack.create_instances(
            os_conn=admin, nics=[{'net-id': network.id}],
            vm_count=1,
            security_groups=[default_sg['name']])
        openstack.verify_instance_state(admin)

        # Get private ips of instances
        ips = []
        for instance in instances:
            ips.append(admin.get_nova_instance_ip(
                instance, net_name=self.inter_net_name))
        time.sleep(30)
        self.show_step(15)
        for ip in ips:
            ping_result = openstack.remote_execute_command(
                access_point_ip, ip, "ping -c 5 {}".format(ip))
            assert_true(
                ping_result['exit_code'] == 0,
                "Ping isn't available from {0} to {1}".format(ip, ip)
            )

        self.show_step(16)
        vcenter_name = [
            name for name in self.WORKSTATION_NODES if 'vcenter' in name].pop()
        node = vmrun.Vmrun(
            self.host_type,
            self.path_to_vmx_file.format(vcenter_name),
            host_name=self.host_name,
            username=self.WORKSTATION_USERNAME,
            password=self.WORKSTATION_PASSWORD)
        node.reset()

        self.show_step(17)
        wait(lambda: not icmp_ping(
            self.VCENTER_IP), interval=1, timeout=10,
            timeout_msg='Vcenter is still availabled.')

        self.show_step(18)
        wait(lambda: icmp_ping(
            self.VCENTER_IP), interval=5, timeout=120,
            timeout_msg='Vcenter is not availabled.')

        self.show_step(20)
        for ip in ips:
            ping_result = openstack.remote_execute_command(
                access_point_ip, ip, "ping -c 5 {}".format(ip))
            assert_true(
                ping_result['exit_code'] == 0,
                "Ping isn't available from {0} to {1}".format(ip, ip)
            )

    @test(depends_on=[TestDVSSystem.dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_uninstall", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_uninstall(self):
        """Negative uninstall of Fuel DVS plugin with deployed environment.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Try to uninstall dvs plugin.

        Duration: 1.8 hours

        """
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        # Try to uninstall dvs plugin
        cmd = 'fuel plugins --remove {0}=={1}'.format(
            plugin.plugin_name, plugin.DVS_PLUGIN_VERSION)

        res = self.ssh_manager.execute(self.ssh_manager.admin_ip, cmd)
        assert_true(res['exit_code'] == 1)

        # Check that plugin is not removed
        output = self.ssh_manager.execute_on_remote(
            ip=self.ssh_manager.admin_ip, cmd='fuel plugins list')['stdout']
        assert_true(
            plugin.plugin_name in output[-1].split(' '),
            "Plugin '{0}' was removed".format(plugin.plugin_name)
        )

    @test(depends_on=[TestDVSSystem.dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_bind_port"])
    @log_snapshot_after_test
    def dvs_vcenter_bind_port(self):
        """Check abilities to bind port on DVS to VM, disable/enable this port.

        Scenario:
            1. Revert snapshot to dvs_vcenter_destructive_setup
            2. Create private networks net01 with sunet.
            3. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            4. Launch instances VM_3 and VM_4 in the net01
               with image TestVM-VMDK and flavor m1.micro in nova az.
            4. Bind sub_net port of instances.
            5. Check instances are not available.
            6. Enable sub_net port of all instances.
            7. Verify that instances should communicate between each other.
               Send icmp ping between instances.


        Duration: 1,5 hours

        """
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Create new network
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = os_conn.create_sec_group_for_ssh()

        logger.info("Create non default network with subnet.")
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = os_conn.create_network(
            network_name=self.net_data[0].keys()[0])['network']

        subnet = os_conn.create_subnet(
            subnet_name=network['name'],
            network_id=network['id'],
            cidr=self.net_data[0][self.net_data[0].keys()[0]])

        logger.info("Check that network are created.")
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )

        logger.info("Add net_1 to default router")
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        os_conn.add_router_interface(
            router_id=router["id"],
            subnet_id=subnet["id"])

        #  Launch instance VM_1 and VM_2
        instances = openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        ports = os_conn.neutron.list_ports()['ports']
        floating_ip = openstack.create_and_assign_floating_ips(
            os_conn, instances)
        instance_ports = []
        for instance in instances:
            instance_addr = os_conn.get_nova_instance_ip(
                instance, net_name=network['name'])
            for port in ports:
                port_addr = port['fixed_ips'][0]['ip_address']
                if instance_addr == port_addr:
                    instance_ports.append(port)
        for port in instance_ports:
            os_conn.neutron.update_port(
                port['id'], {'port': {'admin_state_up': False}}
            )

        ip_pair = dict.fromkeys(floating_ip)
        for key in ip_pair:
            ip_pair[key] = [value for value in floating_ip if key != value]
        # Verify that not connection to instances
        try:
            openstack.check_connection_vms(ip_pair)
        except Exception as e:
                logger.info(str(e))

        # Enable sub_net ports of instances
        for port in instance_ports:
            os_conn.neutron.update_port(
                port['id'], {'port': {'admin_state_up': True}}
            )

            instance.reboot()
            wait(
                lambda:
                os_conn.get_instance_detail(instance).status == "ACTIVE",
                timeout=300)

        time.sleep(60)  # need time after reboot to get ip by instance

        # Verify that instances should communicate between each other.
        # Send icmp ping between instances
        openstack.check_connection_vms(ip_pair)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_destructive_setup_2", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_destructive_setup_2(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller role.
            5. Add 2 node with compute role.
            6. Deploy the cluster.
            7. Launch instances.

        Duration: 1.8 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        # Configure cluster with 2 vcenter clusters and vcenter glance
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['controller'],
             'slave-03': ['controller'],
             'slave-04': ['compute'],
             'slave-05': ['compute']}
        )
        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(cluster_id, multiclusters=True)

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = os_conn.create_sec_group_for_ssh()

        network = os_conn.nova.networks.find(label=self.inter_net_name)
        instances = openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network.id}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        for instance in instances:
            os_conn.assign_floating_ip(instance)

        self.env.make_snapshot("dvs_destructive_setup_2", is_make=True)

    @test(depends_on=[dvs_destructive_setup_2],
          groups=["dvs_vcenter_reset_controller", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_reset_controller(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Revert to 'dvs_destructive_setup_2' snapshot.
            2. Verify connection between instances. Send ping,
               check that ping get reply
            3. Reset controller.
            4. Check that vmclusters should be migrate to another controller.
            5. Verify connection between instances.
                Send ping, check that ping get reply

        Duration: 1.8 hours

        """
        self.env.revert_snapshot("dvs_destructive_setup_2")

        cluster_id = self.fuel_web.get_last_created_cluster()
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Verify connection between instances.
        # Send ping Check that ping get reply.
        srv_list = os_conn.get_servers()
        floating_ip = []
        for srv in srv_list:
            floating_ip.append(os_conn.get_nova_instance_ip(
                srv, net_name=self.inter_net_name, addrtype='floating'))
        ip_pair = dict.fromkeys(floating_ip)
        for key in ip_pair:
            ip_pair[key] = [value for value in floating_ip if key != value]
        openstack.check_connection_vms(ip_pair)

        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )

        self.fuel_web.cold_restart_nodes(
            [self.fuel_web.environment.d_env.get_node(name=controller.name)],
            wait_offline=True, wait_online=True,
            wait_after_destroy=300)

        controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[1]
        )

        # Verify connection between instances.
        # Send ping Check that ping get reply.
        with self.fuel_web.get_ssh_for_node(controller.name) as ssh_control:
            openstack.check_service(ssh=ssh_control, commands=self.cmds)
        openstack.check_connection_vms(ip_pair)

    @test(depends_on=[dvs_destructive_setup_2],
          groups=["dvs_vcenter_shutdown_controller", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_shutdown_controller(self):
        """Verify that vmclusters should be migrate after shutdown controller.

        Scenario:
            1. Revert to 'dvs_destructive_setup_2' snapshot.
            2.  Verify connection between instances. Send ping,
               check that ping get reply.
            3. Shutdown controller.
            4. Check that vmclusters should be migrate to another controller.
            5. Verify connection between instances.
                Send ping, check that ping get reply

        Duration: 1.8 hours

        """
        self.env.revert_snapshot("dvs_destructive_setup_2")

        cluster_id = self.fuel_web.get_last_created_cluster()
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Verify connection between instances.
        # Send ping, check that ping get reply.
        srv_list = os_conn.get_servers()
        floating_ip = []
        for srv in srv_list:
            floating_ip.append(os_conn.get_nova_instance_ip(
                srv, net_name=self.inter_net_name, addrtype='floating'))
        ip_pair = dict.fromkeys(floating_ip)
        for key in ip_pair:
            ip_pair[key] = [value for value in floating_ip if key != value]
        openstack.check_connection_vms(ip_pair)

        controllers = self.fuel_web.get_devops_nodes_by_nailgun_nodes(
            self.fuel_web.get_nailgun_cluster_nodes_by_roles(
                cluster_id=cluster_id,
                roles=['controller']))

        with self.fuel_web.get_ssh_for_node(controllers[0].name) as ssh_contr:
            openstack.check_service(ssh=ssh_contr, commands=self.cmds)

        openstack.check_connection_vms(ip_pair)

        self.fuel_web.warm_shutdown_nodes(
            [self.fuel_web.environment.d_env.get_node(
                name=controllers[0].name)])
        time.sleep(30)

        # Verify connection between instances.
        # Send ping Check that ping get reply.
        with self.fuel_web.get_ssh_for_node(controllers[1].name) as ssh_contr:
            openstack.check_service(ssh=ssh_contr, commands=self.cmds)
        openstack.check_connection_vms(ip_pair)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_reboot_vcenter_1", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_reboot_vcenter_1(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Install DVS plugin on master node.
            2. Create a new environment with following parameters:
                * Compute: KVM/QEMU with vCenter
                * Networking: Neutron with VLAN segmentation
                * Storage: default
                * Additional services: default
            3. Add nodes with following roles:
                * Controller
                * Compute
                * Cinder
                * CinderVMware
            4. Configure interfaces on nodes.
            5. Configure network settings.
            6. Enable and configure DVS plugin.
            7. Enable VMWare vCenter/ESXi datastore for images (Glance).
            8. Configure VMware vCenter Settings. Add 2 vSphere clusters
               and configure Nova Compute instances on conrollers.
            9. Configure Glance credentials on VMware tab.
            10. Verify networks.
            11. Deploy cluster.
            12. Run OSTF.
            13. Launch instance VM_1 with image TestVM, availability zone nova
                and flavor m1.micro.
            14. Launch instance VM_2 with image TestVM-VMDK, availability zone
                vcenter and flavor m1.micro.
            15. Check connection between instances, send ping from VM_1 to VM_2
                and vice verse.
            16. Reboot vcenter.
            17. Check that controller lost connection with vCenter.
            18. Wait for vCenter.
            19. Ensure that all instances from vCenter displayed in dashboard.
            20. Ensure connectivity between instances.
            21. Run OSTF.


        Duration: 2.5 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        self.show_step(1)
        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'images_vcenter': True
            }
        )

        self.show_step(3)
        self.show_step(4)
        self.show_step(5)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute'],
             'slave-03': ['cinder-vmware'],
             'slave-04': ['cinder']}
        )

        self.show_step(6)
        plugin.enable_plugin(cluster_id, self.fuel_web)

        self.show_step(7)
        self.show_step(8)
        self.show_step(9)
        self.fuel_web.vcenter_configure(
            cluster_id,
            multiclusters=True,
            vc_glance=True
        )

        self.show_step(10)
        self.fuel_web.verify_network(cluster_id)

        self.show_step(11)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(12)
        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        self.extended_tests_reset_vcenter(os_ip)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_reboot_vcenter_2", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_reboot_vcenter_2(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Install DVS plugin on master node.
            2. Create a new environment with following parameters:
                * Compute: KVM/QEMU with vCenter
                * Networking: Neutron with VLAN segmentation
                * Storage: default
                * Additional services: default
            3. Add nodes with following roles:
                * Controller
                * Compute
                * Cinder
                * CinderVMware
                * ComputeVMware
            4. Configure interfaces on nodes.
            5. Configure network settings.
            6. Enable and configure DVS plugin.
            7. Enable VMWare vCenter/ESXi datastore for images (Glance).
            8. Configure VMware vCenter Settings. Add 1 vSphere clusters and
               configure Nova Compute instances on compute-vmware.
            9. Configure Glance credentials on VMware tab.
            10. Verify networks.
            11. Deploy cluster.
            12. Run OSTF.
            13. Launch instance VM_1 with image TestVM, availability zone nova
                and flavor m1.micro.
            14. Launch instance VM_2 with image TestVM-VMDK, availability zone
                vcenter and flavor m1.micro.
            15. Check connection between instances, send ping from VM_1 to VM_2
                and vice verse.
            16. Reboot vcenter.
            17. Check that controller lost connection with vCenter.
            18. Wait for vCenter.
            19. Ensure that all instances from vCenter displayed in dashboard.
            20. Ensure connectivity between instances.
            21. Run OSTF.


        Duration: 2.5 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

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
             'slave-02': ['compute'],
             'slave-03': ['cinder-vmware'],
             'slave-04': ['cinder'],
             'slave-05': ['compute-vmware']}
        )

        # Configure VMWare vCenter settings
        target_node_1 = self.node_name('slave-05')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_1=target_node_1,
            multiclusters=False,
            vc_glance=True
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        self.extended_tests_reset_vcenter(os_ip)
