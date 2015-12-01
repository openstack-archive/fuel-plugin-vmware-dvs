Failover
========


Verify that it is not possibility to uninstall of Fuel DVS plugin with deployed environment.
--------------------------------------------------------------------------------------------


ID
##

dvs_uninstall_negative


Description
###########

Verify that it is not possibility to uninstall of Fuel DVS plugin with deployed environment.


Complexity
##########

core


Steps
#####

    1. Install DVS plugin on master node.
    2. Create a new environment with enabled plugin.
    3. Try to delete plugin via cli Remove plugin from master node.


Expected result
###############

Alert: "400 Client Error: Bad Request (Can't delete plugin which is enabled for some environment.)" should be displayed.



Verify that vmclusters should be migrate after shutdown controller.
-------------------------------------------------------------------


ID
##

dvs_shutdown_controller


Description
###########

Verify that vmclusters should be migrate after shutdown controller.


Complexity
##########

core


Steps
#####

    1. Install DVS plugin on master node.
    2. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    3. Add nodes with following roles:
        * Controller
        * Controller
        * Controller
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF
    11. Shutdown controller with  vmclusters.
    12. Check that vmclusters should be migrate to another controller.


Expected result
###############

VMclusters should be migrate to another controller.


Check cluster functionality after reboot vcenter (Nova Compute on controllers).
-------------------------------------------------------------------------------


ID
##

dvs_vcenter_reboot_vcenter


Description
###########

Check cluster functionality after reboot vcenter. Nova Compute instances are running on controller nodes.


Complexity
##########

core


Steps
#####

    1. Install DVS plugin on master node.
    2. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    3. Add nodes with following roles:
        * Controller
        * Compute
        * Cinder
        * CinderVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.
    13. Launch instance VM_1 with image TestVM, availability zone nova and flavor m1.micro.
    14. Launch instance VM_2  with image TestVM-VMDK, availability zone vcenter and flavor m1.micro.
    15. Check connection between VMs, send ping from VM_1 to VM_2 and vice verse.
    16. Reboot vcenter.
    17. Check that controller lost connection with vCenter.
    18. Wait for vCenter.
    19. Ensure that all instances from vCenter displayed in dashboard.
    20. Ensure connectivity between Nova's and VMware's VM.
    21. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed. ping shoul get response.


Check cluster functionality after reboot vcenter (Nova Compute on compute-vmware).
----------------------------------------------------------------------------------


ID
##

dvs_vcenter_reboot_vcenter_2


Description
###########

Check cluster functionality after reboot vcenter. Nova Compute instances are running on compute-vmware nodes.


Complexity
##########

core


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
        * Cinder
        * CinderVMware
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.
    13. Launch instance VM_1 with image TestVM, AZ nova and flavor m1.micro.
    14. Launch instance VM_2  with image TestVM-VMDK, AZ vcenter and flavor m1.micro.
    15. Check connection between VMs, send ping from VM_1 to VM_2 and vice verse.
    16. Reboot vcenter.
    17. Check that ComputeVMware lost connection with vCenter.
    18. Wait for vCenter.
    19. Ensure that all instances from vCenter displayed in dashboard.
    20. Ensure connectivity between Nova's and VMware's VM.
    21. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed. pings shoul get response.

