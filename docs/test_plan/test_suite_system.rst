System
======


Setup for system tests.
-----------------------


ID
##

dvs_setup_system


Description
###########

Deploy environment in DualHypervisors mode with 3 controlers, 2 compute-vmware and 1 compute nodes. Nova Compute instances are running on controller nodes.


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
       
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
        
    11. Deploy cluster.
    12.  Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Check abilities to create and terminate networks on DVS.
--------------------------------------------------------


ID
##

dvs_create_terminate_networks


Description
###########

Check abilities to create and terminate networks on DVS.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Add private networks net_01 and net_02.
    4. Check that networks are present in the vSphere.
    5. Remove private network net_01.
    6. Check that network net_01 is not present in the vSphere.
    7. Add private network net_01.
    8. Check that networks is  present in the vSphere.


Expected result
###############

Networks were successfuly created and presented in Horizont and vSphere.


Check abilities to assign multiple vNIC to a single VM.
-------------------------------------------------------


ID
##

dvs_assign_multiple_vNIC_to_single_VM


Description
###########

Check abilities to assign multiple vNIC to a single VM.


Complexity
##########

core


Steps
#####

    1. Setup for system tests
    2. Log in to Horizon Dashboard.
    3. Add two private networks (net01, and net02).
    4. Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
    5. Launch instance VM_1 with image TestVM and flavor m1.micro in nova az.
    6. Launch instance VM_2  with image TestVM-VMDK and flavor m1.micro vcenter az.
    7. Check abilities to assign multiple vNIC net01 and net02 to VM_1 .
    8. Check abilities to assign multiple vNIC net01 and net02 to VM_2 .
    9. Check that both interfaces on each VM got a ip address. To activate second interface on cirros edit the /etc/network/interfaces and restart network: "sudo /etc/init.d/S40network restart"
    10. Send icmp ping from VM _1 to VM_2  and vice versa.


Expected result
###############

VM_1 and VM_2 should be attached to multiple vNIC net01 and net02. Pings should get a response.


Check connection between VMs in one default tenant.
---------------------------------------------------


ID
##

dvs_connection_between_VMs_from_different_availability zones


Description
###########

Check connectivity between VMs in default tenant which works in different availability zones: on KVM/QEMU and on vCenter.


Complexity
##########

core


Steps
#####

    1. Setup for system tests
    2. Navigate to Project ->  Compute -> Instances
       
    3. Launch instance VM_1 with image TestVM and flavor m1.micro in nova az.
    4. Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter az.
    5. Verify that VM_1 and VM_2 on different hypervisors  should communicate between each other. Send icmp ping from VM_1 of vCenter to VM_2 from Qemu/KVM and vice versa.


Expected result
###############

Pings should get a response.


Check connection between VMs in one non default tenant.
-------------------------------------------------------


ID
##

dvs_connection_between_VMs_in_one_tenant


Description
###########

Check connection between VMs in one tenant.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create tenant net_01 with subnet.
    4. Navigate to Project ->  Compute -> Instances
    5. Launch instance VM_1 with image TestVM and flavor m1.micro in nova az in net_01
    6. Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter az in net_01
    7. Verify that VMs on same tenants should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.


Expected result
###############

Pings should get a response.


Check connectivity between VMs attached to different networks with and within a router between them.
----------------------------------------------------------------------------------------------------


ID
##

dvs_connectivity_between_vms_different_networks


Description
###########

Check connectivity between VMs attached to different networks with and within a router between them.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Add two private networks (net01, and net02).
    4. Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
    5. Navigate to Project ->  Compute -> Instances
    6. Launch instances VM_1 and VM_2 in the network192.168.101.0/24 with image TestVM and flavor m1.micro in nova az.
    7. Launch instances VM_3 and VM_4 in the 192.168.102.0/24 with image TestVM-VMDK and flavor m1.micro in vcenter az.
    8. Verify that VMs of  same networks should communicate between each other. Send icmp ping from VM _1  to VM_2,  VM _3  to VM_4 and vice versa.
    9. Verify that VMs of  different networks should not communicate between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2  and vice versa. 
    10. Create Router_01, set gateway and add interface to external network.
    11. Attach private networks to Router_01.
    12. Verify that VMs of  different networks should communicate between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2)  and vice versa. 
    13. Add new Router_02, set gateway and add interface to external network.
    14. Delete net_02 from Router_01 and add it to the Router_02.
    15. Verify that VMs of different networks should not communicate between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2  and vice versa.


