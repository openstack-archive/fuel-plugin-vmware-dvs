==============================================================
Load/Performance Test Plan for VMware DVS plugin version 3.0.1
==============================================================

************
Introduction
************

Objective of performance testing
================================

* To verify that the VMware DVS plugin meet their expected SLA's while
# TODO



Purpose
=======

The main purpose of this document is to describe Quality Assurance activities
required to ensure that the Fuel plugin for Neutron ML2 vmware_dvs driver
works correctly under loading and is ready for production. The project will be
able to offer VMware DVS integration functionality with MOS.

The scope of this plan defines the following objectives:

* Identify testing activities;
* Outline testing approach, test types, test cycle that will be used;
* List of metrics and deliverable elements;
* List of items for testing and out of testing scope;
* Detect exit criteria in testing purposes;
* Describe test environment.

Scope
=====

The Fuel VMware DVS plugin includes Neutron ML2 Driver For VMware vCenter DVS
which is developed by third party. This test plan covers the performance testing
of Fuel VMware DVS plugin.

The following test types should be provided:

* Shaker tests
* Rally tests

Performance testing will be executed on the scale lab and a custom set of rally
scenarios must be run with the DVS environment. The configuration, environment,
and scenarios for load/performance testing is determined in current document.

Intended Audience
=================

This document is intended for project team staff (QA and Dev engineers and
managers) and all other persons who are interested in testing results.

Limitation
==========

The plugin (or its components) has the following limitations:

* VMware DVS plugin can be enabled only in environments with Neutron as a networking option
* Only VLANs are supported for tenant network separation.
* Only vSphere 5.5 & 6.0 are supported.

Product compatibility matrix
============================

.. list-table:: product compatibility matrix
   :widths: 15 10 30
   :header-rows: 1

   * - Requirement
     - Version
     - Comment
   * - MOS
     - 9.0 with Mitaka
     -
   * - Operating System
     - Ubuntu 14.04
     -
   * - vSphere
     - 5.5, 6.0
     -

Test environment and infrastructure
===================================

Environment configuration
-------------------------

+----------------------------+----------------------------------+
| Mirantis Fuel ISO          | 9.0                              |
+----------------------------+----------------------------------+
| Mirantis Openstack release | Mitaka on Ubuntu 14.04           |
+----------------------------+----------------------------------+
| vSphere                    | 5.5                              |
+----------------------------+----------------------------------+
| VMware DVS plugin          | 3.0.1                            |
+----------------------------+----------------------------------+
| Network                    | Neutron with Vlan Segmentation   |
+----------------------------+----------------------------------+
|                            | Cinder LVM over iSCSI for volumes|
| Storage Backends           +----------------------------------+
|                            | VMware vCenter/ESXi datastore    |
|                            | for images (Glance)              |
+----------------------------+----------------------------------+
| Hypervisor types           | KVM, vCenter                     |
+----------------------------+----------------------------------+

Hardware configuration
----------------------

+-----------------------------------------------------------------------+
|                           Fuel Environment                            |
+===============+============+========+================+================+
|Amount of nodes| Controller + Cinder |Compute + Cinder|Compute-vmware +|
|               | VMware              |                |Cinder-vmware   |
+---------------+---------------------+----------------+----------------+
|      8        |    3                |         2      |     3          |
+---------------+---------------------+----------------+----------------+
| System        | Supermicro X9SRD-F                                    |
+---------------+-------------------------------------------------------+
| CPU           | 12 × 2.10 GHz                                         |
+---------------+-------------------------------------------------------+
| RAM           | 2 x 16.0Gb, 1.6 GHz DDR3 (32GB)                       |
+---------------+-------------------------------------------------------+
| SSD           |80GB                                                   |
+---------------+-------------------------------------------------------+
| HDD           |1TB                                                    |
+---------------+-------------------------------------------------------+
| Network       | 2 × 10GB/s, 2 × 1GB/s                                 |
+---------------+-------------------------------------------------------+

+-----------------------------------------------------------------------+
|                      vCenter Environment                              |
+===============+================+========+================+============+
|Amount of nodes| vCenter Server |Clusters|ESXi per cluster|Storage NFS |
+---------------+----------------+--------+----------------+------------+
|      37       |    1           |    4   |     8          |     5      |
+---------------+----------------+--------+----------------+------------+
| CPU           | 1 Xeon × 2.10 GHz, 12 LCPU                            |
+---------------+-------------------------------------------------------+
| RAM           | 32GB                                                  |
+---------------+-------------------------------------------------------+
| SSD           |80GB                                                   |
+---------------+-------------------------------------------------------+
| HDD           |1TB                                                    |
+---------------+-------------------------------------------------------+
| Network       | 2 × 10GB/s, 2 × 1GB/s                                 |
+---------------+-------------------------------------------------------+
|vCenter Appliance (ESXi based) on hdd datastore                        |
+---------------+-------------------------------------------------------+

**************************************
Evaluation Mission and Test Motivation
**************************************

The main goal of the project is to build a MOS plugin that integrates
the Neutron ML2 Driver For VMware vCenter DVS. This will allow to use Neutron
for networking in VMware-related environments. The plugin must be compatible
with the version 9.0 of Mirantis OpenStack and should be tested with the
software/hardware described in `product compatibility matrix`_.

See the VMware DVS Plugin specification for more details.

Evaluation mission
==================

* Find pressing issues with performance of Neutron ML2 driver for DVS.
* Verify the specification.
* Lab environment deployment.
* Deploy MOS with the developed plugin installed.
* Create and run specific tests for plugin/deployment.
* Verify the documentation.

*****************
Target Test Items
*****************


*************
Test approach
*************


**Shaker testing**

The goal of shaker testing is to ensure that #TODO

**Rally testing**

The goal of rally testing is to ensure #TODO


***********************
Entry and exit criteria
***********************

Criteria for test process starting
==================================

Before test process can be started it is needed to make some preparation
actions - to execute important preconditions. The following steps must be
executed successfully for starting test phase:

* all project requirements are reviewed and confirmed;
* implementation code is stored in GIT;
* test environment is prepared with correct configuration, installed all needed software, hardware;
* test environment contains the latest delivered build for testing;
* test plan is ready and confirmed internally;
* all features have been successfully tested;

Feature exit criteria
=====================

Testing of a feature can be finished when:

All planned tests are executed;
 * no defects are found during this run;
 * found defects during this run are verified or confirmed to be acceptable (known issues);

Suspension and resumption criteria
==================================

Performance esting is suspended if there is a blocking issue
which prevents tests execution. Blocking issue can be one of the following:

* Testing environment is not ready
* Testing environment is unavailable due to failure
* There is a blocking defect, which prevents further usage of
  the vmware DVS plugin or its feature and there is no workaround available

************
Deliverables
************

List of deliverables
====================

Project testing activities are to be resulted in the following reporting documents:

* Test plan
* Test report
* Automated test cases


**********
Test cases
**********

.. include:: test_suite_shaker.rst