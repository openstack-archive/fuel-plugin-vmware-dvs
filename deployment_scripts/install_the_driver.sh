#!/bin/bash

plugin_name=fuel-plugin-vmware-dvs
plugin_version=1.0
ip=`hiera master_ip`
port=8080

function _nova_patch {
    wget -O /usr/lib/python2.7/dist-packages/nova.patch "http://$ip:$port/plugins/$plugin_name-$plugin_version/nova.patch" && cd /usr/lib/python2.7/dist-packages/ ; patch -N -p1 < nova.patch
    for resource in $(crm_mon -1|awk '/nova_compute_vmware/ {print $1}'); do
        execute_node=$(crm resource status $resource | cut -f 6 -d\ )
        if [ "$execute_node"="$(hostname)" ];
        then
            crm resource restart $resource
        fi
    done
}

function _dirty_hack {
    cd /usr/lib/python2.7/dist-packages/oslo
    mv messaging messaging.old
    cd /usr/lib/python2.7/dist-packages/
    mv suds suds.old
}

function _core_install {
    easy_install pip
    apt-get -y install git-core python-dev
}

function _driver_install {
    cd /usr/local/lib/python2.7/dist-packages/
    pip install -e git+git://github.com/yunesj/suds#egg=suds
    pip install oslo.messaging==1.8.3
    pip install git+git://github.com/Mirantis/vmware-dvs.git@mos-6.1
}

function _ln {
    cd /usr/local/lib/python2.7/dist-packages/oslo
    ln -s /usr/lib/python2.7/dist-packages/oslo/db
    ln -s /usr/lib/python2.7/dist-packages/oslo/rootwrap
}

function _del_network {
    . /root/openrc
    router=router04
    neutron router-gateway-clear $router
    port=$(neutron router-port-list $router| grep  ip_a| cut -f 2 -d\ )
    neutron router-interface-delete $router port=$port
    neutron port-delete $port
    neutron net-delete net04
    neutron net-delete net04_ext
}

_del_network
_nova_patch
_core_install
_dirty_hack
_driver_install
_ln
