Troubleshooting
+++++++++++++++

VMware dvs driver consists from two parts: the mechanism driver of neutron and
the agent. Thereby the main source of information for troubleshooting is
/var/log/neutron/server.log and /var/log/neutron/vmware-dvs-agent-....log.

Please to be sure in correctness of configuration in
the /etc/neutron/plugin.ini and
/etc/neutron/plugins/ml2/vmware_dvs-.....ini It should contain following
values:

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
  network_maps=physnet2:<dvSwitch>
  vsphere_hostname=<vsphere_ip>
  vsphere_password=<vsphere_password>

Sure all neutron-dvs-agent should be launched on corresponded nodes. On
controllers --- under corosync and on compute-vmware --- via init script.

Neutron-dvs-agents must be in active state with cluster host name:

  root@node-1:~# neutron agent-list -c agent_type -c alive -c host

  +--------------------+-------+--------------------------+
  | agent_type         | alive | host                     |
  +--------------------+-------+--------------------------+
  | Open vSwitch agent | :-)   | node-1.test.domain.local |
  | DHCP agent         | :-)   | node-1.test.domain.local |
  | L3 agent           | :-)   | node-1.test.domain.local |
  | DVS agent          | :-)   | vcenter-asdf             |
  | Metadata agent     | :-)   | node-1.test.domain.local |
  | DVS agent          | :-)   | vcenter-qwer             |
  ...

Also in case of trouble would be useful to check the
connectivity between controller nodes and vCenter.
