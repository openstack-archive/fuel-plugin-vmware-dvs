.. _prereqs:

Prerequisites
-------------

Before you install and start using the VMware DVS plugin on Fuel, complete the
following steps:

#. Install and set up
   `Fuel 9.1 <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-install-guide.html>`__.

#. Plan the vSphere integration. For details, see
   `Mirantis OpenStack Planning Guide <https://docs.mirantis.com/openstack/fuel/fuel-9.0/mos-planning-guide.html#plan-the-vsphere-integration>`_.

   .. seealso::
    * `VMware vSphere 5.5 official documentation <http://pubs.vmware.com/vsphere-55/index.jsp>`_
    * `VMware vSphere in OpenStack Configuration Reference <http://docs.openstack.org/mitaka/config-reference/compute/hypervisor-vmware.html>`_

#. Create a `vCenter service account <http://pubs.vmware.com/vsphere-55/index.jsp?topic=%2Fcom.vmware.vsphere.vcenterhost.doc%2FGUID-3B5AF2B1-C534-4426-B97A-D14019A8010F.html>`_.

#. In the vCenter service account, apply the following minimum privileges
   for :guilabel:`Distributed switch` and :guilabel:`dvPort group`:

   .. list-table::
      :header-rows: 1

      * - Permission
        - Privilege
      * - dvSwitch
        - * Port configuration operation
      * - dvPort Group
        - * dvPort group.Create
          * dvPort group.Delete
          * dvPort group.Modify
          * dvPort group.Policy operation

   This allows the VMware DVS plugin to use manipulation resources of VMware
   vSphere Distributed Switch (VDS).

#. Create and properly configure VDSes on vCenter that will be used for
   your environment. For details, see the VDS videos in the
   :menuselection:`Technical Details -> Resources` section on the
   `VMware Distributed Switch <https://www.vmware.com/products/vsphere/features/distributed-switch>`__
   page.

#. Connect the VMware DVS plugin to the pre-created and configured VDSes.

   .. note::
    The VMware DVS plugin does not create new VDSes but uses the existing ones.

.. raw:: latex

   \pagebreak
