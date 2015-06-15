==========================================
Fuel plugin for Neutron ML2 vmware_dvs driver
==========================================

There is Fuel plugin which provides an advanced networking for VMware-related
MOS environments.

Problem description
===================

Fuel 6.1 doesn't provide neutron networking for VMware-related environments
only nova-network. Nova-network has a lot of limitations and can not be used in
production. Modern solution for networking is Neutron but vanilla Fuel 6.1 can
not uses it.

This project has aim teach the Neutron to works with the VMware.

Proposed change
===============

The Neutron has special method to use different backends in different cases.
It is ML2 plugins. One of them is vmware_dvs which provides Neutron to manage
VMware Distributed Virtual Switches. And it is exactly what we want.

Alternatives
------------

Use nova-network or other solution for Neutron and VMware.

Data model impact
-----------------

None

REST API impact
---------------

None

Upgrade impact
--------------

None

Security impact
---------------

None

Notifications impact
--------------------

None

Other end user impact
---------------------

Except limitations of nova-network.

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
