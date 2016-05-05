Prerequisites
++++++++++++

The VMware DVS plugin works via manipulation resources of a VMware vSphere
Distributed Switch. It requires a vCenter service account with the following
minimum permissions:

+----------------+--------------------+------------------------------+
| All privileges |                    |                              |
+----------------+--------------------+------------------------------+
|                | Distributed switch | Port configuration operation |
+----------------+--------------------+------------------------------+
|                | dvPort group       | Create                       |
+----------------+--------------------+------------------------------+
|                |                    | Delete                       |
+----------------+--------------------+------------------------------+
|                |                    | Modify                       |
+----------------+--------------------+------------------------------+

The Plugin doesn't create new VDS'es but uses existed ones. It means that it has
to have connectivity to precreated and
`well configured
<https://www.vmware.com/products/vsphere/features/distributed-switch>`__
VDS'es on the vCenter which will be used in this environment.
