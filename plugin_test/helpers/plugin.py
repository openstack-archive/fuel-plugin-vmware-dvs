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

from proboscis.asserts import assert_true

from fuelweb_test import logger
from fuelweb_test.helpers import utils

# constants
DVS_PLUGIN_PATH = os.environ.get('DVS_PLUGIN_PATH')
DVS_PLUGIN_VERSION = os.environ.get('DVS_PLUGIN_VERSION')
DVS_SWITCHES = os.environ.get('DVS_SWITCHES').strip().split(',')
DVS_UPLINKS = os.environ.get('DVS_UPLINKS').strip().split(',')
VCENTER_CLUSTERS = os.environ.get('VCENTER_CLUSTERS').strip().split(',')
msg = "Plugin couldn't be enabled. Check plugin version. Test aborted"
plugin_name = "fuel-plugin-vmware-dvs"


def install_dvs_plugin(master_node):
    """Download and instal DVS plugin on master node."""
    # copy plugins to the master node
    utils.upload_tarball(master_node, DVS_PLUGIN_PATH, "/var")

    # install plugin
    utils.install_plugin_check_code(master_node,
                                    os.path.basename(DVS_PLUGIN_PATH))


def enable_plugin(cluster_id, fuel_web_client, multiclusters=True, tu=0, fu=0):
    """Enable DVS plugin on cluster.

    :param cluster_id: cluster id
    :param fuel_web_client: fuel_web
    :param multiclusters: boolean. True if Multicluster is used.
    :param tu: int, amount of teaming uplinks
    :param fu: int, amount of falback uplinks
    :return: None
    """
    checker = fuel_web_client.check_plugin_exists(cluster_id, plugin_name)
    assert_true(checker, msg)
    opts = {'vmware_dvs_net_maps/value': make_map_data(multiclusters, tu, fu)}
    logger.info("cluster is {0}".format(cluster_id))
    fuel_web_client.update_plugin_settings(cluster_id, plugin_name,
                                           DVS_PLUGIN_VERSION, opts)


def make_map_data(multiclusters=False, tu=2, fu=1):
    """ Make DVS mapping data to paste it to options

    :param multiclusters: boolean. True if Multicluster is used.
    :param tu: int, amount of teaming uplinks
    :param fu: int, amount of falback uplinks
    :return:
    """
    assert_true(False if fu > 0 and tu == 0 else True,
                "We couldn't set Fallback uplinks "
                "if amount of teaming uplinks equals zero."
                "tu = {0}, fu = {1}".format(tu, fu))

    map_sw_cl = map(lambda x, y: "{0}:{1}".format(x, y),
                    VCENTER_CLUSTERS, DVS_SWITCHES)
    if any([tu, fu]):
        assert_true(tu + fu <= len(DVS_UPLINKS), 'Not enough uplinks')
        data = [c + ':' + ';'.join(DVS_UPLINKS[:tu]) for c in map_sw_cl]
        if fu > 0:
            data = [v + ':' + ';'.join(DVS_UPLINKS[tu:tu+fu]) for v in data]
        return '\n'.join(data if multiclusters else data[0:1])
    else:
        return '\n'.join(map_sw_cl if multiclusters else map_sw_cl[0:1])