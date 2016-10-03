Install VMware DVS plugin
-------------------------

Before you proceed with the VMware DVS plugin installation, verify that:

#. You have completed the :ref:`prereqs` steps.

#. All the nodes of your future environment are :guilabel:`DISCOVERED` on the
   Fuel Master node.

#. You have connectivity to correctly configured vCenter with VDSes and
   clusters created.

**To install the VMware DVS plugin:**

#. Download the VMware DVS plugin from the
   `Fuel Plugin Catalog <https://www.mirantis.com/products/openstack-drivers-and-plugins/fuel-plugins/>`__.

#. Copy the plugin ``.rpm`` package to the Fuel Master node:

   .. code-block:: console

     $ scp fuel-plugin-vmware-dvs-3.1-3.1.0-1.noarch.rpm <Fuel Master node ip>:/tmp

#. Log in to the Fuel Master node CLI as root.

#. Install the plugin:

   .. code-block:: console

     # fuel plugins --install /tmp/fuel-plugin-vmware-dvs-3.1-3.1.0-1.noarch.rpm

#. Verify that the plugin was installed successfully:

   .. code-block:: console

     # fuel plugins

     +------+--------------------------+-----------+--------------------+
     | id   | name                     | version   | package\_version   |
     +------+--------------------------+-----------+--------------------+
     | 2    | fuel-plugin-vmware-dvs   | 3.1.0     | 4.0.0              |
     +------+--------------------------+-----------+--------------------+

#. Proceed to :ref:`configure_env`.

.. raw:: latex

   \pagebreak
