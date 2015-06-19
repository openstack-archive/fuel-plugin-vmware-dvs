=============================================
Fuel plugin for Neutron ML2 vmware_dvs driver
=============================================

https://mirantis.jira.com/browse/PROD-617

There is the Fuel plugin which provides Neutron for networking on
VMware-related MOS environments.

Problem description
===================

Modern facilities to networking in OpenStack is Neutron which replaces obsolete
nova-networks. Unfortunately integration with VMware which realized in Fuel 6.1
and below doesn't provide the possibilites to using Neutron. It leads that an
environment which uses VMware hypervisors is greatly limited. When customers
(especially huge customers) want to replicate rich enterprise network
topologies:

* Ability to create multi-tier networks (e.g., web tier, db tier, app tier).

* Control over IP addressing.

* Ability to insert an configure their own services (e.g., firwall, IPS)

* VPN/Bridge to remote physical hosting or customer premises.

Nova-networks can offer:

* No way to control topology.

* Cloud assigns IP prefixes and addresses.

* No generic service insertion.

Such we have the contradiction between customer needs and our solution.

Proposed change
===============

The Neutron has plugable architecture which provides using different backends
(so-called ML2 plugins) in different cases. There is the vmware-dvs [0] plugin
which provides using Neutron for networking in vmware-related environments. And
it is exactly what we want.

Accordingly the plugin architecture on controller have to launched additional
neutron-server process for each vCenter on their control.

::

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

We assume that:

* the VMware environment is already configured by the customer
  (the Cluster and the dvSwitch assigned to Cluster).

* there is only a possibility to deploy one dvSwitch per one VMware vCenter
  Cluster.

* only VLAN segmentation and only vSphere 5.5 are supported.

Alternatives
------------

Use nova-network or other solution for Neutron and VMware.

Data model impact
-----------------

There is the new checkbox "Use vmware_dvs plugin for VMware networking" will
reveal on the Settings tab and near each cluster shoud be append an input field
for setting a dvSwitch's name.

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
lock. It will be never return again even the plugin will remoted. So if user
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

There are some changes should be done on controller for providing security
groups:

* upgrade the python suds library

* apply special patch to nova/virt/vmwareapi/vif.py and vm_util.py

* upgrade the oslo-messaging in version >= 1.6.0

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

* Create the development and testing environment.

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
written. Base idea is new tests have to check same that for nova-network but
for Neutron.

Documentation Impact
====================

* Deployment Guide (how to prepare an env for installation, how to install the
  plugin, how to deploy OpenStack env with the plugin).

* User Guide (which features the plugin provides, how to use them in the
  deployed OS env).

* Test Plan.

* Test Report.


References
==========

* Repo of ML2 plugin https://github.com/Mirantis/vmware-dvs
