#!/bin/bash

if [ -f /etc/primary-controller.yaml ]; then
    ln -sf /etc/primary-controller.yaml /etc/astute.yaml
else
    ln -sf /etc/controller.yaml /etc/astute.yaml
fi

plugin_name=fuel-plugin-vmware-dvs
plugin_version=1.1
ip=`hiera master_ip`
role=`hiera role`
port=8080
_hostname=$(hostname)

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

}

function _restart_nova {
    for resource in $(crm_mon -1|awk '/nova_compute_vmware/ {print $1}'); do
        _restart_crm_resource $resource
    done
}

case $role in
controller|primary-controller)
     _nova_patch
     _restart_nova
     ;;
compute-vmware)
     _nova_patch
     service nova-compute restart
     ;;
*)
     echo "Not a vmware compute node"
     ;;
esac
