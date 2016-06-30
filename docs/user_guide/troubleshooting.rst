Troubleshooting
~~~~~~~~~~~~~~~

This section contains a guidance on how to ensure that the VMware DVS plugin
is up and running on your deployed environment.

**To find logs**

The VMware DVS driver consists of two parts: the mechanism driver of Neutron
and the VMware DVS agent. Therefore, two main sources of information for
troubleshooting are:

* ``/var/log/neutron/server.log``
* ``/var/log/neutron/vmware-dvs-agent-....log``

**To verify Neutron configuration files**
 
To deliver a stable performance of the VMware DVS plugin, verify that the
Neutron configuration files contain the following values:

* ``/etc/neutron/neutron.conf``:

  .. code-block:: ini

   notification_driver=messagingv2

* ``/etc/neutron/plugin.ini``:

  .. code-block:: ini

   [ml2]
   mechanism_drivers =openvswitch,l2population,vmware_dvs
   [ml2_vmware]
   vsphere_login=<vsphere_user>
   vsphere_hostname=<vsphere_ip>
   vsphere_password=<vsphere_password>

* ``/etc/neutron/plugins/ml2/vmware_dvs-<vcenter AZ>-<service name>.ini``:

  .. code-block:: ini

   [DEFAULT]
   host=<vcenter AZ>-<service name>

   [securitygroup]
   enable_security_group = True
   firewall_driver=mech_vmware_dvs.agentDVS.vCenter_firewall.DVSFirewallDriver

   [ml2_vmware]
   vsphere_login=<vsphere_user>
   network_maps=physnet2:<VDS>
   vsphere_hostname=<vsphere_ip>
   vsphere_password=<vsphere_password>

**To verify neutron-dvs-agent services**

All neutron-dvs-agent services should be launched on the corresponding
nodes:

* On controllers: under Corosync
* On compute-vmware: using the init script

**To verify connectivity**

Check the connectivity between controller nodes and vCenter using the
:command:`ping` command.
