Destructive
===========


Check abilities to bind port on DVS to VM, disable and enable this port.
------------------------------------------------------------------------


ID
##

dvs_enable_disable_port_on_dvs_to_vm


Description
###########

Check abilities to bind port on DVS to VM, disable and enable this port.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Navigate to Project ->  Compute -> Instances
    4. Launch instance VM_1 with image TestVM, availability zone nova and flavor m1.micro.
    5. Launch instance VM_2  with image TestVM-VMDK, availability zone  vcenter and flavor m1.micro.
    6. Verify that VMs  should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.
    7. Disable dvs_port of VM_1.
    8. Verify that VMs  should not communicate between each other. Send icmp ping from VM _2 to VM_1  and vice versa.
    9. Enable dvs_port of VM_1.
    10. Verify that VMs  should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.


Expected result
###############

We can enable/disable DVS ports via Horizont.


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


Deploy cluster with plugin, addition and deletion of nodes.
-----------------------------------------------------------


ID
##

dvs_vcenter_add_delete_nodes


Description
###########

Deploy cluster with plugin, addition and deletion of nodes.


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
        * Compute
        * CinderVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF
    13. Remove node with cinder-vmdk role.
    14. Add node with cinder role.
    15. Redeploy cluster.
    16.  Run OSTF.
    17. Remove node with compute role.
    18. Add node with cinder-vmdk  role.
    19. Redeploy cluster.
    20. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin and deletion one node with controller role.
----------------------------------------------------------------------


ID
##

dvs_vcenter_remove_controller


Description
###########

Deploy cluster with plugin and deletion one node with controller role.


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
        * Controller
        * Compute
        * CinderVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.
    13. Remove node with controller role.
    14. Redeploy cluster.
    15. Run OSTF.
    16. Add controller.
    17. Redeploy cluster.
    18. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


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
