#!/bin/bash

. /root/openrc

glance image-update $(glance image-list | awk '/ TestVM / {print $2}') --property hypervisor_type=qemu
glance image-update $(glance image-list | awk '/ TestVM-VMDK / {print $2}') --property hypervisor_type=vmware
