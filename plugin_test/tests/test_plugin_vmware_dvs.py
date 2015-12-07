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
import os
import time


from proboscis import test
from proboscis.asserts import assert_true
from fuelweb_test.helpers import checkers
from devops.helpers.helpers import wait
from devops.error import TimeoutError
from devops.helpers.helpers import tcp_ping


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


@test(groups=["plugins", 'dvs_vcenter_plugin', 'dvs_vcenter_system'])
class TestDVSPlugin(TestBasic):

    # constants
    DVS_PLUGIN_PATH = os.environ.get('DVS_PLUGIN_PATH')
    plugin_name = 'fuel-plugin-vmware-dvs'
    msg = "Plugin couldn't be enabled. Check plugin version. Test aborted"
    dvs_switch_name = ['dvSwitch']
    node_name = lambda self, name_node: self.fuel_web. \
        get_nailgun_node_by_name(name_node)['hostname']

    net_data = [{'net_1': '192.168.112.0/24'},
                {'net_2': '192.168.113.0/24'}]

    def install_dvs_plugin(self):
        # copy plugins to the master node
        checkers.upload_tarball(
            self.env.d_env.get_admin_remote(),
            self.DVS_PLUGIN_PATH, "/var")

        # install plugin
        checkers.install_plugin_check_code(
            self.env.d_env.get_admin_remote(),
            plugin=os.path.basename(self.DVS_PLUGIN_PATH))

    def enable_plugin(self, cluster_id=None):
        assert_true(
            self.fuel_web.check_plugin_exists(cluster_id, self.plugin_name),
            self.msg)
        options = {'metadata/enabled': True,
                   'vmware_dvs_net_maps/value': self.dvs_switch_name[0]}
        self.fuel_web.update_plugin_data(cluster_id, self.plugin_name, options)

        logger.info("cluster is {}".format(cluster_id))

    def create_instances(self, os_conn=None, vm_count=None, nics=None,
                         security_group=None):
        """Create Vms on available hypervisors
        :param os_conn: type object, openstack
        :param vm_count: type interger, count of VMs to create
        :param nics: type dictionary, neutron networks
                         to assign to instance
        :param security_group: type dictionary, security group to assign to
                            instances
        """
        boot_timeout = 300
        # Get list of available images,flavors and hipervisors
        images_list = os_conn.nova.images.list()
        flavors_list = os_conn.nova.flavors.list()
        available_hosts = os_conn.nova.services.list(binary='nova-compute')
        for host in available_hosts:
            if host.zone == 'vcenter':
                image = [image for image
                         in images_list
                         if image.name == 'TestVM-VMDK'][0]
            else:
                image = [image for image
                         in images_list
                         if image.name == 'TestVM'][0]
            os_conn.nova.servers.create(
                flavor=flavors_list[0],
                name='test_{0}'.format(image.name),
                image=image, min_count=vm_count,
                availability_zone='{0}:{1}'.format(host.zone, host.host),
                nics=nics
            )

        # Verify that current state of each VMs is Active
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            assert_true(os_conn.get_instance_detail(srv).status != 'ERROR',
                        "Current state of Vm {0} is {1}".format(
                            srv.name, os_conn.get_instance_detail(srv).status))
            try:
                wait(
                    lambda:
                    os_conn.get_instance_detail(srv).status == "ACTIVE",
                    timeout=boot_timeout)
            except TimeoutError:
                logger.error(
                    "Timeout is reached.Current state of Vm {0} is {1}".format(
                        srv.name, os_conn.get_instance_detail(srv).status))
            # assign security group
            if security_group:
                srv.add_security_group(security_group)

    def check_connection_vms(self, os_conn=None, srv_list=None,
                             result_of_ping=0, remote=None,
                             destination_ip=None):
        """Check network connectivity between instancea and destination ip
           with ping
        :param os_conn: type object, openstack
        :param srv_list: type list, instances
        :param packets: type int, packets count of icmp reply
        :param remote: SSHClient
        :param destination_ip: type list, remote destination ip to
                               check by ping
        """
        creds = ("cirros", "cubswin:)")
        icmp_count = 10

        for srv in srv_list:
            if not remote:
                primary_controller = self.fuel_web.get_nailgun_primary_node(
                    self.env.d_env.nodes().slaves[0]
                )
                remote = self.fuel_web.get_ssh_for_node(
                    primary_controller.name)

            addresses = srv.addresses[srv.addresses.keys()[0]]
            fip = [add['addr'] for add in addresses
                   if add['OS-EXT-IPS:type'] == 'floating'][0]

            wait(lambda: tcp_ping(fip, 22), timeout=120)
            logger.info("Connect to VM {0}".format(fip))

            if not destination_ip:
                for s in srv_list:
                    if s != srv:
                        ip = s.networks[s.networks.keys()[0]][0]
                        ping_command = "ping -c {0} {1}".format(
                            icmp_count, ip)
                        ping_result = os_conn.execute_through_host(
                            remote, fip,
                            ping_command,
                            creds)
                        logger.info("Ping result: \n"
                                    "{0}\n"
                                    "{1}\n"
                                    "exit_code={2}"
                                    .format(ping_result['stdout'],
                                            ping_result['stderr'],
                                            ping_result['exit_code']))

            else:
                for ip in destination_ip:
                    if ip != srv.networks[srv.networks.keys()[0]][0]:
                        ping_command = "ping -c {0} {1}".format(
                            icmp_count, ip)
                        ping_result = os_conn.execute_through_host(
                            remote, fip,
                            ping_command, creds)
                        logger.info("Ping result: \n"
                                    "{0}\n"
                                    "{1}\n"
                                    "exit_code={2}"
                                    .format(ping_result['stdout'],
                                            ping_result['stderr'],
                                            ping_result['exit_code']))
            assert_true(
                result_of_ping == ping_result['exit_code'],
                "Ping VM{0} from Vm {1},"
                " not reached {2}".format(ip, fip, ping_result)
            )

    def check_service(self, ssh=None, commands=None):
        """Check that required nova services are running on controller
        :param ssh: SSHClient
        :param commands: type list, nova commands to execute on controller,
                         example of commands:
                         ['nova-manage service list | grep vcenter-vmcluster1'
        """
        ssh.execute('source openrc')
        for cmd in commands:
            output = list(ssh.execute(cmd)['stdout'])
            wait(
                lambda:
                ':-)' in output[-1].split(' '),
                timeout=200)

    def create_and_assign_floating_ip(self, os_conn, srv_list=None,
                                      ext_net=None, tenant_id=None):
        """Create Vms on available hypervisors
        :param os_conn: type object, openstack
        :param srv_list: type list, objects of created instances
        :param ext_net: type object, neutron external network
        :param tenant_id: type string, tenant id
        """

        if not ext_net:
            ext_net = [net for net
                       in os_conn.neutron.list_networks()["networks"]
                       if net['name'] == "net04_ext"][0]
        if not tenant_id:
            tenant_id = os_conn.get_tenant(SERVTEST_TENANT).id
        ext_net = [net for net
                   in os_conn.neutron.list_networks()["networks"]
                   if net['name'] == "net04_ext"][0]
        if not srv_list:
            srv_list = os_conn.get_servers()
        for srv in srv_list:
            fip = os_conn.neutron.create_floatingip(
                {'floatingip': {
                    'floating_network_id': ext_net['id'],
                    'tenant_id': tenant_id}})
            os_conn.nova.servers.add_floating_ip(
                srv, fip['floatingip']['floating_ip_address']
            )

    def add_router(self, os_conn, router_name, ext_net_name="net04_ext",
                   tenant_name='admin'):
        """Create router with gateway
        :param router_name: type string
        :param ext_net_name: type string
        :param tenant_name: type string
        """

        ext_net = [net for net
                   in os_conn.neutron.list_networks()["networks"]
                   if net['name'] == ext_net_name][0]

        gateway = {"network_id": ext_net["id"],
                   "enable_snat": True
                   }
        tenant_id = os_conn.get_tenant(tenant_name).id
        router_param = {'router': {'name': router_name,
                                   'external_gateway_info': gateway,
                                   'tenant_id': tenant_id}}
        router = os_conn.neutron.create_router(body=router_param)['router']
        return router

    def add_subnet_to_router(self, os_conn, router_id, sub_id):
        os_conn.neutron.add_interface_router(
            router_id,
            {'subnet_id': sub_id}
        )

    def create_network(self, os_conn, name,
                       tenant_name='admin'):
        tenant_id = os_conn.get_tenant(tenant_name).id

        net_body = {"network": {"name": name,
                                "tenant_id": tenant_id
                                }
                    }
        network = os_conn.neutron.create_network(net_body)['network']
        return network

    def create_subnet(self, os_conn, network,
                      cidr, tenant_name='admin'):
        tenant_id = os_conn.get_tenant(tenant_name).id
        subnet_body = {"subnet": {"network_id": network['id'],
                                  "ip_version": 4,
                                  "cidr": cidr,
                                  "name": 'subnet_{}'.format(
                                      network['name'][-1]),
                                  "tenant_id": tenant_id
                                  }
                       }
        subnet = os_conn.neutron.create_subnet(subnet_body)['subnet']
        return subnet

    def get_role(self, os_conn, role_name):
        role_list = os_conn.keystone.roles.list()
        for role in role_list:
            if role.name == role_name:
                return role
        return None

    def add_role_to_user(self, os_conn, user_name, role_name, tenant_name):
        tenant_id = os_conn.get_tenant(tenant_name).id
        user_id = os_conn.get_user(user_name).id
        role_id = self.get_role(os_conn, role_name).id
        os_conn.keystone.roles.add_user_role(user_id, role_id, tenant_id)

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["dvs_vcenter_smoke", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_smoke(self):
        """Deploy cluster with plugin and vmware datastore backend

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Deploy the cluster.
            7. Run OSTF.

        Duration 1.8 hours

        """
        self.env.revert_snapshot("ready_with_3_slaves")

        self.install_dvs_plugin()

        # Configure cluster with 2 vcenter clusters
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )
        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller']}
        )

        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(cluster_id)

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["dvs_vcenter_bvt", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_bvt(self):
        """Deploy cluster with plugin and vmware datastore backend

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Deploy the cluster.
            7. Run OSTF.

        Duration 1.8 hours

        """
        self.env.revert_snapshot("ready_with_3_slaves")

        self.install_dvs_plugin()

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
        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute'], }
        )

        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(
            cluster_id,
            multiclusters=True,
            vc_glance=True
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["dvs_vcenter_systest_setup", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_systest_setup(self):
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
        self.env.revert_snapshot("ready_with_3_slaves")

        self.install_dvs_plugin()

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
        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute-vmware'],
             'slave-03': ['compute'], }
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

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_ha_mode", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_ha_mode(self):
        """Deploy cluster with plugin in HA mode

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller role.
            5. Add 2 node with compute role.
            6. Deploy the cluster.
            7. Run OSTF.

        Duration 2.5 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )

        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['controller'],
             'slave-03': ['controller'],
             'slave-04': ['compute-vmware'],
             'slave-05': ['compute']}
        )

        # Configure VMWare vCenter settings
        target_node_1 = self.node_name('slave-04')
        self.fuel_web.vcenter_configure(
            cluster_id, multiclusters=True,
            target_node_1=target_node_1
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_ceph", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_ceph(self):
        """Deploy cluster with plugin and ceph backend

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller role.
            5. Add 1 node with compute + ceph-osd roles.
            6. Add 1 node with cinder-vmware + ceph-osd roles.
            7. Deploy the cluster
            8. Run OSTF

        Duration 2.5 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'images_ceph': True,
                'volumes_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False})

        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['controller', 'ceph-osd'],
             'slave-03': ['controller', 'ceph-osd'],
             'slave-04': ['compute'],
             'slave-05': ['cinder-vmware']}
        )

        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(cluster_id, multiclusters=True)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_ceph_2", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_ceph_2(self):
        """Deploy cluster with plugin and ceph backend

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Set CephOSD as backend for Glance and Cinder
            5. Add nodes with following roles:
                controller
                compute-vmware
                compute-vmware
                compute
                2 ceph-osd
            6. Deploy the cluster
            7. Run OSTF

        Duration 2.5 hours

        """
        self.env.revert_snapshot("ready_with_9_slaves")

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'images_ceph': True,
                'volumes_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False})

        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute-vmware'],
                'slave-03': ['compute-vmware'],
                'slave-04': ['compute'],
                'slave-05': ['ceph-osd'],
                'slave-06': ['ceph-osd']
            }
        )

        # Configure VMWare vCenter settings
        target_node_1 = self.node_name('slave-02')
        target_node_2 = self.node_name('slave-03')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_1=target_node_1,
            target_node_2=target_node_2,
            multiclusters=True
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id,
            test_sets=['smoke', 'tests_platform'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_5],
          groups=["dvs_vcenter_ceilometer", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_ceilometer(self):
        """Deploy cluster with plugin and ceilometer

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 3 node with controller + mongo roles.
            5. Add 2 node with compute role.
            5. Deploy the cluster.
            6. Run OSTF.

        Duration 3 hours

        """
        self.env.revert_snapshot("ready_with_5_slaves")

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'ceilometer': True})

        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller', 'mongo'],
             'slave-02': ['controller', 'mongo'],
             'slave-03': ['controller', 'mongo'],
             'slave-04': ['compute'],
             'slave-05': ['compute'],
             }
        )

        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(cluster_id, multiclusters=True)

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id,
            test_sets=['smoke', 'tests_platform'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_ceilometer_2", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_ceilometer_2(self):
        """Deploy cluster with plugin and ceilometer

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create cluster with vcenter and ceilometr.
            4. Add nodes with following roles:
                controller
                compute + cinder
                cinder-vmware
                compute-vmware
                compute-vmware
                mongo
            4. Assign vCenter cluster(s) to:
                compute-vmware
            5. Deploy the cluster.
            6. Run OSTF.

        Duration 3 hours

        """
        self.env.revert_snapshot("ready_with_9_slaves")

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'ceilometer': True})

        self.enable_plugin(cluster_id=cluster_id)

        # Assign role to node
        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['compute', 'cinder'],
             'slave-03': ['cinder-vmware'],
             'slave-04': ['compute-vmware'],
             'slave-05': ['compute-vmware'],
             'slave-06': ['mongo']
             }
        )

        # Configure VMWare vCenter settings
        target_node_1 = self.node_name('slave-04')
        target_node_2 = self.node_name('slave-05')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_1=target_node_1,
            target_node_2=target_node_2,
            multiclusters=True
        )

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id,
            test_sets=['smoke', 'tests_platform'])

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

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )

        self.enable_plugin(cluster_id=cluster_id)

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

        self.install_dvs_plugin()

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )

        self.enable_plugin(cluster_id=cluster_id)

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

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_networks", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_networks(self):
        """Check abilities to create and terminate networks on DVS.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Deploy the cluster.
            7. Add 2 private networks net_1 and net_2.
            8. Check that networks are created.
            9. Delete net_1.
            10. Check that net_1 is deleted.
            11. Add net_1 again.

        Duration 1.8 hours

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
            network = self.create_network(
                os_conn,
                net.keys()[0], tenant_name=SERVTEST_TENANT
            )

            logger.info('Create subnet {}'.format(net.keys()[0]))
            subnet = self.create_subnet(
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
        network = self.create_network(
            os_conn,
            self.net_data[0].keys()[0])
        subnet = self.create_subnet(
            os_conn,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name=SERVTEST_TENANT
        )
        assert_true(
            os_conn.get_network(network['name'])['id'] == network['id']
        )
        logger.info('Networks net_2 and net_3 are present.')

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_ping_public", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_ping_public(self):
        """Check connectivity Vms to public network with floating ip.

        Scenario:
            1. Revert snapshot to dvs_vcenter_bvt_2
            2. Create private networks net01 with sunet.
            3. Add one  subnet (net01_subnet01: 192.168.101.0/24
            4. Create Router_01, set gateway and add interface
               to external network.
            5. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            6. Send ping from instances VM_1 and VM_2 to 8.8.8.8
               or other outside ip.

        Duration 1,5 hours

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
        network = self.create_network(
            os_conn,
            self.net_data[0].keys()[0], tenant_name=SERVTEST_TENANT
        )

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = self.create_subnet(
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
        security_group = {}
        security_group[os_conn.get_tenant(SERVTEST_TENANT).id] =\
            os_conn.create_sec_group_for_ssh()
        security_group = security_group[
            os_conn.get_tenant(SERVTEST_TENANT).id].id

        #  Launch instance VM_1, VM_2 in the tenant network net_01
        # with image TestVMDK and flavor m1.micro in the nova az.
        self.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network['id']}], security_group=security_group
        )

        # Add net_1 to default router
        router = os_conn.get_router(os_conn.get_network('net04_ext'))
        self.add_subnet_to_router(
            os_conn,
            router['id'], subnet['id'])

        self.create_and_assign_floating_ip(os_conn=os_conn)

        # Send ping from instances VM_1 and VM_2 to 8.8.8.8
        # or other outside ip.
        srv_list = os_conn.get_servers()
        self.check_connection_vms(
            os_conn=os_conn, srv_list=srv_list,
            destination_ip=['8.8.8.8']
        )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_5_instances", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_5_instances(self):
        """Check creation instance in the one group simultaneously

        Scenario:
            1. Revert snapshot to dvs_vcenter_bvt_2
            2. Upload plugins to the master node
            3. Install plugin.
            4. Create cluster with vcenter.
            5. Add 1 node with controller role.
            6. Add 1 node with compute role.
            7. Deploy the cluster.
            8. Create 5 instances of vcenter and 5 of nova simultaneously.

        Duration 1.8 hours

        """
        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Create 5 instances of vcenter and 5 of nova simultaneously.
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        network = os_conn.nova.networks.find(label='net04')
        self.create_instances(
            os_conn=os_conn, vm_count=5,
            nics=[{'net-id': network.id}])

    @test(depends_on=[dvs_vcenter_systest_setup],
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

        self.env.revert_snapshot("dvs_vcenter_bvt_2")

        # Try to uninstall dvs plugin
        cmd = 'fuel plugins --remove {}==1.1.0'.format(self.plugin_name)
        self.env.d_env.get_admin_remote().execute(cmd)['exit_code'] == 1

        # Check that plugin is not removed
        output = list(self.env.d_env.get_admin_remote().execute(
            'fuel plugins list')['stdout'])

        assert_true(
            self.plugin_name in output[-1].split(' '),
            "Plugin is removed {}".format(self.plugin_name)
        )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_security", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_security(self):
        """Check abilities to create and delete security group.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Deploy the cluster.
            7. Create non default network with subnet net01.
            8. Launch instance 2 VMs of vcenter and 2 VMs of nova
               in the tenant network net_01
            9. Launch instance 2 VMs of vcenter and 2 VMs of nova
               in the tenant net04.
            10. Create security groups SG_1 to allow ICMP traffic.
            11. Add Ingress rule for ICMP protocol to SG_1
            13. Create security groups SG_2 to allow TCP traffic 22 port.
            14. Add Ingress rule for TCP protocol to SG_2
            15. Remove defauld security group and attach SG_1 and SG2 to VMs
            16. Check ssh between VMs
            17. Check ping between VMs
            18. Delete all rules from SG_1 and SG_2
            19. Check  ssh are not available to VMs
                and vice verse
            20. Add Ingress rule for TCP protocol to SG_2
            21. Add Ingress rule for ICMP protocol to SG_1
            22. Check ping between VMs and vice verse
            23. Check SSH between VMs
            25. Delete security groups.
            26. Attach Vms to default security group.
            27. Check  ssh are not available to VMs.

        Duration 1.8 hours

        """

        self.env.revert_snapshot("dvs_vcenter_systest_setup")

        cluster_id = self.fuel_web.get_last_created_cluster()

        # Connect to cluster
        os_ip = self.fuel_web.get_public_vip(cluster_id)
        os_conn = os_actions.OpenStackActions(
            os_ip, SERVTEST_USERNAME,
            SERVTEST_PASSWORD,
            SERVTEST_TENANT)

        # Create non default network with subnet.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = self.create_network(
           os_conn,
           self.net_data[0].keys()[0], tenant_name=SERVTEST_TENANT
        )

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = self.create_subnet(
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
        router = os_conn.get_router(os_conn.get_network('net04_ext'))
        self.add_subnet_to_router(
            os_conn,
            router['id'], subnet['id'])

        #  Launch instance 2 VMs of vcenter and 2 VMs of nova
        #  in the tenant network net_01
        self.create_instances(
            os_conn=os_conn, vm_count=2,
            nics=[{'net-id': network['id']}]
        )

        #  Launch instance 2 VMs of vcenter and 2 VMs of nova
        #  in the tenant network net04
        network = os_conn.nova.networks.find(label='net04')
        self.create_instances(
            os_conn=os_conn, vm_count=2,
            nics=[{'net-id': network.id}])

        self.create_and_assign_floating_ip(os_conn=os_conn)

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

        tcp = os_conn.nova.security_group_rules.create(
            sg1.id, **rulesets[0]
        )
        icmp = os_conn.nova.security_group_rules.create(
            sg2.id, **rulesets[1]
        )

        # Remove defauld security group and attach SG_1 and SG2 to VMs
        srv_list = os_conn.get_servers()
        for srv in srv_list:
            srv.remove_security_group(srv.security_groups[0]['name'])
            srv.add_security_group(sg1.id)
            srv.add_security_group(sg2.id)

        time.sleep(20)  # need wait to update rules on dvs

        # SSh to VMs
        # Check ping between VMs
        self.check_connection_vms(os_conn=os_conn, srv_list=srv_list)

        # Delete all rules from SG_1 and SG_2
        os_conn.nova.security_group_rules.delete(tcp.id)
        os_conn.nova.security_group_rules.delete(icmp.id)

        # Check  ssh are not available between VMs
        # and vice verse
        try:
            self.check_connection_vms(
                os_conn=os_conn, srv_list=srv_list)
        except Exception as e:
            logger.info('{}'.format(e))

        tcp = os_conn.nova.security_group_rules.create(
            sg1.id, **rulesets[0]
        )
        time.sleep(20)  # need wait to update rules on dvs

        # Check  ping are not available between VMs
        srv_list = os_conn.get_servers()
        self.check_connection_vms(os_conn=os_conn, srv_list=srv_list,
                                  result_of_ping=1)

        icmp = os_conn.nova.security_group_rules.create(
            sg2.id, **rulesets[1]
        )
        time.sleep(20)  # need wait to update rules on dvs

        # Check  ping are not available between VMs
        self.check_connection_vms(
            os_conn=os_conn, srv_list=srv_list)

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_tenants_isolation", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_tenants_isolation(self):
        """Verify that VMs on different tenants should not communicate
            between each other. Send icmp ping from VMs
            of admin tenant to VMs of test_tenant and vice versa.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Deploy the cluster.
            7. Create non-admin tenant.
            8. Create network net01 with subnet in non-admin tenant
            9. Create Router_01, set gateway and add interface
               to external network.
            10. Launch instances VM_1 and VM_2 in the net01(non-admin tenant)
               in nova and vcenter az.
            11. Launch instances VM_3 and VM_4 in the net04(default
               admin tenant) in nova and vcenter az.
            12. Verify that VMs on different tenants should not communicate
              between each other via no floating ip. Send icmp ping from VM_3,
              VM_4 of admin tenant to VM_3 VM_4 of test_tenant and vice versa.

        Duration 1,5 hours

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
        self.add_role_to_user(admin, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, 'test', 'test', 'test')

        # Create non default network with subnet in test tenant.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = self.create_network(
            test,
            self.net_data[0].keys()[0], tenant_name='test'
        )

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = self.create_subnet(
            test,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name='test'
        )

        # create security group with rules for ssh and ping
        security_group = {}
        security_group[test.get_tenant('test').id] =\
            test.create_sec_group_for_ssh()
        security_group = security_group[
            test.get_tenant('test').id].id

        #  Launch instance VM_1 and VM_2 in the est tenant network net_01
        self.create_instances(
            os_conn=test, vm_count=1,
            nics=[{'net-id': network['id']}], security_group=security_group
        )

        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = self.add_router(
            test,
            'router_1'
        )

        # Add net_1 to router_1
        self.add_subnet_to_router(
            test,
            router_1['id'], subnet['id'])

        # create security group with rules for ssh and ping
        security_group = {}
        security_group[admin.get_tenant(SERVTEST_TENANT).id] =\
            admin.create_sec_group_for_ssh()
        security_group = security_group[
            admin.get_tenant(SERVTEST_TENANT).id].id

        # Launch instance VM_3 and VM_4 in the admin tenant net04
        network = admin.nova.networks.find(label='net04')
        self.create_instances(
            os_conn=admin, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group)

        # Send ping from instances VM_1 and VM_2 to VM_3 and VM_4
        # via no floating ip
        srv_1 = admin.get_servers()
        srv_2 = test.get_servers()
        self.create_and_assign_floating_ip(os_conn=admin, srv_list=srv_1)
        self.create_and_assign_floating_ip(
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
        self.check_connection_vms(
            os_conn=admin, srv_list=srv_1,
            result_of_ping=1,
            remote=None, destination_ip=ips
        )

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_same_ip", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_same_ip(self):
        """Check connectivity between VMs with same ip in different tenants.

        Scenario:
            1. Upload plugins to the master node
            2. Install plugin.
            3. Create cluster with vcenter.
            4. Add 1 node with controller role.
            5. Add 1 node with compute role.
            6. Deploy the cluster.
            7. Create non-admin tenant.
            8. Create private network net01 with sunet in non-admin tenant.
            9. Create Router_01, set gateway and add interface
               to external network.
            10. Create private network net01 with sunet in default admin tenant
            11. Create Router_01, set gateway and add interface
               to external network.
            12. Launch instances VM_1 and VM_2 in the net01(non-admin tenant)
               with image TestVM and flavor m1.micro in nova az.
            13. Launch instances VM_3 and VM_4
               in the net01(default admin tenant)
               with image TestVM and flavor m1.micro in nova az.
            14. Verify that VM_1 and VM_2 should communicate
               between each other via no floating ip.
            15. Verify that VM_3 and VM_4 should communicate
               between each other via no floating ip.

        Duration 1,5 hours

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
        self.add_role_to_user(admin, 'test', 'admin', 'test')

        test = os_actions.OpenStackActions(
            os_ip, 'test', 'test', 'test')

        # Create non default network with subnet in test tenant.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = self.create_network(
            test,
            self.net_data[0].keys()[0], tenant_name='test'
        )

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = self.create_subnet(
            test,
            network,
            self.net_data[0][self.net_data[0].keys()[0]],
            tenant_name='test'
        )

        # create security group with rules for ssh and ping
        security_group = {}
        security_group[test.get_tenant('test').id] =\
            test.create_sec_group_for_ssh()
        security_group = security_group[
            test.get_tenant('test').id].id

        #  Launch instances in the tenant network net_01
        self.create_instances(
            os_conn=test, vm_count=1,
            nics=[{'net-id': network['id']}], security_group=security_group
        )

        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = self.add_router(
            test,
            'router_1',
            ext_net_name='net04_ext', tenant_name='test'
        )

        # Add net_1 to router_1
        self.add_subnet_to_router(
            test,
            router_1['id'], subnet['id'])

        srv_1 = test.get_servers()
        self.create_and_assign_floating_ip(
            os_conn=test,
            srv_list=srv_1,
            ext_net=None,
            tenant_id=test.get_tenant('test').id)
        srv_1 = test.get_servers()
        # create security group with rules for ssh and ping
        security_group = {}
        security_group[admin.get_tenant(SERVTEST_TENANT).id] =\
            admin.create_sec_group_for_ssh()
        security_group = security_group[
            admin.get_tenant(SERVTEST_TENANT).id].id
        # Create non default network with subnet in admin tenant.
        logger.info('Create network {}'.format(self.net_data[0].keys()[0]))
        network = self.create_network(
            admin,
            self.net_data[0].keys()[0])

        logger.info('Create subnet {}'.format(self.net_data[0].keys()[0]))
        subnet = self.create_subnet(
            admin,
            network,
            self.net_data[0][self.net_data[0].keys()[0]])

        # Launch instance VM_3 and VM_4 in the tenant net04
        self.create_instances(
            os_conn=admin, vm_count=1,
            nics=[{'net-id': network['id']}], security_group=security_group)

        # Create Router_01, set gateway and add interface
        # to external network.
        router_1 = self.add_router(
            admin,
            'router_1')

        # Add net_1 to router_1
        self.add_subnet_to_router(
            admin,
            router_1['id'], subnet['id'])

        # Send ping from instances VM_1 and VM_2 to VM_3 and VM_4
        # via no floating ip
        srv_2 = admin.get_servers()
        self.create_and_assign_floating_ip(
            os_conn=admin,
            srv_list=srv_2)
        srv_2 = admin.get_servers()

        # Verify that VM_1 and VM_2 should communicate
        # between each other via fixed ip.
        self.check_connection_vms(
            os_conn=test, srv_list=srv_1)

        # Verify that VM_3 and VM_4 should communicate
        # between each other via fixed ip.
        self.check_connection_vms(os_conn=admin, srv_list=srv_2)

    @test(depends_on=[dvs_vcenter_systest_setup],
          groups=["dvs_vcenter_bind_port", 'dvs_vcenter_system'])
    @log_snapshot_after_test
    def dvs_vcenter_bind_port(self):
        """Check abilities to bind port on DVS to VM,
           disable and enable this port.

        Scenario:
            1. Revert snapshot to dvs_vcenter_bvt_2
            2. Create private networks net01 with sunet.
            3. Launch instances VM_1 and VM_2 in the net01
               with image TestVM and flavor m1.micro in nova az.
            4. Bind sub_net port of Vm_1 and VM_2
            5. Check VMs are not available.
            6. Enable sub_net port of Vm_1 and VM_2.
            7. Verify that VMs should communicate between each other.
               Send icmp ping from VM 2 to VM1 and vice versa.


        Duration 1,5 hours

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
        security_group = {}
        security_group[os_conn.get_tenant(SERVTEST_TENANT).id] =\
            os_conn.create_sec_group_for_ssh()
        security_group = security_group[
            os_conn.get_tenant(SERVTEST_TENANT).id].id

        #  Launch instance VM_1 and VM_2
        network = os_conn.nova.networks.find(label='net04')
        self.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group
        )

        self.create_and_assign_floating_ip(os_conn=os_conn)

        time.sleep(30)  # need time to apply updates

        # Bind sub_net port of Vm_1 and VM_2
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

        try:
            self.check_connection_vms(
                os_conn=os_conn, srv_list=srv_list)
        except Exception as e:
            logger.info(str(e))

        # Enable sub_net port of Vm_1 and VM_2
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

        self.check_connection_vms(os_conn=os_conn, srv_list=srv_list)

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

        self.install_dvs_plugin()

        # Configure cluster with 2 vcenter clusters and vcenter glance
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )
        self.enable_plugin(cluster_id=cluster_id)

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
        self.fuel_web.vcenter_configure(cluster_id)

        self.fuel_web.deploy_cluster_wait(cluster_id)

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

        network = os_conn.nova.networks.find(label='net04')
        self.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group)

        # Verify connection between VMs. Send ping Check that ping get reply
        self.create_and_assign_floating_ip(os_conn=os_conn)
        srv_list = os_conn.get_servers()
        self.check_connection_vms(os_conn=os_conn, srv_list=srv_list)

        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )

        ssh = self.fuel_web.get_ssh_for_node(primary_controller.name)

        cmds = ['nova-manage service list | grep vcenter-vmcluster1',
                'nova-manage service list | grep vcenter-vmcluster2']

        self.check_service(ssh=ssh, commands=cmds)

        self.fuel_web.warm_restart_nodes(
            [self.fuel_web.environment.d_env.get_node(
                name=primary_controller.name)])
        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[1]
        )

        ssh = self.fuel_web.get_ssh_for_node(primary_controller.name)
        self.check_service(ssh=ssh, commands=cmds)

        # Verify connection between VMs. Send ping Check that ping get reply
        srv_list = os_conn.get_servers()
        self.check_connection_vms(os_conn=os_conn, srv_list=srv_list)

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

        self.install_dvs_plugin()

        # Configure cluster with 2 vcenter clusters and vcenter glance
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )

        self.enable_plugin(cluster_id=cluster_id)

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
        self.fuel_web.vcenter_configure(cluster_id)

        self.fuel_web.deploy_cluster_wait(cluster_id)

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

        network = os_conn.nova.networks.find(label='net04')
        self.create_instances(
            os_conn=os_conn, vm_count=1,
            nics=[{'net-id': network.id}], security_group=security_group)

        # Verify connection between VMs. Send ping Check that ping get reply
        self.create_and_assign_floating_ip(os_conn=os_conn)
        srv_list = os_conn.get_servers()
        self.check_connection_vms(os_conn=os_conn, srv_list=srv_list)

        primary_controller = self.fuel_web.get_nailgun_primary_node(
            self.env.d_env.nodes().slaves[0]
        )

        ssh = self.fuel_web.get_ssh_for_node(primary_controller.name)

        cmds = ['nova-manage service list | grep vcenter-vmcluster1',
                'nova-manage service list | grep vcenter-vmcluster2']

        self.check_service(ssh=ssh, commands=cmds)

        self.fuel_web.warm_shutdown_nodes(
            [self.fuel_web.environment.d_env.get_node(
                name=primary_controller.name)])

        ssh = self.fuel_web.get_ssh_for_node(
            self.env.d_env.nodes().slaves[1].name)

        self.check_service(ssh=ssh, commands=cmds)
        # Verify connection between VMs. Send ping Check that ping get reply
        srv_list = os_conn.get_servers()
        self.check_connection_vms(
            os_conn=os_conn, srv_list=srv_list,
            remote=ssh
        )
