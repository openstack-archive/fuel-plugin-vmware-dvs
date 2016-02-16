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
from proboscis import test

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import NEUTRON_SEGMENT_TYPE
from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic

from helpers import plugin


@test(groups=["plugins", 'dvs_vcenter_plugin'])
class TestDVSPlugin(TestBasic):

    # constants
    node_name = lambda self, name_node: self.fuel_web. \
        get_nailgun_node_by_name(name_node)['hostname']

    @test(depends_on=[SetupEnvironment.prepare_slaves_3],
          groups=["dvs_vcenter_smoke", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_smoke(self):
        """Check deployment with VMware DVS plugin and one controller.

        Scenario:
            1. Upload plugins to the master node
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
            8. Enable VMWare vCenter/ESXi datastore for images (Glance)
            9  Configure VMware vCenter Settings.
               Add 1 vSphere clusters and configure Nova Compute instances
               on conrollers.
            10. Deploy the cluster.
            11. Run OSTF.

        Duration 1.8 hours

        """
        self.env.revert_snapshot("ready_with_3_slaves")

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

        # Configure cluster with 2 vcenter clusters
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
            {'slave-01': ['controller']}
        )

        # Configure VMWare vCenter settings
        self.fuel_web.vcenter_configure(cluster_id, vcenter_glance=True)

        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_bvt", "dvs_vcenter_plugin"])
    @log_snapshot_after_test
    def dvs_vcenter_bvt(self):
        """Deploy cluster with DVS plugin and ceph storage.

        Scenario:
            1. Upload plugins to the master node
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
                * Compute
                * CephOSD
                * CephOSD
                * CinderVMware
                * ComputeVMware
            5. Configure interfaces on nodes.
            6. Configure network settings.
            7. Enable and configure DVS plugin.
               Configure VMware vCenter Settings. Add 2 vSphere clusters
               and configure Nova Compute instances on conroller
               and compute-vmware.
            8. Verify networks.
            9. Deploy the cluster.
            10. Run OSTF.

        Duration 1.8 hours

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
                'images_ceph': True,
                'volumes_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False
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
             'slave-05': ['compute-vmware'],
             'slave-06': ['cinder-vmware'],
             'slave-07': ['ceph-osd'],
             'slave-08': ['ceph-osd'],
             'slave-09': ['ceph-osd']}
        )

        # Configure VMWare vCenter settings
        target_node_2 = self.node_name('slave-05')
        self.fuel_web.vcenter_configure(
            cluster_id,
            target_node_2=target_node_2,
            multiclusters=True
        )

        self.fuel_web.verify_network(cluster_id)
        self.fuel_web.deploy_cluster_wait(cluster_id)

        self.fuel_web.run_ostf(
            cluster_id=cluster_id, test_sets=['smoke'])
