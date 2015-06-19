==========================================
Fuel plugin for Neutron ML2 vmware_dvs driver
==========================================

https://mirantis.jira.com/browse/PROD-617

There is Fuel plugin which provides Neutron for networking on VMware-related
MOS environments.

Problem description
===================

Modern facilities to networking in OpenStack is Neutron which replaces obsolete
nova-networks. Unfortunately integration with VMware which realized in Fuel 6.1
and below doesn't provide the possibilites to using Neutron. It leads that
environments which uses VMware hypervisors greatly limited. When customers
(especially huge customers) want to replicate rich enterprise network
topologies:

* Ability to crate multi-tier networks (e.g., web tier, db tier, app tier).

* Control over IP addressing.

* Ability to insert an configure their own services (e.g., firwall, IPS)

* VPN/Bridge to remote physical hosting or customer premises.

Nova-networks can offer:

* No way to control topology.

* Cloud assigns IP prefixes and addresses.

* No generic service insertion.

Such we have contradiction between customer needs and our solution.

Proposed change
===============

The Neutron has plugable architecture which provides using different backends
(so-called ML2 plugins) in different cases. There is the vmware-dvs [0] plugin
which provides using Neutron for networking in vmware-related environments. And
it is exactly what we want.

Accordingly the plugin architecture on contrller have to launched additional
neutron-server process for each vCenter on ther control.

+-------------------------------------------+                       +--------+
|Controller1                                |                       |        |
|                                           |                       |vCenter1|
| +---------------------------------------+ |                       |        |
| |Pacemaker                              | |                       |        |
| |                                       | |                       |        |
| | neutron+server --config-file vC1.ini +--------+-----------------+        |
| |                                       | |     |                 |        |
| |                                       | |     |                 |        |
| | neutron+server --config-file vC2.ini +---------------+          |        |
| |                                       | |     |      |          |        |
| +---------------------------------------+ |     |      |          +--------+
|                                           |     |      |
+-------------------------------------------+     |      |
                                                  |      |
+-------------------------------------------+     |      |          +--------+
|Controller2                                |     |      |          |        |
|                                           |     |      |          |vCenter2|
| +---------------------------------------+ |     |      |          |        |
| |Pacemaker                              | |     |      |          |        |
| |                                       | |     |      +----------+        |
| | neutron+server --config-file vC1.ini +--------+      |          |        |
| |                                       | |            |          |        |
| |                                       | |            |          |        |
| | neutron+server --config-file vC2.ini +---------------+          |        |
| |                                       | |                       |        |
| +---------------------------------------+ |                       +--------+
|                                           |
+-------------------------------------------+

We assume that the VMware environment is already configured by the customer
(the Cluster and the dvSwitch assigned to Cluster) - there is only a
possibility to deploy one dvSwitch per one VMware vCenter Cluster.

Alternatives
------------

Use nova-network or other solution for Neutron and VMware.

Data model impact
-----------------

There is new checkbox "Use vmware_dvs plugin for VMware networking" will reveal
on the Settings tab.

REST API impact
---------------

None

Upgrade impact
--------------

This plugin have to special version for Fuel 7.0. For this reason after
upgrades Fuel the plugin also should be upgraded.

Security impact
---------------

Neutron provides better isolation between tenantes. Using this plugin increases
security.

Notifications impact
--------------------

None

Other end user impact
---------------------



Performance Impact
------------------

None

Plugin impact
-------------

None

Other deployer impact
---------------------

None

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

Who is leading the writing of the code? Or is this a blueprint where you're
throwing it out there to see who picks it up?

If more than one person is working on the implementation, please designate the
primary author and contact.

Primary assignee:
  igajsin

QA team:
  tsvigun

Work Items
----------

None


Dependencies
============

VMware_dvs Neutron ML2 plugin [1]


Testing
=======

None

Documentation Impact
====================

None


References
==========

* Repo of ML2 plugin https://github.com/Mirantis/vmware-dvs
