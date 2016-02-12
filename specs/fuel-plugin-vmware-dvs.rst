=============================================
Fuel plugin for Neutron ML2 vmware_dvs driver
=============================================

There is the Fuel plugin which provides Neutron for networking on
VMware-related MOS environments.

Problem description
===================

There are several solutions which provide networking for OpenStack with
vSphere. Part of them are or were integrated in the Fuel: nova-network and
VMware NSXv plugin. Other part --- networking-vsphere -- is the separate
upstream project.

Unfortunately each of them has defects. Nova-network is the obsolete network
solution which provides really restricted possibilities. When customers
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

This contradiction doesn't allow to use nova-network in big enterprise.

VMware NSXv and networking-vsphere don't have such restrictions. Both of this
solutions are based on the same idea: to create on ESXi's hosts special control
VMs and redirect all tenant traffic to them. That approach permits to using all
possibilities of Neutron but multiple traffic redirection dramatically affects
to network performance. Also NSXv can be used in VMware-only environments.

Proposed change
===============

The Neutron has pluggable architecture which provides using different backends
in different cases simultaneously by using ML2 plugin [0]. There is the
vmware_dvs driver [1] which provides using Neutron for networking in
vmware-related environments. This driver realizes different way to manage
networks on vSphere. Vmware_dvs provides the mechanism driver which uses
special vSphere API for direct manipulation virtual distributed switches:
creates or deletes port-groups, ports and changes security rules on that ports.
In that way no unnecessary traffic redirections and the given scheme admits to
achieve best performance. Also using modular ML2 architecture provides to
usage several network backends simultaneously and hence creating heterogeneous
OpenStack environments. And it is exactly what we want.

This plugin automates installation and configuration the vmware_dvs driver and
its dependencies (it carries all of them with it to be independent from public
network). After driver installation it changes configuration files
/etc/neutron/neutron.conf and /etc/neutron/plugin.ini whereby neutron-server
can manage networking on vCenter.

::

                                              | Management   | Public
                                              |              |
                                              |              |
                                              |              |
    +-------------------------+               |              |
    | Controller1             |               |              |
    |  neutron-server         +---------------o--------------+
    | +--------------------+  |               |              |
    | |Pacemaker           |  |               |              |
    | |  neutron-...-agent |  +---------------+              |        +-------------+
    | +--------------------+  |               |              |        | vCenter     |
    +-------------------------+               |              +--------+             |
                                              |              |        |             |
                                              |              |        |             |
                                              |              |        +-------------+
    +-------------------------+               |              |
    | Controller2             |               |              |
    |  neutron-server         +---------------o--------------+
    | +--------------------+  |               |              |
    | |Pacemaker           |  |               |              |
    | |  neutron-...-agent |  +---------------+              |
    | +--------------------+  |               |              |
    +-------------------------+               |              |
                                              |              |
                                              |              |
    +----------------------------+            |              |
    |Compute1                    |            |              |
    |                            +------------+              |
    |  neutron-openvswitch-agent |            |              |
    +----------------------------+            |              |
                                              |              |
                                              |              |
    +----------------------------+            |              |
    |Compute2                    |            |              |
    |                            +------------+              |
    |  neutron-openvswitch-agent |            |              |
    +----------------------------+            |              |
                                              |              |
                                              |              |

Assumptions:
------------

  #. The VDS must be provisioned by using vCenter firstly and manually.

  #. There must be a mapping between physical network and VDS:

  3. VLANs will be used as a tenant network separation by KVM’s OVS and ESXi’s
     VDS (must be the same for tenant network regardless which switch type OVS
     or VDS)

  #. There must be an ability to:

    #. create / terminate network on VDS

    #. bind port on VDS to VM

    #. disable state of the neutron network / port on VDS

    #. assign multiple vNIC to a single VM deployed on ESXi

  5. Name of driver is vmware_dvs

Limitations:
------------

  #. Only VLANs are supported for tenant network separation.

  #. Only vSphere 5.5 or 6.0 is supported

Alternatives
------------

Use nova-network or other solution for Neutron and VMware.

Data model impact
-----------------

There are two changes will appears on the Settings tab:

  #. checkbox "Neutron VMware DVS ML2 plugin".

  #. input field for specification VDS's name for clusters.

REST API impact
---------------

None

Upgrade impact
--------------

This plugin has to have a special version for an each Fuel's version. For this
reason after the Fuel's upgrades plugin also should be upgraded.

Security impact
---------------

Neutron provides better isolation between tenants. Using this plugin increases
security.

Notifications impact
--------------------

None

Other end user impact
---------------------

After the VMware DVS plugin is installed there is the new checkbox "Neutron 
with VMware DVS" on the "Networking Setup" step of wizard. UI elements of the 
plugin are stored on subtab "Other" of tab "Networks" on the Fuel WebUI.

Performance Impact
------------------

None

Plugin impact
-------------

None

Other deployer impact
---------------------

With the vmware_dvs driver will be installed its dependencies:

* python-suds 0.4.1

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
                        <bogdando>, Sergii Golovatiuk <sgolovatiuk>


Work Items
----------

* Add changes to 7.0 version of the plugin according to component registry.
  
* Rewrite puppet manifests and deployment scripts for Fuel 8.0.

* Make new tests and build CI.

* Rewrite the documentation.  

Dependencies
============

VMware_dvs Neutron ML2 plugin [1]

Testing
=======

There is the list of cases for checking:

#. Deploy testing:

  1. Install Fuel plugin for Neutron ML2 vmware_dvs driver.

  #. Uninstall Fuel plugin for Neutron ML2 vmware_dvs driver.

  #. Deploy an environment with plugin where all VMware clusters are assigned
     to controllers.

  #. Deploy an environment with plugin where some VMware clusters are
     assigned to controllers and some --- to compute-vmware nodes

  #. Deploy an environment with plugin and vmware datastore backend.

  #. Deploy an environment with plugin and Ceph backend for Glance and Cinder.

  #. Deploy an environment with plugin on Fuel 7.0 and upgrade to Fuel 8.0.

#. Functional testing:

  #. Check abilities to create and terminate networks on VDS.

  #. Check abilities to create and delete security groups.

  #. Check abilities to bind port on VDS to VM, disable and enable this port.

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

  #. Verify that an environment survives after remove controller.

  #. Deploy an environment with plugin, addition and deletion of nodes.

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