Expected result
###############

Network connectivity must conform to each of the scenarios.


Check isolation between VMs in different tenants.
-------------------------------------------------


ID
##

dvs_no_connectivity_between_Vms_different_tenants


Description
###########

Check isolation between VMs in different tenants.


Complexity
##########

core


Steps
#####

    1. Setup for system tests
    2. Log in to Horizon Dashboard.
    3. Create non-admin tenant.
    4. Navigate to Identity -> Projects.
    5. Click on Create Project.
    6. Type name test_tenant.
    7. On tab Project Members add admin with admin and member
    8. Navigate to Project -> Network -> Networks
    9. Create network  with  subnet.
    10. Navigate to Project ->  Compute -> Instances
    11. Launch instance VM_1  with image TestVM-VMDK in the vcenter az.
    12. Navigate to test_tenant
    13. Navigate to Project -> Network -> Networks 
    14. Create Router, set gateway and add interface
    15. Navigate to Project ->  Compute -> Instances
    16. Launch instance VM_2 with image TestVM-VMDK in the vcenter az.
    17. Verify that VMs on different tenants should not communicate between each other. Send icmp ping from VM _1 of admin tenant to VM_2  of test_tenant and vice versa.


Expected result
###############

Pings should not get a response.


Check connectivity Vms to public network without floating ip.
-------------------------------------------------------------


ID
##

dvs_connectivity_vms_to_public_net_without_floating_ip


Description
###########

Check connectivity Vms to public network without floating ip.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create net01: net01__subnet, 192.168.112.0/24 and attach it to the router04
    4. Launch instance VM_1 of nova AZ with image TestVM and flavor m1.micro in the net_04.
    5. Launch instance VM_2  of vcenter AZ with image TestVM-VMDK and flavor m1.micro in the net_01.
    6. Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.


Expected result
###############

Pings should  get a response


Check abilities to create and delete security group.
----------------------------------------------------


ID
##

dvs_create_delete_security_group


Description
###########

Check abilities to create and delete security group.


Complexity
##########

core


Steps
#####

    1. Setup for system tests
    2. Log in to Horizon Dashboard.
       
    3. Launch instance VM_1 in the tenant network net_02 with image TestVM and flavor m1.micro in the nova az.
    4. Launch instance VM_2  in the tenant net_02  with image TestVM-VMDK and flavor m1.micro in the vcenter az.
    5. Create security groups SG_1 to allow ICMP traffic.
    6. Add Ingress rule for ICMP protocol to SG_1
    7. Attach SG_1 to VMs
    8. Check ping between VM_1 and VM_2 and vice verse
    9. Create security groups SG_2 to allow TCP traffic 80 port.
    10. Add Ingress rule for TCP protocol to SG_2
        
    11. Attach SG_2 to VMs
    12. SSh from VM_1 to VM_2 and vice verse
    13. Delete all rules from SG_1 and SG_2
    14. Check that ping and ssh aren't available from VM_1 to VM_2  and vice verse
    15. Add Ingress rule for ICMP protocol to SG_1
    16. Add Ingress rule for TCP protocol to SG_2
    17. Check ping between VM_1 and VM_2 and vice verse
    18. Check SSh from VM_1 to VM_2 and vice verse
    19. Delete Ingress rule for ICMP protocol from SG_1
    20. Add Ingress rule for ICMP ipv6 to SG_1
    21. Check ping6 between VM_1 and VM_2 and vice versa
    22. Delete security group.
    23. Attach Vms to default security group.
    24. Check ping between VM_1 and VM_2 and vice verse
    25. Check SSh from VM_1 to VM_2 and vice verse
        


Expected result
###############

We should have the ability to send ICMP and TCP traffic between VMs in different tenants.


Verify that only the associated MAC and IP addresses can communicate on the logical port.
-----------------------------------------------------------------------------------------


ID
##

dvs_port_security_group


Description
###########

Verify that only the associated MAC and IP addresses can communicate on the logical port.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Launch 2 instances on each of hypervisors.
    4. Verify that traffic can be successfully sent from and received on the MAC and IP address associated with the logical port.
    5. Configure a new IP address on the instance associated with the logical port.
    6. Confirm that the instance cannot communicate with that IP address.
    7. Configure a new MAC address on the instance associated with the logical port. 
    8. Confirm that the instance cannot communicate with that MAC address and the original IP address.


Expected result
###############

