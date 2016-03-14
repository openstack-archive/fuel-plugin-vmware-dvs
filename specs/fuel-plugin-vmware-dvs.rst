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
networks on vSphere. Vmware_dvs provides the mechanism driver and the
neutron-dvs-agent that uses special vSphere API for direct manipulation virtual
distributed switches: creates or deletes port-groups, ports and changes
security rules on that ports.

In that way no unnecessary traffic redirections and the given scheme admits to
achieve best performance. Also using modular ML2 architecture provides to
usage several network backends simultaneously and hence creating heterogeneous
OpenStack environments. And it is exactly what we want.

This plugin automates installation and configuration the vmware_dvs driver and
its dependencies (it carries all of them with it to be independent from public
network). After driver installation it changes configuration files
/etc/neutron/neutron.conf, /etc/neutron/plugin.ini and
/etc/neutron/plugins/ml2/vmware_dvs-$vcenters_az-$service_name.ini whereby
neutron-server can manage networking on vCenter.

::

                                       | Management  | Public
                                       |             |
                                       |             |
                                       |             |
    +-------------------------+        |             |
    | Controller1             |        |             |
    |  neutron-server         +--------o-------------+       +---------------+
    | +--------------------+  |        |             |       |vSphere        |
    | |Pacemaker           |  |        |             |       |               |
    | |  neutron-dvs-agent |  +--------+             |       | +----------+  |
    | +--------------------+  |        |             |       | | Cluster1 |  |
    +-------------------------+        |             |       | |          |  |
                                       |             |       |++--+       |  |
                                       |             +--------+VDS|       |  |
                                       |             |       |++--+       |  |
    +-------------------------+        |             |       | +----------+  |
    | Controller2             |        |             |       |               |
    |  neutron-server         +--------o-------------+       |               |
    | +--------------------+  |        |             |       | +----------+  |
    | |Pacemaker           |  |        |             |       | | Cluster2 |  |
    | |  neutron-dvs-agent |  +--------+             |       | |          |  |
    | +--------------------+  |        |             |       |++---+      |  |
    +-------------------------+        |             +--------+VDS2|      |  |
                                       |             |       |++---+      |  |
                                       |             |       | +----------+  |
    +----------------------------+     |             |       +---------------+
    |Compute                     |     |             |
    |                            +-----+             |
    |  neutron-openvswitch-agent |     |             |
    +----------------------------+     |             |
                                       |             |
                                       |             |
    +----------------------------+     |             |
    |Compute-vmware              |     |             |
    |                            +-----o-------------+
    |  neutron-dvs-agent       	 |     |             |
    +----------------------------+     |             |
                                       |             |
                                       |             |
 				       |	     |
Assumptions:
------------

  #. All VDS'es must be provisioned by using vCenter firstly and manually.

  #. There must be a mapping between physical network and VDS'es:

  3. VLANs will be used as a tenant network separation by KVM’s OVS and ESXi’s
     VDS (must be the same for tenant network regardless which switch type OVS
     or VDS)

  #. Each vSphere's Cluster has its own VDS.

  #. There must be an ability to:

    #. create / terminate network on VDS

    #. bind port on VDS to VM

    #. disable state of the neutron network / port on VDS

    #. assign multiple vNIC to a single VM deployed on ESXi

    #. add VM to security groups

  5. Name of driver is vmware_dvs

Limitations:
------------

  #. Only VLANs are supported for tenant network separation.

  #. Only vSphere 5.5 or 6.0 is supported

Alternatives
------------

Use other solution for Neutron and VMware.

Data model impact
-----------------

There are serveral changes will appears on the other subtab of Networks tab:

  #. checkbox "Neutron VMware DVS ML2 plugin".

  #. radiobutton with plugin's version

  #. checkbox "Use the VMware DVS firewall driver"

  #. input field for specification the cluster to VDS mapping.

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

* Rewrite puppet manifests, deployment scripts, init and corosync scripts and
  for working with agents on controller and compute-vmware nodes.

* Make new tests and build CI.

* Rewrite the documentation.

Dependencies
============

VMware_dvs Neutron ML2 plugin [1]

Testing
=======

Target Test Items:
------------------

* Install/uninstall Fuel Vmware-DVS plugin
* Deploy Cluster with Fuel Vmware-DVS plugin by Fuel
    * Roles of nodes
        * controller
        * compute
        * cinder
        * mongo
        * compute-vmware
        * cinder-vmware
    * Hypervisors:
        * KVM+Vcenter
        * Qemu+Vcenter
    * Storage:
        * Ceph
        * Cinder
        * VMWare vCenter/ESXi datastore for images
    * Network
        * Neutron with Vlan segmentation
        * HA + Neutron with VLAN
    * Additional components
        * Ceilometer
        * Health Check
    * Upgrade master node
* MOS and VMware-DVS plugin
    * Computes(Nova)
        * Launch and manage instances
        * Launch instances in batch
    * Networks (Neutron)
        * Create and manage public and private networks.
        * Create and manage routers.
        * Port binding / disabling
        * Port security
        * Security groups
        * Assign vNIC to a VM
        * Connection between instances
    * Heat
        * Create stack from template
        * Delete stack
    * Keystone
        * Create and manage roles
    * Horizon
        * Create and manage projects
        * Create and manage users
    * Glance
        * Create  and manage images
* GUI
    * Fuel UI
* CLI
    * Fuel CLI

Test approach:
--------------

The project test approach consists of Smoke,  Integration, System, Regression
Failover and Acceptance  test levels.

Acceptance criterias:
---------------------

  #. All acceptance criteria for user stories are met.
  #. All test cases are executed. BVT tests are passed.
  #. Critical and high issues are fixed.
  #. All required documents are delivered.
  #. Release notes including a report on the known errors of that release.

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

* The blueprint for component registry
  https://blueprints.launchpad.net/fuel/+spec/component-registry
