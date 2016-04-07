Troubleshooting
+++++++++++++++

VMware dvs driver consists from two parts: the mechanism driver of neutron and
the agent. Thereby the main source of information for troubleshooting is
/var/log/neutron/server.log and /var/log/neutron/vmware-dvs-agent-....log.

Please to be sure in correctness of configuration in
the /etc/neutron/neutron.conf, /etc/neutron/plugin.ini. and
/etc/neutron/plugins/ml2/vmware_dvs-.....ini It should contain following
values:

neutron.conf::

  notification_driver=messagingv2


plugin.ini::

  [ml2]
  mechanism_drivers =openvswitch,l2population,vmware_dvs
  [ml2_vmware]
  vsphere_login=<vsphere_user>
  vsphere_hostname=<vsphere_ip>
  vsphere_password=<vsphere_password>

vmware_dvs-<vcenter AZ>-<service name>.ini::

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

Sure all neutron-dvs-agent should be launched on corresponded nodes. On
controllers --- under corosync and on compute-vmware --- via init script.

Also in case of trouble would be useful to check the
connectivity between controller nodes and vCenter.
