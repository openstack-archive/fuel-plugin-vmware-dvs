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
DVS_SWITCHS = os.environ.get('DVS_SWITCHS').split(',')
VCENTER_CLUSTERS = os.environ.get('VCENTER_CLUSTERS').split(',')
msg = "Plugin couldn't be enabled. Check plugin version. Test aborted"
dvs_clusters_map = zip(VCENTER_CLUSTERS, DVS_SWITCHS)


def get_dvs_plugin_data(master_node):
    """ Get plugin data from output of command fuel plugins list.

    """
    output = list(master_node.execute(
            'fuel plugins list')['stdout'])

    dvs_plugin_data = dict(
        zip([j.replace('\n', '')
            for j in[
                i.replace(' ', '')
                for i in output[0].split('|')]
            ],
            [j.replace('\n', '')
             for j in[
                i.replace(' ', '')
                for i in output[2].split('|')]
            ]
        )
    )

    return dvs_plugin_data


def install_dvs_plugin(master_node):
    """Download and instal DVS plugin on master node.

    """
    # copy plugins to the master node
    checkers.upload_tarball(
        master_node,
        DVS_PLUGIN_PATH, "/var")

    # install plugin
    checkers.install_plugin_check_code(
        master_node,
        plugin=os.path.basename(DVS_PLUGIN_PATH))

    # get plugin dada
    dvs_plugin_data = get_dvs_plugin_data(master_node)
    return dvs_plugin_data


def enable_plugin(
    cluster_id, fuel_web_client, dvs_plugin_data, multiclusters=True):
    """Enable DVS plugin on cluster

    """
    assert_true(
        fuel_web_client.check_plugin_exists(
            cluster_id, dvs_plugin_data['name']),
        msg)
    if multiclusters is True:
        vmware_dvs_net_maps = '{0};{1}'.format(
            ':'.join(dvs_clusters_map[0]), ':'.join(dvs_clusters_map[1])
        )
    else:
        vmware_dvs_net_maps = ''.format(':'.join(dvs_clusters_map[0]))

    logger.info("cluster is {}".format(cluster_id))

    options = {'vmware_dvs_net_maps/value': vmware_dvs_net_maps}

    fuel_web_client.update_plugin_settings(
        cluster_id, dvs_plugin_data['name'],
        dvs_plugin_data['version'], options)
