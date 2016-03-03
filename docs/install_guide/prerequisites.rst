Prerequisites
++++++++++++

The VMware DVS plugin works via manipulation resources of a VMware vSphere
Distributed Switch. It means that it has to have connectivity to precreated and
`well configured
<https://www.vmware.com/products/vsphere/features/distributed-switch>`__
dvSwitch on the vCenter which will be used in this environment.

Please, pay attention that this vSphere Distrubuted Switch should have at least
5.5.0 version:

  .. image:: _static/vds_create.png
