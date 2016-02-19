Removing the VMware DVS plugin
------------------------------

To uninstall VMware DVS plugin, follow these steps:

#. Delete all environments in which VMware DVS plugin has been enabled.

#. Uninstall the plugin:
   ::

      # fuel plugins --remove fuel-plugin-vmware-dvs==2.1.0

#. Check if the plugin was uninstalled successfully:
   ::

      +------+--------+-----------+--------------------+
      | id   | name   | version   | package_version    |
      +------+--------+-----------+--------------------+
      +------+--------+-----------+--------------------+
