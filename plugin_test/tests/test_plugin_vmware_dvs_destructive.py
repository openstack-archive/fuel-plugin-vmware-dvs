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
from devops.helpers.helpers import wait


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


@test(groups=["plugins", 'dvs_vcenter_plugin', 'dvs_vcenter_system'])
class TestDVSPlugin(TestBasic):

    # constants
    node_name = lambda self, name_node: self.fuel_web. \
        get_nailgun_node_by_name(name_node)['hostname']

    # defaults
    inter_net_name = 'admin_internal_net'

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_add_delete_nodes", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_add_delete_nodes(self):
        """Deploy cluster with plugin and vmware datastore backend

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller role.
            5. Add 2 node with cinder-vmdk role.
            6. Add 1 node with compute role.
            7. Remove node with cinder-vmdk role.
            8. Add node with cinder role.
            9. Redeploy cluster.
            10. Run OSTF.
            11. Remove node with compute role.
            12. Add node with cinder-vmdk role.
            13. Redeploy cluster.
            14. Run OSTF.

        Duration 3 hours

        """
        self.env.revert_snapshot("ready_with_9_slaves")

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

        # Configure cluster
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
             'slave-04': ['cinder-vmware'],
             'slave-05': ['compute'],
             'slave-06': ['compute'],
             'slave-07': ['compute-vmware'], })

        # Configure VMWare vCenter settings
        target_node_1 = self.node_name('slave-07')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_1=target_node_1,
            multiclusters=True
        )
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        # Remove node with cinder-vmdk role
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-04': ['cinder-vmware'], }, False, True)

        # Add 1 node with cinder role and redeploy cluster
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-08': ['cinder'],
            }
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        # Remove node with compute role
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-05': ['compute'], }, False, True)

        # Add 1 node with cinder-vmdk role and redeploy cluster
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-04': ['cinder-vmware'],
            }
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_add_delete_controller", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_add_delete_controller(self):
        """Deploy cluster with plugin, adding  and deletion controler node.

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 4 node with controller role.
            5. Add 1 node with cinder-vmdk role.
            6. Add 1 node with compute role.
            7. Deploy cluster.
            8. Run OSTF.
            9. Remove node with controller role.
            10. Redeploy cluster.
            11. Run OSTF.
            12. Add node with controller role.
            13. Redeploy cluster.
            14. Run OSTF.

        Duration 3.5 hours

        """
        self.env.revert_snapshot("ready_with_9_slaves")

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

        # Configure cluster
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
             'slave-04': ['controller'],
             'slave-05': ['cinder-vmware'],
             'slave-06': ['compute'], })

        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(cluster_id)

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        # Remove node with controller role
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'], }, False, True)

        self.fuel_web.deploy_cluster_wait(cluster_id, check_services=False)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

        # Add node with controller role

        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-07': ['controller'],
            }
        )

        self.fuel_web.deploy_cluster_wait(cluster_id, check_services=False)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_destructive_setup", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_destructive_setup(self):
        """Deploy cluster with plugin and vmware datastore backend

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Add 1 node with compute-vmware role.
            7. Deploy the cluster.
            8. Run OSTF.

        Duration 1.8 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

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
             'slave-03': ['compute']
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

        self.env.make_snapshot("dvs_vcenter_destructive_setup", is_make=True)

    @test(depends_on=[dvs_vcenter_destructive_setup],
          groups=["dvs_vcenter_uninstall", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_uninstall(self):
        """Verify that it is not possibility to uninstall
           of Fuel DVS plugin with deployed environment.

        Scenario:
            1. Revert snapshot to dvs_vcenter_bvt_2
            2. Try to uninstall dvs plugin.

        Duration 1.8 hours

        """

        self.env.revert_snapshot("dvs_vcenter_destructive_setup")

        # Try to uninstall dvs plugin
        cmd = 'fuel plugins --remove {}==1.1.0'.format(plugin.plugin_name)
        self.env.d_env.get_admin_remote().execute(cmd)['exit_code'] == 1

        # Check that plugin is not removed
        output = list(self.env.d_env.get_admin_remote().execute(
            'fuel plugins list')['stdout'])

        assert_true(
            plugin.plugin_name in output[-1].split(' '),
            "Plugin is removed {}".format(plugin.plugin_name)
        )

    @test(depends_on=[dvs_vcenter_destructive_setup],
          groups=["dvs_vcenter_bind_port", "dvs_vcenter_destructive_setup"])
    @log_snapshot_after_test
    def dvs_vcenter_bind_port(self):
        """Check abilities to bind port on DVS to VM,
           disable and enable this port.

        Scenario:
            1. Revert snapshot to dvs_vcenter_bvt_2
            2. Create private networks net01 with sunet.
            3. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            4. Launch instances VM_3 and VM_4 in the net01
               with image TestVM-VMDK and flavor m1.micro in nova az.
            4. Bind sub_net port of Vms
            5. Check VMs are not available.
            6. Enable sub_net port of all Vms.
            7. Verify that VMs should communicate between each other.
               Send icmp ping between VMs.


        Duration 1,5 hours

        """

        self.env.revert_snapshot("dvs_vcenter_destructive_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Create new network
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # create security group with rules for ssh and ping
        security_group = {}
        security_group[os_conn.get_tenant(SERVTEST_TENANT).id] =\
            os_conn.create_sec_group_for_ssh()
        security_group = security_group[
            os_conn.get_tenant(SERVTEST_TENANT).id].id

        #  Launch instance VM_1 and VM_2
        network = os_conn.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group
        )

        openstack.create_and_assign_floating_ip(os_conn=os_conn)

        time.sleep(30)  # need time to apply updates

        # Bind sub_net ports of Vms
        ports = os_conn.neutron.list_ports()['ports']
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv_addr = srv.networks[srv.networks.keys()[0]][0]
            for port in ports:
                port_addr = port['fixed_ips'][0]['ip_address']
                if srv_addr == port_addr:
                    os_conn.neutron.update_port(
                        port['id'], {'port': {'admin_state_up': False}}
                    )

        srv_list = os_conn.get_servers()

        # Verify that not connection to VMs
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name
        )

        try:
            openstack.check_connection_vms(
                os_conn=os_conn, srv_list=srv_list, remote=ssh_controller)
        except Exception as e:
            logger.info(str(e))

        # Enable sub_net ports of VMs
        for srv in srv_list:
            srv_addr = srv.networks[srv.networks.keys()[0]][0]
            for port in ports:
                port_addr = port['fixed_ips'][0]['ip_address']
                if srv_addr == port_addr:
                    os_conn.neutron.update_port(
                        port['id'], {'port': {'admin_state_up': True}}
                    )

        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv.reboot()
            wait(
                lambda:
                os_conn.get_instance_detail(srv).status == "ACTIVE",
                timeout=300)
        time.sleep(60)  # need time after reboot to get ip by instance

        # Verify that VMs should communicate between each other.
        # Send icmp ping between VMs
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       remote=ssh_controller)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_reset_controller", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_reset_controller(self):
        """Verify that vmclusters should be migrate after reset controller.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller role.
            5. Add 2 node with compute role.
            6. Deploy the cluster.
            7. Launch instances.
            8. Verify connection between VMs. Send ping
               Check that ping get reply
            9. Reset controller.
            10. Check that vmclusters should be migrate to another controller.
            11. Verify connection between VMs.
                Send ping, check that ping get reply

        Duration 1.8 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

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
        security_group = {}
        security_group[os_conn.get_tenant(SERVTEST_TENANT).id] =\
            os_conn.create_sec_group_for_ssh()
        security_group = security_group[
            os_conn.get_tenant(SERVTEST_TENANT).id].id

        network = os_conn.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group)

        # Verify connection between VMs. Send ping Check that ping get reply
        openstack.create_and_assign_floating_ip(os_conn=os_conn)
        srv_list = os_conn.get_servers()
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )
        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name
        )
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       remote=ssh_controller)

        cmds = ['nova-manage service list | grep vcenter-vmcluster1',
                'nova-manage service list | grep vcenter-vmcluster2']

        openstack.check_service(ssh=ssh_controller, commands=cmds)

        self.fuel_web.warm_restart_nodes(
            [self.fuel_web.environment.d_env.get_node(
                name=primary_controller.name)])
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[1]
        )

        ssh_controller = self.fuel_web.get_ssh_for_node(
            primary_controller.name
        )
        openstack.check_service(ssh=ssh_controller, commands=cmds)

        # Verify connection between VMs. Send ping Check that ping get reply
        srv_list = os_conn.get_servers()
        openstack.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                       remote=ssh_controller)

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_shutdown_controller", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_shutdown_controller(self):
        """Verify that vmclusters should be migrate after shutdown controller.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller role.
            5. Add 2 node with compute role.
            6. Deploy the cluster.
            7. Launch instances.
            8. Verify connection between VMs. Send ping
               Check that ping get reply
            9. Shutdown controller.
            10. Check that vmclusters should be migrate to another controller.
            11. Verify connection between VMs.
                Send ping, check that ping get reply

        Duration 1.8 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

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
        security_group = {}
        security_group[os_conn.get_tenant(SERVTEST_TENANT).id] =\
            os_conn.create_sec_group_for_ssh()
        security_group = security_group[
            os_conn.get_tenant(SERVTEST_TENANT).id].id

        network = os_conn.nova.networks.find(label=self.inter_net_name)
        openstack.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group)

        # Verify connection between VMs. Send ping, check that ping get reply
        openstack.create_and_assign_floating_ip(os_conn=os_conn)
        srv_list = os_conn.get_servers()

        controlers = self.fuel_web.get_devops_nodes_by_nailgun_nodes(
            self.fuel_web.get_nailgun_cluster_nodes_by_roles(
                cluster_id=cluster_id,
                roles=['controller']))

        ssh_controller = self.fuel_web.get_ssh_for_node(controlers[0].name)
        openstack.check_connection_vms(
            os_conn=os_conn,
            srv_list=srv_list,
            remote=ssh_controller
        )

        cmds = ['nova-manage service list | grep vcenter-vmcluster1',
                'nova-manage service list | grep vcenter-vmcluster2']

        openstack.check_service(ssh=ssh_controller, commands=cmds)

        self.fuel_web.warm_shutdown_nodes(
            [self.fuel_web.environment.d_env.get_node(
                name=controlers[0].name)])

        ssh_controller = self.fuel_web.get_ssh_for_node(
            controlers[1].name)

        openstack.check_service(ssh=ssh_controller, commands=cmds)
        # Verify connection between VMs. Send ping Check that ping get reply
        srv_list = os_conn.get_servers()
        openstack.check_connection_vms(
            os_conn=os_conn, srv_list=srv_list,
            remote=ssh_controller
        )
