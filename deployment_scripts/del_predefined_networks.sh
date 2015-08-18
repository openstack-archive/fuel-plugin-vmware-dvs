#!/bin/bash

. /root/openrc
router=router04

neutron router-gateway-clear $router

for port in $(neutron router-port-list $router| grep  ip_a| cut -f 2 -d\ ); do
    neutron router-interface-delete $router port=$port
    neutron port-delete $port
done

for net in $(neutron net-list|grep '/'|cut -f 4 -d\ ); do
    neutron net-delete $net
done
