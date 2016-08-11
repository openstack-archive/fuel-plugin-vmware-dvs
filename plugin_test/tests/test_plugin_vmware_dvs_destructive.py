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
from devops.error import TimeoutError
from proboscis import test
from proboscis.asserts import assert_true
from proboscis.asserts import assert_raises

import fuelweb_test.tests.base_test_case
from fuelweb_test import logger
from fuelweb_test.helpers import os_actions
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import NEUTRON_SEGMENT_TYPE
from fuelweb_test.settings import SERVTEST_PASSWORD
from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test.settings import SERVTEST_USERNAME
from helpers import openstack
from helpers import plugin
from helpers import vmrun
from tests.test_plugin_vmware_dvs_system import TestDVSSystem

TestBasic = fuelweb_test.tests.base_test_case.TestBasic
SetupEnvironment = fuelweb_test.tests.base_test_case.SetupEnvironment


@test(groups=["plugins", 'dvs_vcenter_plugin', 'dvs_vcenter_system',
              'dvs_vcenter_destructive'])
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

    networks = [
        {'name': 'net_1',
         'subnets': [
             {'name': 'subnet_1',
                      'cidr': '192.168.112.0/24'}
                     ]
         },
        {'name': 'net_2',
         'subnets': [
             {'name': 'subnet_1',
                      'cidr': '192.168.113.0/24'}
         ]
         }
    ]

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

        self.show_step(11)
        self.show_step(12)
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
        self.show_step(13)
        ip_pair = {key: [ip for ip in ips if key != ip] for key in ips}
        for ip_from in ip_pair:
            for ip_to in ip_pair[ip_from]:
                cmd = "ping -c 5 {0}".format(ip_to)
                res = openstack.remote_execute_command(
                        access_point_ip, ip_from, cmd)

                assert_true(
                    res['exit_code'] == 0,
                    "Ping isn't available from {0} to {1}".format(ip_from,
                                                                  ip_to)
                )

        self.show_step(14)
        vcenter_name = [
            name for name in self.WORKSTATION_NODES if 'vcenter' in name].pop()
        node = vmrun.Vmrun(
            self.host_type,
            self.path_to_vmx_file.format(vcenter_name),
            host_name=self.host_name,
            username=self.WORKSTATION_USERNAME,
            password=self.WORKSTATION_PASSWORD)
        node.reset()

        self.show_step(15)
        wait(lambda: not icmp_ping(self.VCENTER_IP),
             interval=1,
             timeout=10,
             timeout_msg='Vcenter is still available.')

        self.show_step(16)
        wait(lambda: icmp_ping(self.VCENTER_IP),
             interval=5,
             timeout=120,
             timeout_msg='Vcenter is not available.')

        self.show_step(17)
        for ip_from in ip_pair:
            for ip_to in ip_pair[ip_from]:
                cmd = "ping -c 5 {0}".format(ip_to)
                res = openstack.remote_execute_command(
                    access_point_ip, ip_from, cmd)
                assert_true(
                    res['exit_code'] == 0,
                    "Ping isn't available from {0} to {1}".format(ip_from,
                                                                  ip_to)
                )

    @test(depends_on=[TestDVSSystem.dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_uninstall"])
    @log_snapshot_after_test
    def dvs_vcenter_uninstall(self):
        """Negative uninstall of Fuel DVS plugin with deployed environment.

        Scenario:
            1. Revert snapshot to dvs_vcenter_systest_setup.
            2. Try to uninstall dvs plugin.
            3. Check plugin was not removed.

        Duration: 1.8 hours

        """
        # TODO(vgorin) Uncomment when reverting of WS snapshot is available
        # self.show_step(1)
        # self.env.revert_snapshot("dvs_vcenter_systest_setup")

        self.show_step(2)
        cmd = 'fuel plugins --remove {0}=={1}'.format(
            plugin.plugin_name, plugin.DVS_PLUGIN_VERSION)

        self.ssh_manager.execute_on_remote(
            ip=self.ssh_manager.admin_ip,
            cmd=cmd,
            assert_ec_equal=[1]
        )

        self.show_step(3)
        output = self.ssh_manager.execute_on_remote(
            ip=self.ssh_manager.admin_ip, cmd='fuel plugins list')['stdout']
        assert_true(plugin.plugin_name in output[-1].split(' '),
                    "Plugin '{0}' was removed".format(plugin.plugin_name))

    @test(depends_on=[TestDVSSystem.dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_bind_port"])
    @log_snapshot_after_test
    def dvs_vcenter_bind_port(self):
        """Check abilities to bind port on DVS to VM, disable/enable this port.

        Scenario:
            1. Revert snapshot to dvs_vcenter_destructive_setup
            2. Create private networks net01 with subnet.
            3. Launch instance VM_1 in the net01
               with image TestVM and flavor m1.micro in nova az.
            4. Launch instance VM_2 in the net01
               with image TestVM-VMDK and flavor m1.micro in vcenter az.
            5. Disable sub_net port of instances.
            6. Check instances are not available.
            7. Enable sub_net port of all instances.
            8. Verify that instances communicate between each other.
               Send icmp ping between instances.


        Duration: 1,5 hours

        """
        # TODO(vgorin) Uncomment when reverting of WS snapshot is available
        # self.show_step(1)
        # self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = os_conn.create_sec_group_for_ssh()

        self.show_step(2)
        net = self.networks[0]
        network = os_conn.create_network(network_name=net['name'])['network']

        subnet = os_conn.create_subnet(
            subnet_name=net['subnets'][0]['name'],
            network_id=network['id'],
            cidr=net['subnets'][0]['cidr'])

        logger.info("Check network was created.")
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )

        logger.info("Add net_1 to default router")
        router = os_conn.get_router(os_conn.get_network(self.ext_net_name))
        os_conn.add_router_interface(router_id=router["id"],
                                     subnet_id=subnet["id"])

        self.show_step(3)
        self.show_step(4)
        instances = openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network['id']}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        ports = os_conn.neutron.list_ports()['ports']
        floating_ip = openstack.create_and_assign_floating_ips(
            os_conn, instances)

        def get_ports_by_ip(ports, ips):
            res = []
            for p in ports:
                if p['fixed_ips'][0]['ip_address'] in ips:
                    res.append(p)
            return res

        instance_ips = [os_conn.get_nova_instance_ip(
                instance,
                net_name=network['name']) for instance in instances]
        instance_ports = get_ports_by_ip(ports, instance_ips)

        self.show_step(5)
        for port in instance_ports:
            os_conn.neutron.update_port(
                port['id'], {'port': {'admin_state_up': False}}
            )
        ip_pair = {
            key: [ip for ip in floating_ip if key != ip] for key in floating_ip
        }

        self.show_step(6)
        assert_raises(exception_type=TimeoutError,
                      function=openstack.check_connection_vms,
                      ip_pair=ip_pair)

        self.show_step(7)
        for port in instance_ports:
            os_conn.neutron.update_port(
                port['id'], {'port': {'admin_state_up': True}}
            )

        self.show_step(8)
        openstack.check_connection_vms(ip_pair, timeout=90)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_destructive_setup_2"])
    @log_snapshot_after_test
    def dvs_destructive_setup_2(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Configure cluster with 2 vcenter clusters.
            4. Add 3 node with controller role.
            5. Add 2 node with compute role.
            6. Configure vcenter
            7. Deploy the cluster.
            8. Run smoke OSTF tests
            9. Launch instances. 1 per az. Assign gloating ips.
            10. Make snapshot

        Duration: 1.8 hours
        Snapshot: dvs_destructive_setup_2
        """
        self.show_step(1)
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        self.show_step(2)
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web)

        self.show_step(3)
        self.show_step(4)
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['controller'],
             'slave-03': ['controller'],
             'slave-04': ['compute'],
             'slave-05': ['compute']}
        )
        self.show_step(6)
        self.fuel_web.vcenter_configure(cluster_id, multiclusters=True)

        self.show_step(7)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(8)
        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        self.show_step(9)
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        security_group = os_conn.create_sec_group_for_ssh()

        network = os_conn.nova.networks.find(label=self.inter_net_name)
        instances = openstack.create_instances(
            os_conn=os_conn, nics=[{'net-id': network.id}], vm_count=1,
            security_groups=[security_group.name]
        )
        openstack.verify_instance_state(os_conn)

        for instance in instances:
            os_conn.assign_floating_ip(instance)

        self.show_step(10)
        self.env.make_snapshot("dvs_destructive_setup_2", is_make=True)

    @test(depends_on=[dvs_destructive_setup_2],
          groups=["dvs_vcenter_reset_controller"])
    @log_snapshot_after_test
    def dvs_vcenter_reset_controller(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Revert to 'dvs_destructive_setup_2' snapshot.
            2. Verify connection between instances. Send ping,
               check that ping get reply
            3. Reset controller.
            4. Check that vmclusters migrate to another controller.
            5. Verify connection between instances.
                Send ping, check that ping get reply

        Duration: 1.8 hours

        """
        # TODO(vgorin) Uncomment when reverting of WS snapshot is available
        # self.show_step(1)
        # self.env.revert_snapshot("dvs_destructive_setup_2")

        cluster_id = self.fuel_web.get_last_created_cluster()
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        self.show_step(2)
        srv_list = os_conn.get_servers()
        floating_ip = []
        for srv in srv_list:
            floating_ip.append(os_conn.get_nova_instance_ip(
                srv, net_name=self.inter_net_name, addrtype='floating'))
        ip_pair = {
            key: [ip for ip in floating_ip if key != ip] for key in floating_ip
        }
        openstack.check_connection_vms(ip_pair)

        d_ctrl = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0])
        n_ctrl = self.fuel_web.get_nailgun_node_by_devops_node(d_ctrl)

        self.show_step(3)
        self.fuel_web.cold_restart_nodes([d_ctrl], wait_after_destroy=300)

        self.show_step(4)
        openstack.check_service(ip=n_ctrl['ip'], commands=self.cmds)

        self.show_step(5)
        openstack.check_connection_vms(ip_pair)

    @test(depends_on=[dvs_destructive_setup_2],
          groups=["dvs_vcenter_shutdown_controller"])
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
        # TODO(vgorin) Uncomment when reverting of WS snapshot is available
        # self.show_step(1)
        # self.env.revert_snapshot("dvs_destructive_setup_2")

        cluster_id = self.fuel_web.get_last_created_cluster()
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        self.show_step(2)
        srv_list = os_conn.get_servers()
        ips = []
        for srv in srv_list:
            ips.append(os_conn.get_nova_instance_ip(
                srv, net_name=self.inter_net_name, addrtype='floating'))

        ip_pair = {key: [ip for ip in ips if key != ip] for key in ips}
        openstack.check_connection_vms(ip_pair)

        n_ctrls = self.fuel_web.get_nailgun_cluster_nodes_by_roles(
                cluster_id=cluster_id, roles=['controller'])

        openstack.check_service(ip=n_ctrls[0]['ip'], commands=self.cmds)
        openstack.check_connection_vms(ip_pair)

        self.show_step(3)
        self.fuel_web.warm_shutdown_nodes(
            [self.fuel_web.get_devops_node_by_nailgun_node(n_ctrls[0])])

        self.show_step(4)
        openstack.check_service(ip=n_ctrls[1]['ip'], commands=self.cmds)

        self.show_step(5)
        openstack.check_connection_vms(ip_pair, timeout=90)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_reboot_vcenter_1"])
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
            7. Configure VMware vCenter Settings. Add 2 vSphere clusters
               and configure Nova Compute instances on controllers.
            8. Verify networks.
            9. Deploy cluster.
            10. Run OSTF.
            11. Launch instance VM_1 with image TestVM, availability zone nova
                and flavor m1.micro.
            12. Launch instance VM_2 with image TestVM-VMDK, availability zone
                vcenter and flavor m1.micro.
            13. Check connection between instances, send ping from VM_1 to VM_2
                and vice verse.
            14. Reboot vcenter.
            15. Check that controller lost connection with vCenter.
            16. Wait for vCenter.
            17. Ensure that all instances from vCenter displayed in dashboard.
            18. Run OSTF.


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
                "net_segment_type": NEUTRON_SEGMENT_TYPE
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
        self.fuel_web.vcenter_configure(cluster_id, multiclusters=True)

        self.show_step(8)
        self.fuel_web.verify_network(cluster_id)

        self.show_step(9)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(10)
        self.fuel_web.run_ostf(cluster_id=cluster_id, test_sets=['smoke'])

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        self.extended_tests_reset_vcenter(os_ip)

        self.show_step(18)
        self.fuel_web.run_ostf(cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_reboot_vcenter_2"])
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
            7. Configure VMware vCenter Settings. Add 1 vSphere clusters and
               configure Nova Compute instances on compute-vmware.
            8. Verify networks.
            9. Deploy cluster.
            10. Run OSTF.
            11. Launch instance VM_1 with image TestVM, availability zone nova
                and flavor m1.micro.
            12. Launch instance VM_2 with image TestVM-VMDK, availability zone
                vcenter and flavor m1.micro.
            13. Check connection between instances, send ping from VM_1 to VM_2
                and vice verse.
            14. Reboot vcenter.
            15. Check that controller lost connection with vCenter.
            16. Wait for vCenter.
            17. Ensure that all instances from vCenter displayed in dashboard.
            18. Run OSTF.


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
                "net_segment_type": NEUTRON_SEGMENT_TYPE
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
             'slave-04': ['cinder'],
             'slave-05': ['compute-vmware']}
        )

        self.show_step(6)
        plugin.enable_plugin(cluster_id, self.fuel_web)

        self.show_step(7)
        target_node_1 = self.node_name('slave-05')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_1=target_node_1,
            multiclusters=False
        )

        self.show_step(8)
        self.fuel_web.verify_network(cluster_id)

        self.show_step(9)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(10)
        self.fuel_web.run_ostf(cluster_id=cluster_id, test_sets=['smoke'])

        os_ip = self.fuel_web.get_public_vip(cluster_id)
        self.extended_tests_reset_vcenter(os_ip)

        self.show_step(18)
        self.fuel_web.run_ostf(cluster_id=cluster_id, test_sets=['smoke'])