Instance should not communicate with new ip and mac addresses but it should communicate with old IP.


Check connectivity Vms to public network with floating ip.
----------------------------------------------------------


ID
##

dvs_connectivity_vms_to_public_net_with_floating_ip


Description
###########

Check connectivity Vms to public network with floating ip.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create net01: net01__subnet, 192.168.112.0/24 and attach it to the router04
    4. Launch instance VM_1 of nova AZ with image TestVM and flavor m1.micro in the net_04. Associate floating ip.
    5. Launch instance VM_2 of vcenter AZ with image TestVM-VMDK  and flavor m1.micro in the net_01. Associate floating ip.
    6. Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.


Expected result
###############

Instances have access to an internet.


Check connectivity between VMs with same ip in different tenants.
-----------------------------------------------------------------


ID
##

dvs_connectivity_between_Vms_in_different_tenants


Description
###########

Check connectivity between VMs with same ip in different tenants.


Complexity
##########

core


Steps
#####

    1. Setup for system tests
    2. Log in to Horizon Dashboard.
    3. Create 2 non-admin tenants "test_1" and "test_2".
    4. Navigate to Identity -> Projects.
    5. Click on Create Project.
    6. Type name "test_1" of tenant.
    7. Click on Create Project.
    8. Type name "test_2" of tenant.
    9. On tab Project Members add admin with admin and member.
    10. In tenant "test_1" create net1 and subnet1 with CIDR 10.0.0.0/24.
    11. In tenant "test_1" create security group "SG_1" and add rule that allows ingress icmp traffic.
    12. In tenant "test_2" create net2 and subnet2 with CIDR 10.0.0.0/24.
    13. In tenant "test_2" create security group "SG_2".
    14. In tenant "test_1" add VM_1 of vcenter in net1 with ip 10.0.0.4 and "SG_1" as security group.
    15. In tenant "test_1" add  VM_2 of nova in net1 with ip 10.0.0.5 and "SG_1" as security group.
    16. In tenant "test_2" create net1 and subnet1 with CIDR 10.0.0.0/24.
    17. In tenant "test_2" create security group "SG_1" and add rule that allows ingress icmp traffic.
    18. In tenant "test_2" add  VM_3 of nova  in net1 with ip 10.0.0.4 and "SG_1" as security group.
    19. In tenant "test_2" add VM_4 of vcenter in net1 with ip 10.0.0.5 and "SG_1" as security group.
    20. Verify that VMs with same ip on different tenants should communicate between each other. Send icmp ping from VM _1 to VM_3,  VM_2 to Vm_4 and vice versa.


Expected result
###############

Pings should  get a response.


Check creation instance in the one group simultaneously.
--------------------------------------------------------


ID
##

dvs_vcenter_10_instances


Description
###########

Create a batch of instances.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Navigate to Project -> Compute -> Instances
    3. Launch 10 instance VM_1 simultaneously with image TestVM and flavor m1.micro in nova az in default net_04.
    4. Launch 10 instance VM_2 simultaneously with image TestVM-VMDK and flavor m1.micro in vcenter az in default net_04.
    5. Check connection between VMs(ping, ssh).
    6. Delete all Vms from horizon simultaneously.


Expected result
###############

All instance should be created and deleted without any error.


Check that we can create volumes to an instance from different availability zones, which have different types of hypervisors.
-----------------------------------------------------------------------------------------------------------------------------


ID
##

dvs_vcenter_volume


Description
###########

Create volumes in different availability zones and attach them to appropriate instances.


Complexity
##########

core


Steps
#####

    1. Install plugin on master node.
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
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on conrollers.
    8. Verify networks.
    9. Deploy cluster.
    10. Create  VM for each of hypervisor's type
    11. Create 2 volumes each in his own availability zone.
    12. Attach each volume to his instance.


Expected result
###############

Each volume should be attached to his instance.


Check abilities to update network name
--------------------------------------


ID
##

dvs_update_network


Description
###########

Check abilities to update network name


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in Horizon.
    3. Create network net_1.
    4. Update network name net_1 to net_2.
    5. Update default network name net04 to net4.


Expected result
###############

Network name should be changed successfully


Check abilities to create stack heat from template.
---------------------------------------------------


ID
##

dvs_vcenter_heat


Description
###########

Check abilities to stack heat from template.


Complexity
##########

core


Steps
#####

    1. Create stack with heat template.
    2. Check that stack was created.


