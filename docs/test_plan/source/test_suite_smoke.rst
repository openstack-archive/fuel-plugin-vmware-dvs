Smoke
=====


Install Fuel VMware DVS plugin.
-------------------------------


ID
##

dvs_install


Description
###########

Check that plugin can be installed.


Complexity
##########

smoke


Steps
#####

    1. Connect to fuel node via ssh.
    2. Upload plugin.
    3. Install plugin.


Expected result
###############

Ensure that plugin is installed successfully using cli, run command 'fuel plugins'. Check name, version and package version of plugin.


Uninstall Fuel VMware DVS plugin.
---------------------------------


ID
##

dvs_uninstall


Description
###########

Check that plugin can be removed.


Complexity
##########

smoke


Steps
#####

    1. Connect to fuel node with preinstalled plugin via ssh.
    2. Remove plugin.


Expected result
###############

Verify that plugin is removed, run command 'fuel plugins'.


Deploy cluster with plugin and controller.
------------------------------------------


ID
##

dvs_vcenter_smoke


Description
###########

Check deployment with VMware DVS plugin and one controller.


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
    3. Add nodes with following roles:
        * Controller
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on conrollers.
    8. Deploy cluster.
    9. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin and vmware datastore backend.
--------------------------------------------------------


ID
##

dvs_vcenter_bvt


Description
###########

Deploy cluster with plugin and vmware datastore backend.


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
    3. Add nodes with following roles:
        * Controller
        * Compute
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin, ComputeVMware and VMware datastore backend.
-----------------------------------------------------------------------


ID
##

dvs_vcenter_bvt_2


Description
###########

Deploy cluster with plugin, vmware datastore backend and compute-vmware role.


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
    3. Add nodes with following roles:
        * Controller
        * Compute
        * ComputeVMWare
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.
