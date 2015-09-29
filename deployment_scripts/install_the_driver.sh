#!/bin/bash

plugin_name=fuel-plugin-vmware-dvs
plugin_version=1.1
ip=`hiera master_ip`
port=8080
_hostname=$(hostname)
haproxy_cfg="/etc/haproxy/conf.d/085-neutron.cfg"

function _restart_crm_resource {
    res=$1
    _where=$(crm resource show $res| awk '{print $6}')
    if [ "$_where" = "$_hostname" ];
    then
        echo restart $res
        crm resource restart $res
    else
        echo resource $res launched not here
        echo does not restart
    fi
}

function _nova_patch {
    wget -O /usr/lib/python2.7/dist-packages/nova.patch "http://$ip:$port/plugins/$plugin_name-$plugin_version/nova.patch" && cd /usr/lib/python2.7/dist-packages/ ; patch -N -p1 < nova.patch
    sed -i s/neutron_url_timeout=.*/neutron_url_timeout=3600/ /etc/nova/nova.conf
    for resource in $(crm_mon -1|awk '/nova_compute_vmware/ {print $1}'); do
        _restart_crm_resource $resource
     done
}

function _haproxy_config {
    if grep -q "timeout server" $haproxy_cfg;
    then
        echo "Timeout already set"
    else
        echo "Setting timeout"
        echo '  timeout server 1h' >> $haproxy_cfg
    fi
    _restart_crm_resource p_haproxy
}

function _core_install {
    easy_install pip
    apt-get -y install git-core python-dev
}

function _driver_install {
    cd /usr/local/lib/python2.7/dist-packages/
    pip install git+git://github.com/Mirantis/vmware-dvs.git
}


_haproxy_config
_nova_patch
_core_install
_driver_install
