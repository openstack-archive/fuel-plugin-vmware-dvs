=============================================
Fuel plugin for Neutron ML2 vmware_dvs driver
=============================================

There is the Fuel plugin which provides Neutron for networking on
VMware-related MOS environments.

Problem description
===================

Modern facilities to networking in OpenStack is Neutron which replaces obsolete
nova-networks. Unfortunately integration with VMware which realized in Fuel 6.1
and below doesn't provide the possibilities to using Neutron. It leads that an
environment which uses VMware hypervisors is greatly limited. When customers
(especially huge customers) want to replicate rich enterprise network
topologies:

* Ability to create multi-tier networks (e.g., web tier, db tier, app tier).

* Control over IP addressing.

* Ability to insert an configure their own services (e.g., firewall, IPS)

* VPN/Bridge to remote physical hosting or customer premises.

Nova-networks can offer:

* No way to control topology.

* Cloud assigns IP prefixes and addresses.

* No generic service insertion.

Such we have the contradiction between customer needs and our solution.

Proposed change
===============

The Neutron has pluggable architecture which provides using different backends
in different cases simultaneously by using ML2 plugin [0]. There is the
vmware_dvs driver [1] which provides using Neutron for networking in
vmware-related environments. And it is exactly what we want.

This plugin automates installation and configuration the vmware_dvs driver and
its dependencies (it carries all of them with it to be independent from public
network). After driver installation it changes configuration files
/etc/neutron/neutron.conf and /etc/neutron/plugin.ini whereby neutron-server
can manage networking on vCenter.

::

    				      | Management   | Public
    				      |		     |
       	      			      |		     |
       	      			      |		     |
    +-------------------------+       |		     |
    | Controller1             |       |		     |
    |  neutron-server         +-------o--------------+
    | +--------------------+  |       |		     |
    | |Pacemaker           |  |       |		     |
    | |  neutron-...-agent |  +-------+		     |	      +-------------+
    | +--------------------+  |       |		     |	      | vCenter     |
    +-------------------------+       |		     +--------+             |
    	      		       	      |		     |	      |             |
    	      		       	      |		     |	      |             |
    	      		       	      |		     |	      +-------------+
    +-------------------------+       |		     |
    | Controller2             |       |		     |
    |  neutron-server         +-------o--------------+
    | +--------------------+  |       |		     |
    | |Pacemaker           |  |       |		     |
    | |  neutron-...-agent |  +-------+		     |
    | +--------------------+  |       |		     |
    +-------------------------+       |		     |
    	      		       	      |		     |
    	      		       	      |		     |
    +----------------------------+    |		     |
    |Compute1   	   	 |    |		     |
    |           	   	 +----+		     |
    |  neutron-openvswitch-agent |    |		     |
    +----------------------------+    |		     |
    			       	      |		     |
    			       	      |		     |
    +----------------------------+    |		     |
    |Compute2     	       	 |    |		     |
    |           	   	 +----+		     |
    |  neutron-openvswitch-agent |    |		     |
    +----------------------------+    |		     |
    				      |		     |
    				      |		     |

Assumptions:
------------

  #. DVS switches must be provisioned by using vCenter firstly and manually

  #. There must be a mapping between physical network and DVS switch:

    #. different physnet to different DVS switches (i.e. physnet1:dvswitch1,
       physnet2:dvswitch2)

    #. different physnet to the same DVS switch (i.e. physnet1:dvswitch1,
       physnet2:dvswitch1)

  3. VLANs will be used as a tenant network separation by KVM’s OVS and ESXi’s
     DVS (must be the same for tenant network regardless which switch type OVS
     or DVS)

  #. There must be an ability to:

    #. create / terminate network on DVS

    #. bind port on DVS to VM

    #. disable state of the neutron network / port on DVS

    #. assign multiple vNIC to a single VM deployed on ESXi

  5. Name of driver is vmware_dvs

Limitations:
------------

  #. Only VLANs are supported for tenant network separation (VxLAN support can
     be added later, if project will be continued).

  #. Only vSphere 5.5 is supported

Alternatives
------------

Use nova-network or other solution for Neutron and VMware.

Data model impact
-----------------

There are two changes will appears on the Settings tab:

  #. checkbox "Use vmware_dvs plugin for VMware networking".

  #. input field for specification dvSwitch's name for clusters.

REST API impact
---------------

None

Upgrade impact
--------------

