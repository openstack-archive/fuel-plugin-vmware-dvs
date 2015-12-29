#    Copyright 2015 Mirantis, Inc.
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


from proboscis.asserts import assert_true


from fuelweb_test.helpers import checkers
from fuelweb_test import logger


# constants
DVS_PLUGIN_PATH = os.environ.get('DVS_PLUGIN_PATH')
plugin_name = 'fuel-plugin-vmware-dvs'
msg = "Plugin couldn't be enabled. Check plugin version. Test aborted"
dvs_switch_name = ['dvSwitch']


def install_dvs_plugin(master_node):
    # copy plugins to the master node
    checkers.upload_tarball(
        master_node,
        DVS_PLUGIN_PATH, "/var")

    # install plugin
    checkers.install_plugin_check_code(
        master_node,
        plugin=os.path.basename(DVS_PLUGIN_PATH))


def enable_plugin(cluster_id, fuel_web_client):
    assert_true(
        fuel_web_client.check_plugin_exists(cluster_id, plugin_name),
        msg)

    cluster_attr = fuel_web_client.client.get_cluster_attributes(cluster_id)
    plugin_data = cluster_attr['editable'][plugin_name]
    plugin_data['metadata']['enabled'] = True
    plugin_data['metadata']['versions'][0]['vmware_dvs_net_maps']['value'] = \
        dvs_switch_name[0]
    fuel_web_client.client.update_cluster_attributes(cluster_id, cluster_attr)

    logger.info("cluster is {}".format(cluster_id))
