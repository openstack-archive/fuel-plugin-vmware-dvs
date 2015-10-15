#!/bin/bash

. /root/openrc

glance image-update TestVM --property hypervisor_type=qemu
glance image-update TestVM-VMDK --property hypervisor_type=vmware