Expected result
###############

Stack was successfully created.


System (Compute-vmware)
=======================


Setup for system tests with compute-vmware.
-------------------------------------------


ID
##

dvs_compute_vmware_setup_system


Description
###########

Deploy environment in DualHypervisors mode with 3 controlers, 2 compute-vmware and 1 compute nodes. Nova Compute instances are running on compute-vmware nodes.


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
        * ComputeVMware
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on compute-vmware.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Check abilities to create and terminate networks on DVS.
--------------------------------------------------------


ID
##

dvs_compute_vmware_create_terminate_networks


Description
###########

Check abilities to create and terminate networks on DVS with Compute-VMware role.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Add private networks net_01 and net_02.
    4. Check that networks are present in the vSphere.
    5. Remove private network net_01.
    6. Check that network net_01 is not present in the vSphere.
    7. Add private network net_01.
    8. Check that networks is  present in the vSphere.


Expected result
###############

Networks were successfuly created and presented in Horizont and vSphere.


Check abilities to assign multiple vNIC to a single VM.
-------------------------------------------------------


ID
##

dvs_compute_vmware_assign_multiple_vNIC_to_single_VM


Description
###########

Check abilities to assign multiple vNIC to a single VM.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Add two private networks (net01, and net02).
    4. Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
    5. Launch instance VM_1 with image TestVM and flavor m1.micro in nova az.
    6. Launch instance VM_2  with image TestVM-VMDK and flavor m1.micro vcenter az.
    7. Check abilities to assign multiple vNIC net01 and net02 to VM_1 .
    8. Check abilities to assign multiple vNIC net01 and net02 to VM_2 .
    9. Send icmp ping from VM _1 to VM_2  and vice versa.


Expected result
###############

VM_1 and VM_2 should be attached to multiple vNIC net01 and net02. Pings should get a response.


Check connection between VMs in one default tenant.
---------------------------------------------------


ID
##

dvs_compute_vmware_connection_between_VMs_from_different_availability zones


Description
###########

Check connectivity between VMs in default tenant which works in different availability zones: on KVM/QEMU and on vCenter.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Navigate to Project ->  Compute -> Instances
    3. Launch instance VM_1 with image TestVM and flavor m1.micro in nova az.
    4. Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter az.
    5. Verify that VM_1 and VM_2 on different hypervisors  should communicate between each other. Send icmp ping from VM_1 of vCenter to VM_2 from Qemu/KVM and vice versa.


Expected result
###############

Pings should get a response


Check connection between VMs in one non default tenant.
-------------------------------------------------------


ID
##

dvs_compute_vmware_connection_between_VMs_in_one_tenant_compute_vmware


Description
###########

Check connection between VMs in one tenant.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Create tenant net_01 with subnet.
    4. Navigate to Project ->  Compute -> Instances
    5. Launch instance VM_1 with image TestVM and flavor m1.micro in nova az in net_01
    6. Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter az in net_01
    7. Verify that VMs on same tenants should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.


Expected result
###############

Pings should get a response


Check connectivity between VMs attached to different networks with and within a router between them.
----------------------------------------------------------------------------------------------------


ID
##

dvs_compute_vmware_connectivity_between_vms_different_networks


Description
###########

Check connectivity between VMs attached to different networks with and within a router between them.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Add two private networks (net01, and net02).
    4. Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
    5. Navigate to Project ->  Compute -> Instances
    6. Launch instances VM_1 and VM_2 in the network192.168.101.0/24 with image TestVM and flavor m1.micro in nova az.
    7. Launch instances VM_3 and VM_4 in the 192.168.102.0/24 with image TestVM-VMDK and flavor m1.micro in vcenter az.
    8. Verify that VMs of  same networks should communicate between each other. Send icmp ping from VM _1  to VM_2,  VM _3  to VM_4 and vice versa.
    9. Verify that VMs of  different networks should not communicate between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2  and vice versa.
    10. Create Router_01, set gateway and add interface to external network.
    11. Attach private networks to Router_01.
    12. Verify that VMs of  different networks should communicate between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2)  and vice versa.
    13. Add a new Router_02, set gateway and add interface to external network.
    14. Delete net_02 from Router_01 and add it to the Router_02.
    15. Verify that VMs of  different networks should not communicate between each other. Send icmp ping from VM _1 to VM_3, VM_4 to VM_2  and vice versa.


Expected result
###############

Network connectivity must conform to each of the scenarios.


