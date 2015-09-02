*****************************************************
Guide to the VMware DVS plugin version 1.0.1 for Fuel
*****************************************************

.. raw:: pdf

   PageBreak


Document purpose
----------------

The purpose of this document is to describe how to install, configure
and use the VMware DVS plugin 1.0.1 for Fuel 6.1.

Key terms, acronyms and abbreviation
-------------------------------------

============================= ========================================================
**Term/acronym/abbreviation** **Definition**
============================= ========================================================
VM                            Virtual Machine
MOS                           Mirantis OpenStack
OVS                           Open vSwitch
Neutron ML2 plugin            The Neutron Modular Layer 2 plugin is a framework
                              allowing OpenStack Networking to simultaneously
........................      utilize the variety of layer 2 networking technologies
vmware_dvs driver             The driver in the Neutron ML2 plugin which provides
                              interaction with dvSwitch on vCenter
VMware DVS plugin             The plugin for Fuel which installs and configures
                              vmware_dvs driver on a MOS environment
dvSwitch                      distributed vSwitch on VMware ESXi
VMware ESXi                   bare-metal hypervisor
VMware vCenter Server         Central control point for VMware vSphere
VMware vSphere                VMware’s cloud computing virtualization operating
                              system.
============================= ========================================================

The VMware DVS plugin
---------------------

MOS supports using vCenter as a hypervisor in a vCenter-only or
heterogeneous, mixed with KVM environments. There is the vmware\_dvs
driver for Neutron ML2 plugin which provides usage Neutron for
networking in such environments. Thereby environments receives an
advanced network features:

-  Ability to create multi-tier networks (e.g., web tier, db tier, app
   tier).

-  Control over IP addressing.

-  Ability to insert an configure their own services (e.g., firewall,
   IPS)

-  VPN/Bridge to remote physical hosting or customer premises.

Licensing information
+++++++++++++++++++++

================= ============
**Component**     **License**
vmware_dvs driver Apache 2.0
VMware DVS plugin Apache 2.0
================= ============

Requirements
++++++++++++

The plugin has the following requirements for software:

================  ===========
**Requirement**   **Version**
 Fuel             6.1
 vCenter          5.5
================  ===========

Limitations
+++++++++++

-  VMware DVS plugin be enabled only in environments with Neutron as the
   networking option.

-  Only VLANs are supported for tenant network separation.

-  Only vSphere 5.5 is supported.


Installing the VMware DVS plugin
--------------------------------

Make sure that:
- you have the installed the
`Fuel Master node <https://docs.mirantis.com/openstack/fuel/fuel-6.1/user-guide.html>`__
- all the nodes of your future environment are discovered and functional.
- there is a connectivity to correctly configured vCenter with dvSwitch and clusters created. Please,
  see the
  `Mirantis OpenStack Planning Guide <https://docs.mirantis.com/openstack/fuel/fuel-6.1/planning-guide.html#vcenter-plan>`_,
  `User Guide <https://docs.mirantis.com/openstack/fuel/fuel-6.1/user-guide.html#vmware-integration-notes>`_ and
  `this plugin's specifcation <https://github.com/openstack/fuel-plugin-vmware-dvs/blob/master/specs/fuel-plugin-vmware-dvs.rst>__
  for information how to configure vCenter.

#. Download the plugin from the
   `Fuel Plugin Catalog <https://www.mirantis.com/products/openstack-drivers-and-plugins/fuel-plugins/>`__

#. Copy the plugin into Fuel Master node:
   ::

      $ scp fuel-plugin-vmware-dvs-1.0-1.0.1-1.noarch.rpm <Fuel Master node ip>:/tmp

#. Log into the Fuel Master node and install the plugin:
   ::

      $ ssh root@<Fuel Master node ip>
      [root@nailgun ~]# fuel plugins --install /
      /tmp/fuel-plugin-vmware-dvs-1.01.0.11.noarch.rpm
      [root@nailgun  ]# fuel plugins
      DEPRECATION WARNING: /etc/fuel/client/config.yaml exists and will
      be used as the source for settings. This behavior is deprecated.
      Please specify the path to your custom settings file in the
      FUELCLIENT_CUSTOM_SETTINGS environment variable.

      +------+--------------------------+-----------+--------------------+
      | id   | name                     | version   | package\_version   |
      +------+--------------------------+-----------+--------------------+
      | 2    | fuel-plugin-vmware-dvs   | 1.0.1     | 2.0.0              |
      +------+--------------------------+-----------+--------------------+

Removing the VMware DVS plugin
++++++++++++++++++++++++++++++

To uninstall VMware DVS plugin, follow these steps:

#. Delete all environments in which VMware DVS plugin has been enabled.

#. Uninstall the plugin:
   ::

      # fuel plugins --remove fuel-plugin-vmware-dvs--1.0.1

#. Check if the plugin was uninstalled successfully:
   ::

      +------+--------+-----------+--------------------+
      | id   | name   | version   | package_version    |
      +------+--------+-----------+--------------------+
      +------+--------+-----------+--------------------+

.. raw:: pdf

   PageBreak

Configuring VMware DVS plugin
-----------------------------

#. `Create a new OpenStack
   environment <https://docs.mirantis.com/openstack/fuel/fuel-6.1/user-guide.html#create-a-new-openstack-environment>`_
   with Fuel UI wizard.

   .. image:: pics/create.png

#. In *Compute* menu, select *vCenter* checkbox:

   .. image:: pics/compute.png

#. Select *Neutron with VLAN segmentation* for *Networking Setup* - it is
   the only networking configuration supported with VMware DVS plugin:

   .. image:: pics/net.png

#. Finish environment creation following
   `documentation <https://docs.mirantis.com/openstack/fuel/fuel-6.1/user-guide.html#create-a-new-openstack-environment>`_.

#. `Add
   <https://docs.mirantis.com/openstack/fuel/fuel-6.1/user-guide.html#configure-your-environment>`__
   at least 1 Controller and 1 Compute node to the environment.

#. Open the *Settings* tab of the Fuel Web UI and scroll down the page. Select the
   *use Neutron VMware DVS ML2 plugin* checkbox and specify correct name of dvSwitch:

   .. image:: pics/settings.png

#. Fill in the VMware configuration fields on the *VMware* tab:

   .. image:: pics/vmware.png

#. The rest of configuration is up to you.
   See `Mirantis OpenStack User Guide <https://docs.mirantis.com/openstack/fuel/fuel-6.1/user-guide.html>`__
   for instructions.

#. Click *Deploy changes* button to finish.

.. raw:: pdf

   PageBreak

User Guide
----------

#. Once OpenStack has been deployed, we can start using Neutron for
   networking. The net04 port group should appear on the vCenter:

   .. image:: pics/net04pg.png

#. In Horizon, the network topology should look like:

   .. image:: pics/topology.png

   where VMware is the name of the instance located on the vCenter.

#. You can use Neutron for such instance brand the same way as for KVM-located instances.
