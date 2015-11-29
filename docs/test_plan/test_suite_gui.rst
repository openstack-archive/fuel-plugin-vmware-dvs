GUI
===


Verify that all elements of DVS plugin section meets the requirements.
----------------------------------------------------------------------


ID
##

dvs_gui


Description
###########

Verify that all elements of DVS plugin section meets the requirements.


Complexity
##########

smoke


Steps
#####

    1. Connect to a Fuel web UI with preinstalled plugin.
    2. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    3. Click on the Settings tab and check that section of  DVS  plugin is displayed with all required GUI elements.
    4. Verify that section of DVS plugin is present on the Settings tab.
    5. Verify that check box "Use Neutron VMware DVS ML2 plugin" is enabled by default.
    6. Verify that user can disabled -> enabled DVS plugin by click on check box "Use Neutron VMware DVS ML2 plugin".
    7. Verify that  check box "Use VMware DVS ML2 plugin for networking" is enabled by default.
    8. Verify that all labels of DVS plugin section have same font style and color.
    9. Verify that all elements of DVS plugin section are  vertical aligned.


Expected result
###############

All elements of DVS plugin section meets the requirements.
