Removing the VMware DVS plugin
------------------------------

To uninstall VMware DVS plugin, follow these steps:

#. Delete all environments in which VMware DVS plugin has been enabled.

#. Uninstall the plugin:
   ::

      # fuel plugins --remove fuel-plugin-vmware-dvs--1.1.0

#. Check if the plugin was uninstalled successfully:
   ::

      +------+--------+-----------+--------------------+
      | id   | name   | version   | package_version    |
      +------+--------+-----------+--------------------+
      +------+--------+-----------+--------------------+

There is one issue with wizard on the Fuel WEB UI. Please be informed that
after removing this plugin the option "Neutron with VLAN segmentation" stays
unlocked when the 'vCenter' checkbox is selected. Therefore there is a
possibilities for deployment environment with vCenter as a hypervisor, Neutron
for networking and without the VMware DVS plugin. If no other plugin provides
this functionality such environment will be misconfigured.