This plugin has to have a special version for Fuel 7.0. For this reason after
the Fuel's upgrades plugin also should be upgraded.

Security impact
---------------

Neutron provides better isolation between tenantes. Using this plugin increases
security.

Notifications impact
--------------------

None

Other end user impact
---------------------

In the Fuel 6.1 if using vCenter was chosen on the wizard UI then possibilities
of using Neutron for networking are locked. Unfortunately current plugin's
architecture doesn't provide the way to pliable unlock it. Instead of it when
the plugin is installed it just amend the Nailgun's database and cancel this
lock. It will be never return again even the plugin will be remoted. So if user
installs and remotes the plugin after that he can deploy environment with
Neutron and VMware which will not work normally. User can care about that.

Performance Impact
------------------

None

Plugin impact
-------------

None

Other deployer impact
---------------------

With the vmware_dvs driver will be installed its dependencies(see in pip
syntax):

* pbr>=0.6,!=0.7,<1.0

* oslo.vmware>=0.6.0

* -e git://git.openstack.org/openstack/python-novaclient#egg=python-novaclient

* -e git+git://github.com/yunesj/suds#egg=suds

* oslo.log<=1.1.0

* oslo.messaging>=1.6.0, <=1.8.3

* oslo.config<=1.11.0

* oslo.i18n<2.0.0

Developer impact
----------------

None

Infrastructure impact
---------------------

None

Implementation
==============

Assignee(s)
-----------

:Primary assignee: Igor Gajsin <igajsin>

:QA: Olesia Tsvigun <otsvigun>

:Mandatory design review: Vladimir Kuklin <vkuklin>, Bogdan Dobrelia
                        <bogdando>, Sergii Golovatiuk <sgolovatiuk>,
                        Andrzej Skupień <kendriu>


Work Items
----------

* Create the development and testing environment. Make a repository on github
  and job for CI on jenkins.

* Add script for amend the nailgun database.

* Add puppet manifests for install the driver, upgrade the python library and
  patch a controller.

* Add puppet manifests for configure neutron to use vmware_dvs ML2 plugin.

* Add pacemaker/corosync scripts for additional neutron-server processes.

* Add ostf-tests. Manual and auto acceptance testing.


Dependencies
============

VMware_dvs Neutron ML2 plugin [1]

Testing
=======

The existent ostf tests for Neutron good enough however they doesn't have a
support for VMware. This lack should be eliminate by writing new tests special
for Neutron and VMware. After this new system tests for Jenkins will be
written. There is the list of cases for cheking:

#. Deploy testing:

  1. Install Fuel plugin for Neutron ML2 vmware_dvs driver.

  #. Uninstall Fuel plugin for Neutron ML2 vmware_dvs driver.

  #. Deploy in HA cluster with plugin.

  #. Deploy cluster with plugin and vmware datastore backend.

  #. Deploy cluster with plugin and Ceph backend for Glance and Cinder.

  #. Deploy cluster with plugin on Fuel 6.1 and upgrade to Fuel 7.0.

#. Functional testing:

  #. Check abilities to create and teminate networks on DVS.

  #. Check abilities to create and delete security groups.

  #. Check abilities to bind port on DVS to VM, disable and enable this port.

  #. Check abilities to assign multiple vNIC to a single VM.

  #. Check connection between VMs in one tenant.

  #. Check connectivity between VMs in one tenant which works in different
     availability zones: on KVM and on vCenter.

  #. Check connectivity between VMs attached to different networks with and
     within a router between them.

  #. Check isolation between VMs in different tenants.

  #. Check connectivity to public network.

#.  GUI testing.

#. Failover testing.

  #. Verify that vmclusters should be migrate after remove controler.

  #. Deploy cluster with plugin, addition and deletion of nodes.

Acceptance criterias:
---------------------

  #. Tests with high and medium priority are passed.

  #. Critical and high issues are fixed.

  #. Test Coverage of feature is about 90 %

Documentation Impact
====================

* Deployment Guide (how to prepare an environment for installation, how to
  install the plugin, how to deploy OpenStack an environment with the plugin).

* User Guide (which features the plugin provides, how to use them in the
  deployed OS environment).

* Test Plan.

* Test Report.

References
==========

* Neutron ML2 wiki page https://wiki.openstack.org/wiki/Neutron/ML2

* Repository of ML2 driver https://github.com/Mirantis/vmware-dvs
