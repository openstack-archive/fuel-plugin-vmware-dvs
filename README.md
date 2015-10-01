fuel-plugin-vmware-dvs
============

There is the Fuel plugin which provides Neutron for networking on
VMware-related MOS environments.

Installation
============

For fuel-plugin-builder v2 there is only one difference from normal plugin
installation way. Before building the plugin you have to patch
plugin_rpm.spec.mako file which is a part of the fuel plugin builder.

Just do
$ cd /path/to/fuel-plugin-vmware-dvs; sudo patch /path/to/plugin_rpm.spec.mako hack.diff
