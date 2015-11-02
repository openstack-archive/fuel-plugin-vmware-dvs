GUI
===

Verify that all elements of DVS plugin section require GUI regiments.
---------------------------------------------------------------------

**ID**

dvs_gui

**Description**
::

 Verify that all elements of DVS plugin section require GUI regiments.

**Complexity**

smoke

**Requre to automate**

Yes

**Steps**
::

 Copy plugin to to the Fuel master node using scp.
 Install plugin
 fuel plugins --install plugin-name-1.1-1.1.0-1.noarch.rpm
 Ensure that plugin is installed successfully using cli, run command 'fuel plugins'.
 Connect to the Fuel web UI.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and Qemu radio button
  network setup : Neutron with Vlan segmentation
  storage backends: default
 additional services: all by default
 Click on the Settings tab and check that section of  DVS  plugin is displayed with all required GUI elements.
 Verify that section of DVS plugin is present on the Settings tab.
 Verify that check box ‘Use Neutron VMware DVS ML2 plugin’ is enabled by default.
 Verify that user can disabled -> enabled DVS plugin by click on check box ‘Use Neutron VMware DVS ML2 plugin’.
 Verify that  check box ‘Use VMware DVS ML2 plugin for networking’ is enabled by default.
 Verify that all labels of DVS plugin section have same font style and color.
 Verify that all elements of DVS plugin section are  vertical aligned.All elements of DVS plugin section should be  required GUI regiments.

