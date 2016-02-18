Troubleshooting
+++++++++++++++

VMware dvs driver works as the mechanism driver of neutron. Due to the fact of
that the main source of information for troubleshooting is
/var/log/neutron/server.log. Please to be sure in correctness of configuration
in the /etc/neutron/neutron.conf and /etc/neutron/plugin.ini. It should contain
following values:

neutron.conf::

  notification_driver=messagingv2
  notification_topics=notifications,vmware_dvs

plugin.in::

  [ml2]
  mechanism_drivers =openvswitch,l2population,vmware_dvs
  [ml2_vmware]
  vsphere_login=<vsphere_user>
  network_maps=physnet2:<VDS>
  vsphere_hostname=<vsphere_ip>
  vsphere_password=<vsphere_password>

Also in case of trouble would be useful to check the
connectivity between controller nodes and vCenter.