Check isolation between VMs in different tenants.
-------------------------------------------------


ID
##

dvs_compute_vmware_no_connectivity_between_Vms_different_tenants


Description
###########

Check isolation between VMs in different tenants.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Create non-admin tenant.
    4. Navigate to Identity -> Projects.
    5. Click on Create Project.
    6. Type name test_tenant.
    7. On tab Project Members add admin with admin and member
    8. Navigate to Project -> Network -> Networks
    9. Create network  with  subnet.
    10. Navigate to Project ->  Compute -> Instances
    11. Launch instance VM_1
    12. Navigate to test_tenant
    13. Navigate to Project -> Network -> Networks
    14. Create Router, set gateway and add interface
    15. Navigate to Project ->  Compute -> Instances
    16. Launch instance VM_2
    17. Verify that VMs on different tenants should not communicate between each other. Send icmp ping from VM _1 of admin tenant to VM_2  of test_tenant and vice versa.


Expected result
###############

Pings should not get a response.


Check connectivity Vms to public network without floating ip
------------------------------------------------------------


ID
##

dvs_compute_vmware_connectivity_vms_to_public_net_without_floating_ip


Description
###########

Check connectivity Vms to public network without floating ip.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Create net01: net01__subnet, 192.168.112.0/24 and attach it to the router04
    4. Launch instance VM_1 of nova AZ with image TestVM and flavor m1.micro in the net_04.
    5. Launch instance VM_2 of vcenter AZ with image TestVM-VMDK and flavor m1.micro in the net_01.
    6. Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.


Expected result
###############

Pings should  get a response.


Check abilities to create and delete security group.
----------------------------------------------------


ID
##

dvs_compute_vmware_create_delete_security_group


Description
###########

Check abilities to create and delete security group.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Launch instance VM_1 in the tenant network net_02 with image TestVM and flavor m1.micro in the nova az.
    4. Launch instance VM_2  in the tenant net_02  with image TestVM-VMDK and flavor m1.micro in the vcenter az.
    5. Create security groups SG_1 to allow ICMP traffic.
    6. Add Ingress rule for ICMP protocol to SG_1
    7. Attach SG_1 to VMs
    8. Check ping between VM_1 and VM_2 and vice verse
    9. Create security groups SG_2 to allow TCP traffic 80 port.
    10. Add Ingress rule for TCP protocol to SG_2
    11. Attach SG_2 to VMs
    12. SSh from VM_1 to VM_2 and vice verse
    13. Delete all rules from SG_1 and SG_2
    14. Check that ping and ssh aren't available from VM_1 to VM_2  and vice verse
    15. Add Ingress rule for ICMP protocol to SG_1
    16. Add Ingress rule for TCP protocol to SG_2
    17. Check ping between VM_1 and VM_2 and vice verse
    18. Check SSh from VM_1 to VM_2 and vice verse
    19. Delete Ingress rule for ICMP protocol from SG_1
    20. Add Ingress rule for ICMP ipv6 to SG_1
    21. Check ping6 between VM_1 and VM_2 and vice versa
    22. Delete security group.
    23. Attach Vms to default security group.
    24. Check ping between VM_1 and VM_2 and vice verse.
    25. Check SSh from VM_1 to VM_2 and vice verse.


Expected result
###############

We should have the ability to send ICMP and TCP traffic between VMs in different tenants.


Verify that only the associated MAC and IP addresses can communicate on the logical port.
-----------------------------------------------------------------------------------------


ID
##

dvs_compute_vmware_port_security_group


Description
###########

Verify that only the associated MAC and IP addresses can communicate on the logical port.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Launch 2 instances on each of hypervisors.
    4. Verify that traffic can be successfully sent from and received on the MAC and IP address associated with the logical port.
    5. Configure a new IP address on the instance associated with the logical port.
    6. Confirm that the instance cannot communicate with that IP address.
    7. Configure a new MAC address on the instance associated with the logical port.
    8. Confirm that the instance cannot communicate with that MAC address and the original IP address.


Expected result
###############

Instance should not communicate with new ip and mac addresses but it should communicate with old IP.


Check connectivity VMs to public network with floating ip.
----------------------------------------------------------


ID
##

dvs_compute_vmware_connectivity_vms_to_public_net_with_floating_ip


Description
###########

