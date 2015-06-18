#!/bin/bash

set -e

plugin_name=fuel-plugin-vmware-dvs
plugin_version=1.0
ip=`hiera master_ip`
port=8080

url=http://$ip:$port/plugins/$plugin_name-$plugin_version/vmware-dvs

pip install $url
