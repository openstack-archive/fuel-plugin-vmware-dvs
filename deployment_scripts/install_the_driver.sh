#!/bin/bash

# notice
echo Start setup vmware-dvs neutron ml2 plugin > /tmp/fuel-plugin-vmware-dvs.log

# Install the driver.
pip install git+git://github.com/Mirantis/vmware-dvs.git@mos-6.1
