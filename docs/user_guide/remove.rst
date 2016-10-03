Uninstall VMware DVS plugin
---------------------------

To uninstall VMware DVS plugin, follow the steps below:

#. Log in to the Fuel Master node CLI.

#. Delete all the environments in which VMware DVS plugin is enabled:

   .. code-block:: console

    # fuel --env <ENV_ID> env delete

#. Uninstall the plugin:

   .. code-block:: console

     # fuel plugins --remove fuel-plugin-vmware-dvs==3.1.0

#. Verify whether the VMware DVS plugin was uninstalled successfully:

   .. code-block:: console

     # fuel plugins

   The VMware DVS plugin should not appear in the output list.

.. raw:: latex

   \pagebreak
