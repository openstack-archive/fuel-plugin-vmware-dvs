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

from fuelweb_test import logger

from fuelweb_test.helpers.decorators import log_snapshot_after_test

from fuelweb_test.settings import DEPLOYMENT_MODE
from fuelweb_test.settings import NEUTRON_SEGMENT_TYPE

from fuelweb_test.tests.base_test_case import SetupEnvironment
from fuelweb_test.tests.base_test_case import TestBasic

from fuelweb_test.tests.test_net_templates_base import TestNetworkTemplatesBase

from helpers import plugin

from proboscis import test

import yaml


@test(groups=["dvs_vcenter_net_template"])
class TestNetworkTemplates(TestNetworkTemplatesBase, TestBasic):
    """TestNetworkTemplates."""

    def node_name(self, name_node):
        """Get node by name."""
        return self.fuel_web.get_nailgun_node_by_name(name_node)['hostname']

    def get_network_template(self, template_name):
        """Get netwok template.

        param: template_name: type string, name of file
        """
        template = 'plugin_test/templates/{0}.yaml'.format(template_name)
        logger.info('{0}'.format(template))
        if os.path.exists(template):
            with open(template) as template_file:
                return yaml.load(template_file)

    @test(depends_on=[SetupEnvironment.prepare_slaves_9],
          groups=["dvs_vcenter_net_template"])
    @log_snapshot_after_test
    def dvs_vcenter_net_template(self):
        """Deploy cluster with DVS plugin, Neutron, Ceph and network template.

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
                3 ceph-osd
            6. Upload network template.
            7. Check network configuration.
            8. Deploy the cluster
            9. Run OSTF

        Duration 2.5 hours

        Duration 180m
        Snapshot deploy_cinder_net_tmpl
        """
        self.env.revert_snapshot("ready_with_9_slaves")

        plugin.install_dvs_plugin(
            self.ssh_manager.admin_ip)

        cluster_id = self.fuel_web.create_cluster(
            name=self.__class__.__name__,
            mode=DEPLOYMENT_MODE,
            settings={
                "net_provider": 'neutron',
                "net_segment_type": NEUTRON_SEGMENT_TYPE,
                'images_ceph': True,
                'volumes_ceph': True,
                'objects_ceph': True,
                'volumes_lvm': False,
                'tenant': 'netTemplate',
                'user': 'netTemplate',
                'password': 'netTemplate',
            }
        )

        plugin.enable_plugin(cluster_id, self.fuel_web)

        self.fuel_web.update_nodes(
            cluster_id,
            {
                'slave-01': ['controller'],
                'slave-02': ['compute-vmware'],
                'slave-03': ['compute-vmware'],
                'slave-04': ['compute'],
                'slave-05': ['ceph-osd'],
                'slave-06': ['ceph-osd'],
                'slave-07': ['ceph-osd'],
            },
            update_interfaces=False
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

        network_template = self.get_network_template('default')
        self.fuel_web.client.upload_network_template(
            cluster_id=cluster_id, network_template=network_template)
        networks = self.generate_networks_for_template(
            template=network_template,
            ip_nets={'default': '10.200.0.0/16'},
            ip_prefixlen='24')
        existing_networks = self.fuel_web.client.get_network_groups()
        networks = self.create_custom_networks(networks, existing_networks)

        logger.debug('Networks: {0}'.format(
            self.fuel_web.client.get_network_groups()))

        self.fuel_web.verify_network(cluster_id)

        self.fuel_web.deploy_cluster_wait(cluster_id, timeout=180 * 60)

        self.fuel_web.verify_network(cluster_id)

        self.check_ipconfig_for_template(cluster_id, network_template,
                                         networks)
        self.check_services_networks(cluster_id, network_template)

        self.fuel_web.run_ostf(cluster_id=cluster_id,
                               timeout=3000,
                               test_sets=['smoke', 'sanity',
                                          'ha', 'tests_platform'])
        self.check_ipconfig_for_template(cluster_id, network_template,
                                         networks)

        self.check_services_networks(cluster_id, network_template)