Check connectivity Vms to public network with floating ip.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Create net01: net01__subnet, 192.168.112.0/24 and attach it to the router04
    4. Launch instance VM_1 of nova AZ with image TestVM and flavor m1.micro in the net_04. Associate floating ip.
    5. Launch instance VM_2 of vcenter AZ with image TestVM-VMDK and flavor m1.micro in the net_01. Associate floating ip.
    6. Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.


Expected result
###############

Instances have access to an internet.


Check connectivity between VMs with same ip in different tenants.
-----------------------------------------------------------------


ID
##

dvs_compute_vmware_connectivity_between_Vms_in_different_tenants


Description
###########

Check connectivity between VMs with same ip in different tenants.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in to Horizon Dashboard.
    3. Create 2 non-admin tenants "test_1" and "test_2".
    4. Navigate to Identity -> Projects.
    5. Click on Create Project.
    6. Type name "test_1" of tenant.
    7. Click on Create Project.
    8. Type name "test_2" of tenant.
    9. On tab Project Members add admin with admin and member.
    10. In tenant "test_1" create net1 and subnet1 with CIDR 10.0.0.0/24.
    11. In tenant "test_1" create security group "SG_1" and add rule that allows ingress icmp traffic.
    12. In tenant "test_2" create net2 and subnet2 with CIDR 10.0.0.0/24.
    13. In tenant "test_2" create security group "SG_2".
    14. In tenant "test_1" add  VM_1 of vcenter  in net1 with ip 10.0.0.4 and "SG_1" as security group.
    15. In tenant "test_1" add  VM_2 of nova  in net1 with ip 10.0.0.5 and "SG_1" as security group.
    16. In tenant "test_2" create net1 and subnet1 with CIDR 10.0.0.0/24.
    17. In tenant "test_2" create security group "SG_1" and add rule that allows ingress icmp traffic.
    18. In tenant "test_2" add  VM_3 of nova  in net1 with ip 10.0.0.4 and "SG_1" as security group.
    19. In tenant "test_2" add  VM_4 of vcenter in net1 with ip 10.0.0.5 and "SG_1" as security group.
    20. Verify that VMs with same ip on different tenants should communicate between each other. Send icmp ping from VM _1 to VM_3,  VM_2 to Vm_4 and vice versa.


Expected result
###############

Pings should  get a response.


Check creation instance in the one group simultaneously.
--------------------------------------------------------


ID
##

dvs_compute_vmware_vcenter_10_instances


Description
###########

Create a batch of instances.


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Navigate to Project -> Compute -> Instances
    3. Launch 10 instance VM_1 simultaneously with image TestVM and flavor m1.micro in nova az in default net_04
    4. Launch 10 instance VM_2 simultaneously with image TestVM-VMDK and flavor m1.micro in nova az in default net_04
    5. Check connection between VMs(ping, ssh)
    6. Delete all Vms from horizon simultaneously.


Expected result
###############

All instance should be created and deleted without any error.


Check that we can create volumes to an instance from different availability zones, which have different types of hypervisors
----------------------------------------------------------------------------------------------------------------------------


ID
##

dvs_compute_vmware_vcenter_volume


Description
###########

Create volumes in different availability zones and attach them to appropriate instances.


Complexity
##########

core


Steps
#####

    1. Install plugin on master node.
    2. Create a new environment with following parameters:
        * Compute: KVM/QEMU with vCenter
        * Networking: Neutron with VLAN segmentation
        * Storage: default
        * Additional services: default
    3. Add nodes with following roles:
        * Controller
        * Cinder
        * CinderVMware
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    8. Verify networks.
    9. Deploy cluster.
    10. Create VM for each of hypervisor's type
    11. Create 2 volumes each in his own availability zone.
    12. Attach each volume to his instance.


Expected result
###############

Each volume should be attached to his instance.


Check abilities to update network name
--------------------------------------


ID
##

dvs_compute_vmware_update_network


Description
###########

Check abilities to update network name


Complexity
##########

core


Steps
#####

    1. Setup for system tests with compute-vmware.
    2. Log in Horizon.
    3. Create network net_1.
    4. Update network name net_1 to net_2.
    5. Update default network name net04 to net4.


Expected result
###############

Network name should be changed successfully.


Check abilities to create stack heat from template.
---------------------------------------------------


ID
##

dvs_compute_vmware_vcenter_heat


Description
###########

Check abilities to stack heat from template.


Complexity
##########

core


Steps
#####

    1. Create stack with heat template.
    2. Check that stack was created.


Expected result
###############

Stack was successfully created.
