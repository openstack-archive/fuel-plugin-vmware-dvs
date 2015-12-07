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


@test(groups=["plugins", 'dvs_vcenter_plugin', 'dvs_vcenter_system'])
class TestDVSPlugin(TestBasic):

    # constants
    node_name = lambda self, name_node: self.fuel_web. \
        get_nailgun_node_by_name(name_node)['hostname']

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

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

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

        plugin.enable_plugin(cluster_id, self.fuel_web)

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

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

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

        plugin.enable_plugin(cluster_id, self.fuel_web)

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

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'ceilometer': True})

        plugin.enable_plugin(cluster_id, self.fuel_web)

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

        plugin.install_dvs_plugin(self.env.d_env.get_admin_remote())

        # Configure cluster
        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'ceilometer': True})

        plugin.enable_plugin(cluster_id, self.fuel_web)

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
