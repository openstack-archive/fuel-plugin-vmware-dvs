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

    1. Connect to fuel node with pre-installed plugin via ssh.
    2. Remove plugin.


Expected result
###############

Verify that plugin is removed, run command 'fuel plugins'.


Verify that all elements of DVS plugin section meet the requirements.
---------------------------------------------------------------------


ID
##

dvs_gui


Description
###########

Verify that all elements of DVS plugin section meet the requirements.


Complexity
##########

smoke


Steps
#####

    1. Install Neutron VMware DVS ML2 plugin on master node. Connect to the Fuel Web UI.
    2. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    3. Go to Network tab -> Other subtab and check DVS plugin section is displayed with all required GUI elements:
       'Neutron VMware DVS ML2 plugin' check box
       "Use the VMware DVS firewall driver" check box
       "Enter the cluster to dvSwitch mapping." text field with description 'List of ClusterName:SwitchName pairs, separated by semicolon. '
       'Versions' radio button with <plugin version>
    4. Verify that check box "Neutron VMware DVS ML2 plugin" is enabled by default.
    5. Verify that user can disable -> enable the DVS plugin by clicking on the checkbox “Neutron VMware DVS ML2 plugin”
    6. Verify that check box "Use the VMware DVS firewall driver" is enabled by default.
    7. Verify that all labels of the DVS plugin section have the same font style and color.
    8. Verify that all elements of the DVS plugin section are vertically aligned


Expected result
###############

All elements of DVS plugin section meet the requirements.


Deployment with plugin, controller and vmware datastore backend.
----------------------------------------------------------------


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

    1. Upload plugins to the master node.
    2. Install plugin.
    3. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    4. Add nodes with following roles:
        * Controller
    5. Configure interfaces on nodes.
    6. Configure network settings.
    7. Enable and configure DVS plugin.
    8. Configure VMware vCenter Settings. Add 1 vSphere cluster and configure
       Nova Compute instances on controllers.
    9. Deploy cluster.
    10. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin and ceph datastore backend.
------------------------------------------------------


ID
##

dvs_vcenter_bvt


Description
###########

Check deployment with VMware DVS plugin, 3 Controllers, Compute, 2 CephOSD, CinderVMware and computeVMware roles.


Complexity
##########

smoke


Steps
#####

    1. Connect to the Fuel web UI with pre-installed plugin.
    2. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: Ceph
        * Additional services: default
    3. Add nodes with following roles:
        * Controller
        * Controller
        * Controller
        * Compute + CephOSD
        * Compute + CephOSD
        * Compute + CephOSD
        * CinderVMware + ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on controllers and compute-vmware.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.
