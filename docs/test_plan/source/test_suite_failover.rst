Failover
========


Verify that it is not possible to uninstall Fuel DVS plugin with deployed environment.
--------------------------------------------------------------------------------------


ID
##

dvs_vcenter_uninstall


Description
###########

Verify that it is not possible to uninstall Fuel DVS plugin with deployed environment.


Complexity
##########

core


Steps
#####

    1. Install DVS plugin on master node.
    2. Create a new environment with enabled plugin.
    3. Try to delete plugin via cli


Expected result
###############

Alert: "400 Client Error: Bad Request (Can't delete plugin which is enabled for some environment.)" should be displayed.


Verify that vmclusters migrate after shutdown of controller.
------------------------------------------------------------


ID
##

dvs_vcenter_shutdown_controller


Description
###########

Verify that vcenter-vmcluster migrates after shutdown of controller.


Complexity
##########

core


Steps
#####

    1. Install DVS plugin on master node.
    2. Create a new environment with the following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    3. Add nodes with following roles:
        * Controller
        * Controller
        * Controller
        * Compute
        * Compute
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on controllers.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.
    11. Launch instances in nova and vcenter availability zones.
    12. Verify connection between instances: check that instances can ping each other.
    13. Shutdown controller with vmclusters.
    14. Check that vcenter-vmcluster migrates to another controller.
    15. Verify connection between instances: check that instances can ping each other.


Expected result
###############

Vcenter-vmcluster should migrate to another controller. Ping is available between instances.


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
    2. Create a new environment with the following parameters:
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
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure
       Nova Compute instances on controllers.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.
    11. Launch instance VM_1 from image TestVM, with availability zone nova and flavor m1.micro.
    12. Launch instance VM_2 from image TestVM-VMDK, with availability zone vcenter and flavor m1.micro.
    13. Verify connection between instances: check that VM_1 and VM_2 can ping each other.
    14. Reboot vcenter.
    15. Check that controller lost connection with vCenter.
    16. Wait for vCenter.
    17. Ensure connectivity between instances.
    18. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed. Ping should get response.


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
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure
       Nova Compute instances on compute-vmware.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.
    11. Launch instance VM_1 with image TestVM, nova availability zone and flavor m1.micro.
    12. Launch instance VM_2 with image TestVM-VMDK, vcenter availability zone and flavor m1.micro.
    13. Verify connection between instances: check that VM_1 and VM_2 can ping each other.
    14. Reboot vCenter.
    15. Check that ComputeVMware lost connection with vCenter.
    16. Wait for vCenter.
    17. Ensure connectivity between instances.
    18. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed. Pings should get response.


Verify that vmclusters migrate after reset of controller.
---------------------------------------------------------


ID
##

dvs_vcenter_reset_controller


Description
###########

Verify that vcenter-vmcluster migrates after reset of controller.


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
        * Compute
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on controllers.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.
    11. Launch instances in nova and vcenter availability zones.
    12. Verify connection between instances: check that instances can ping each other.
    13. Reset controller with vmclusters services.
    14. Check that vmclusters services migrate to another controller.
    15. Verify connection between instances: check that instances can ping each other.


Expected result
###############

Vcenter-vmcluster should migrate to another controller. Ping is available between instances.
