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
from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import NEUTRON_SEGMENT_TYPE
from helpers import plugin

TestBasic = fuelweb_test.tests.base_test_case.TestBasic
SetupEnvironment = fuelweb_test.tests.base_test_case.SetupEnvironment


@test(groups=['plugins', 'dvs_vcenter_plugin', 'dvs_vcenter_smoke'])
class TestDVSSmoke(TestBasic):
    """Smoke test suite.

    The goal of smoke testing is to ensure that the most critical features
    of Fuel VMware DVS plugin work after new build delivery. Smoke tests
    will be used by QA to accept software builds from Development team.
    """

    @test(depends_on=[SetupEnvironment.prepare_slaves_1],
          groups=["dvs_install"])
    @log_snapshot_after_test
    def dvs_install(self):
        """Check that plugin can be installed.

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Ensure that plugin is installed successfully using cli,
               run command 'fuel plugins'. Check name, version of plugin.

        Duration: 30 min

        """
        self.env.revert_snapshot("ready_with_1_slaves")

        self.show_step(1)
        self.show_step(2)
        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        self.show_step(3)
        cmd = 'fuel plugins list'

        output = self.ssh_manager.execute_on_remote(
            ip=self.ssh_manager.admin_ip, cmd=cmd
        )['stdout'].pop().split(' ')

        # check name
        assert_true(
            plugin.plugin_name in output,
            "Plugin '{0}' is not installed.".format(plugin.plugin_name))
        # check version
        assert_true(
            plugin.DVS_PLUGIN_VERSION in output,
            "Plugin '{0}' is not installed.".format(plugin.plugin_name))
        self.env.make_snapshot("dvs_install", is_make=True)

    @test(depends_on=[dvs_install],
          groups=["dvs_uninstall"])
    @log_snapshot_after_test
    def dvs_uninstall(self):
        """Check that plugin can be removed.

        Scenario:
            1. Revert to snapshot 'dvs_install'.
            2. Remove plugin.
            3. Verify that plugin is removed, run command 'fuel plugins'.

        Duration: 5 min

        """
        self.show_step(1)
        self.env.revert_snapshot("dvs_install")

        self.show_step(2)
        cmd = 'fuel plugins --remove {0}=={1}'.format(
            plugin.plugin_name, plugin.DVS_PLUGIN_VERSION)

        self.ssh_manager.execute_on_remote(ip=self.ssh_manager.admin_ip,
                                           cmd=cmd,
                                           err_msg='Can not remove plugin.')

        self.show_step(3)
        output = self.ssh_manager.execute_on_remote(
            ip=self.ssh_manager.admin_ip,
            cmd='fuel plugins list')['stdout'].pop().split(' ')

        assert_true(plugin.plugin_name not in output,
                    "Plugin '{0}' is not removed".format(plugin.plugin_name))

    @test(depends_on=[dvs_install],
          groups=["dvs_vcenter_smoke"])
    @log_snapshot_after_test
    def dvs_vcenter_smoke(self):
        """Check deployment with VMware DVS plugin and one controller.

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create a new environment with following parameters:
                * Compute: KVM/QEMU with vCenter
                * Networking: Neutron with VLAN segmentation
                * Storage: default
                * Additional services: default
            4. Add 1 node with controller role.
            5. Configure interfaces on nodes.
            6. Configure network settings.
            7. Enable and configure DVS plugin.
            8. Configure VMware vCenter Settings.
               Add 1 vSphere clusters and configure Nova Compute instances
               on controllers.
            9. Deploy the cluster.
            10. Run OSTF.

        Duration: 1.8 hours

        """
        self.show_step(1)
        self.show_step(2)
        self.env.revert_snapshot("dvs_install")

        # Configure cluster with 2 vcenter clusters
        self.show_step(3)

        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web, multiclusters=False)

        # Assign role to node
        self.show_step(4)
        self.fuel_web.update_nodes(cluster_id, {'slave-01': ['controller']})

        # Configure VMWare vCenter settings
        self.show_step(5)
        self.show_step(6)
        self.show_step(7)
        self.show_step(8)
        self.fuel_web.vcenter_configure(cluster_id)

        self.show_step(9)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.show_step(10)
        self.fuel_web.run_ostf(cluster_id=cluster_id, test_sets=['smoke'])


@test(groups=["plugins", 'dvs_vcenter_bvt'])
class TestDVSBVT(TestBasic):
    """Build verification test."""

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_bvt"])
    @log_snapshot_after_test
    def dvs_vcenter_bvt(self):
        """Deploy cluster with DVS plugin and ceph storage.

        Scenario:
            1. Upload plugins to the master node.
            2. Install plugin.
            3. Create a new environment with following parameters:
                * Compute: KVM/QEMU with vCenter
                * Networking: Neutron with VLAN segmentation
                * Storage: ceph
                * Additional services: default
            4. Add nodes with following roles:
                * Controller
                * Controller
                * Controller
                * Compute + CephOSD
                * Compute + CephOSD
                * Compute + CephOSD
                * CinderVMware + ComputeVMware
            5. Configure interfaces on nodes.
            6. Configure network settings.
            7. Enable and configure DVS plugin.
               Configure VMware vCenter Settings. Add 2 vSphere clusters
               and configure Nova Compute instances on conroller
               and compute-vmware.
            8. Verify networks.
            9. Deploy the cluster.
            10. Run OSTF.

        Duration: 1.8 hours

        """
        self.env.revert_snapshot("ready_with_9_slaves")

        self.show_step(1)
        self.show_step(2)
        plugin.install_dvs_plugin(self.ssh_manager.admin_ip)

        # Configure cluster with 2 vcenter clusters and vcenter glance
        self.show_step(3)

        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'images_ceph': True,
                'volumes_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False
            }
        )
        plugin.enable_plugin(cluster_id, self.fuel_web)

        # Assign roles to nodes
        self.show_step(4)

        self.fuel_web.update_nodes(
            cluster_id,
            {'slave-01': ['controller'],
             'slave-02': ['controller'],
             'slave-03': ['controller'],
             'slave-04': ['compute', 'ceph-osd'],
             'slave-05': ['compute', 'ceph-osd'],
             'slave-06': ['compute', 'ceph-osd'],
             'slave-07': ['compute-vmware', 'cinder-vmware']})

        # Configure VMWare vCenter settings
        self.show_step(5)
        self.show_step(6)
        self.show_step(7)

        target_node_2 = self.fuel_web.get_nailgun_node_by_name('slave-07')
        target_node_2 = target_node_2['hostname']
        self.fuel_web.vcenter_configure(cluster_id,
                                        target_node_2=target_node_2,
                                        multiclusters=True)

        self.show_step(8)
        self.fuel_web.verify_network(cluster_id, timeout=60 * 15)

        self.show_step(9)
        self.fuel_web.deploy_cluster_wait(cluster_id, timeout=3600 * 3)

        self.show_step(10)
        self.fuel_web.run_ostf(cluster_id=cluster_id, test_sets=['smoke'])

        self.env.make_snapshot("dvs_bvt", is_make=True)
