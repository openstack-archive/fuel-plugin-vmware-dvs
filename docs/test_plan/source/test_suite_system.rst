System
======


Setup for system tests.
-----------------------


ID
##

dvs_vcenter_systest_setup


Description
###########

Deploy environment in DualHypervisors mode with 3 controllers, 2 compute-vmware and 1 compute nodes. Nova Compute instances are running on controller nodes.


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
        * Compute
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMware vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on controllers and compute-vmware.
    9. Verify networks.
    10. Deploy cluster.
    11.  Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Check abilities to create and terminate networks on DVS.
--------------------------------------------------------


ID
##

dvs_vcenter_networks


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

Networks were successfully created and presented in Horizon and vSphere.


Check abilities to update network name
--------------------------------------


ID
##

dvs_update_network


Description
###########

Check abilities to update network name.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in Horizon.
    3. Create network net_1.
    4. Update network name net_1 to net_2.
    5. Update name of default network   to 'spring'.


Expected result
###############

Network name should be changed successfully.


Check abilities to bind port on DVS to instance, disable and enable this port.
------------------------------------------------------------------------------


ID
##

dvs_vcenter_bind_port


Description
###########

Check abilities to bind port on DVS to instance, disable and enable this port.


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
    6. Verify that instances  should communicate between each other. Send icmp ping from VM_1 to VM_2  and vice versa.
    7. Disable interface of VM_1.
    8. Verify that instances  should not communicate between each other. Send icmp ping from VM_2 to VM_1  and vice versa.
    9. Enable interface of VM_1.
    10. Verify that instances  should communicate between each other. Send icmp ping from VM_1 to VM_2  and vice versa.


Expected result
###############

We can enable/disable interfaces of instances via Horizon.


Check abilities to assign multiple vNIC to a single instance.
-------------------------------------------------------------


ID
##

dvs_multi_vnic


Description
###########

Check abilities to assign multiple vNIC to a single instance.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Add two private networks (net01, and net02).
    4. Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
    5. Launch instance VM_1 with image TestVM and flavor m1.micro in nova availability zone.
    6. Launch instance VM_2  with image TestVM-VMDK and flavor m1.micro vcenter availability zone.
    7. Check abilities to assign multiple vNIC net01 and net02 to VM_1.
    8. Check abilities to assign multiple vNIC net01 and net02 to VM_2.
    9. Check that both interfaces on each instance got a ip address. To activate second interface on cirros edit the /etc/network/interfaces and restart network: "sudo /etc/init.d/S40network restart"
    10. Send icmp ping from VM_1 to VM_2  and vice versa.


Expected result
###############

VM_1 and VM_2 should be attached to multiple vNIC net01 and net02. Pings should get a response.


Check connection between instances  in one default tenant.
----------------------------------------------------------


ID
##

dvs_connect_default_net


Description
###########

Check connectivity between instances in default tenant which works in different availability zones: on KVM/QEMU and on vCenter.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Navigate to Project ->  Compute -> Instances
    3. Launch instance VM_1 with image TestVM and flavor m1.micro in nova availability zone.
    4. Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter availability zone.
    5. Verify that VM_1 and VM_2 on different hypervisors  should communicate between each other. Send icmp ping from VM_1 of vCenter to VM_2 from Qemu/KVM and vice versa.


Expected result
###############

Pings should get a response.


Check connection between instances in one non default network.
--------------------------------------------------------------


ID
##

dvs_connect_nodefault_net


Description
###########

Check connection between instances in one non default network.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create tenant net_01 with subnet.
    4. Navigate to Project ->  Compute -> Instances
    5. Launch instance VM_1 with image TestVM and flavor m1.micro in nova availability zone in net_01
    6. Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter availability zone in net_01
    7. Verify that instances on same tenants should communicate between each other. Send icmp ping from VM_1 to VM_2  and vice versa.


Expected result
###############

Pings should get a response.


Check connectivity between instances attached to different networks with and within a router between them.
----------------------------------------------------------------------------------------------------------


ID
##

dvs_different_networks


Description
###########

Check connectivity between instances attached to different networks with and within a router between them.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Create private networks net01 and net02 with subnets.
    3. Create Router_01, set gateway and add interface to external network.
    4. Create Router_02, set gateway and add interface to external network.
    5. Attach private networks to Router_01.
    6. Attach private networks to Router_02.
    7. Launch instances in the net01 with image TestVM and flavor m1.micro in nova az.
    8. Launch instances in the net01 with image TestVM-VMDK and flavor m1.micro in vcenter az.
    9. Launch instances in the net02 with image TestVM and flavor m1.micro in nova az.
    10. Launch instances in the net02 with image TestVM-VMDK and flavor m1.micro in vcenter az.
    11. Verify that instances of same networks should communicate between each other via private ip.
         Send icmp ping between instances.
    12. Verify that instances of different networks should not communicate between each other via private ip.
    13. Delete net_02 from Router_02 and add it to the Router_01.
    14. Verify that instances of different networks should communicate between each other via private ip.
         Send icmp ping between instances.


Expected result
###############

Network connectivity must conform to each of the scenarios.


Check isolation between instances in different tenants.
-------------------------------------------------------


ID
##

dvs_vcenter_tenants_isolation


Description
###########

Check isolation between instances in different tenants.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create non-admin tenant with name 'test_tenant': Identity -> Projects-> Create Project. On tab Project Members add admin with admin and member.
    4. Navigate to Project -> Network -> Networks
    5. Create network  with  subnet.
    6. Navigate to Project ->  Compute -> Instances
    7. Launch instance VM_1  with image TestVM-VMDK in the vcenter availability zone.
    8. Navigate to test_tenant.
    9. Navigate to Project -> Network -> Networks
    10. Create Router, set gateway and add interface.
    11. Navigate to Project ->  Compute -> Instances
    12. Launch instance VM_2 with image TestVM-VMDK in the vcenter availability zone.
    13. Verify that instances on different tenants should not communicate between each other. Send icmp ping from VM_1 of admin tenant to VM_2  of test_tenant and vice versa.


Expected result
###############

Pings should not get a response.


Check connectivity instances to public network without floating ip.
-------------------------------------------------------------------


ID
##

dvs_ping_without_fip


Description
###########

Check connectivity instances to public network without floating ip.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create net_01: net01_subnet, 192.168.112.0/24 and attach it to default router.
    4. Launch instance VM_1 of nova availability zone with image TestVM and flavor m1.micro in the default internal network.
    5. Launch instance VM_2  of vcenter availability zone with image TestVM-VMDK and flavor m1.micro in the net_01.
    6. Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.


Expected result
###############

Pings should  get a response


Check connectivity instances to public network with floating ip.
----------------------------------------------------------------


ID
##

dvs_vcenter_ping_public


Description
###########

Check connectivity instances to public network with floating ip.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create net01: net01__subnet, 192.168.112.0/24 and attach it to the default router.
    4. Launch instance VM_1 of nova availability zone with image TestVM and flavor m1.micro in the default internal network. Associate floating ip.
    5. Launch instance VM_2 of vcenter availability zone with image TestVM-VMDK  and flavor m1.micro in the net_01. Associate floating ip.
    6. Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.


Expected result
###############

Instances have access to an internet.


Check abilities to create and delete security group.
----------------------------------------------------


ID
##

dvs_vcenter_security


Description
###########

Check abilities to create and delete security group.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Create non default network with subnet net_01.
    3. Launch 2 instances  of vcenter availability zone and 2 instances of nova availability zone in the tenant network net_01
    4. Launch 2 instances  of vcenter availability zone and 2 instances of nova availability zone in the internal tenant network.
    5. Attach net_01 to default router.
    6. Create security group SG_1 to allow ICMP traffic.
    7. Add Ingress rule for ICMP protocol to SG_1.
    8. Create security groups SG_2 to allow TCP traffic 22 port.
    9. Add Ingress rule for TCP protocol to SG_2.
    10. Remove default security group and attach SG_1 and SG_2 to VMs
    11. Check ping is available between instances.
    12. Check ssh connection is available between instances.
    13. Delete all rules from SG_1 and SG_2.
    14. Check that ssh aren't available to instances.
    15. Add Ingress and egress rules for TCP protocol to SG_2.
    16. Check ssh connection is available between instances.
    17. Check ping is not available between instances.
    18. Add Ingress and egress rules for ICMP protocol to SG_1.
    19. Check ping is available between instances.
    20. Delete Ingress rule for ICMP protocol from SG_1 (if OS cirros skip this step).
    21. Add Ingress rule for ICMP ipv6 to SG_1 (if OS cirros skip this step).
    22. Check ping6 is available between instances. (if OS cirros skip this step).
    23. Delete SG1 and SG2 security groups.
    24. Attach instances to default security group.
    25. Check ping is available between instances.
    26. Check ssh is available between instances.


Expected result
###############

We should have the ability to send ICMP and TCP traffic between instances in different tenants.


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
    3. Launch 2 instances on each  hypervisors.
    4. Verify that traffic can be successfully sent from and received on the MAC and IP address associated with the logical port.
    5. Configure a new IP address on the instance associated with the logical port.
    6. Confirm that the instance cannot communicate with that IP address.


Expected result
###############

Each instance should not communicate with new ip address but it should
communicate with old ip address.


Check connectivity between instances with same ip in different tenants.
-----------------------------------------------------------------------


ID
##

dvs_vcenter_same_ip


Description
###########

Check connectivity between instances with same ip in different tenants.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Log in to Horizon Dashboard.
    3. Create 2 non-admin tenants "test_1" and "test_2": Identity -> Projects -> Create Project. On tab Project Members add admin with admin and member.
    4. In tenant "test_1" create net1 and subnet1 with CIDR 10.0.0.0/24.
    5. In tenant "test_1" create security group "SG_1" and add rule that allows ingress icmp traffic.
    6. In tenant "test_2" create net2 and subnet2 with CIDR 10.0.0.0/24.
    7. In tenant "test_2" create security group "SG_2".
    8. In tenant "test_1"  launch VM_1 of vcenter availability zone in net1 with ip 10.0.0.4 and "SG_1" as security group.
    9. In tenant "test_1"  launch  VM_2 of nova availability zone in net1 with ip 10.0.0.5 and "SG_1" as security group.
    10. In tenant "test_2" create net1 and subnet1 with CIDR 10.0.0.0/24.
    11. In tenant "test_2" create security group "SG_1" and add rule that allows ingress icmp traffic.
    12. In tenant "test_2" launch  VM_3 of nova  availability zone in net1 with ip 10.0.0.4 and "SG_1" as security group.
    13. In tenant "test_2" launch VM_4 of vcenter availability zone in net1 with ip 10.0.0.5 and "SG_1" as security group.
    14. Verify that instances with same ip on different tenants should communicate between each other. Send icmp ping from VM_1 to VM_3,  VM_2 to VM_4 and vice versa.


Expected result
###############

Pings should  get a response.


Check creation instance in the one group simultaneously.
--------------------------------------------------------


ID
##

dvs_instances_one_group


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
    3. Launch few instances simultaneously with image TestVM and flavor m1.micro in nova availability zone in default internal network.
    4. Launch few instances simultaneously with image TestVM-VMDK and flavor m1.micro in vcenter availability zone in  default internal network.
    5. Check connection between instances (ping, ssh).
    6. Delete all instances from horizon simultaneously.


Expected result
###############

All instances should be created and deleted without any error.


Create volumes in different availability zones and attach them to appropriate instances.
----------------------------------------------------------------------------------------


ID
##

dvs_volume


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
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on controllers.
    8. Verify networks.
    9. Deploy cluster.
    10. Create  instances for each of hypervisor's type
    11. Create 2 volumes each in his own availability zone.
    12. Attach each volume to his instance.


Expected result
###############

Each volume should be attached to his instance.


Check abilities to create stack heat from template.
---------------------------------------------------


ID
##

dvs_heat


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


Deploy cluster with DVS plugin, Neutron, Ceph and network template
------------------------------------------------------------------


ID
##

dvs_vcenter_net_template


Description
###########

Deploy cluster with DVS plugin, Neutron, Ceph and network template.


Complexity
##########

core


Steps
#####

    1. Upload plugins to the master node.
    2. Install plugin.
    3. Create cluster with vcenter.
    4. Set CephOSD as backend for Glance and Cinder
    5. Add nodes with following roles:
                       controller
                       compute-vmware
                       compute-vmware
                       compute
                       3 ceph-osd
    6. Upload network template.
    7. Check network configuration.
    8. Deploy the cluster
    9. Run OSTF


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Security group rules with remote group id.
------------------------------------------


ID
##

dvs_vcenter_remote_sg


Description
###########

Verify that network traffic is allowed/prohibited to instances according security groups
rules.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Launch ubuntu cloud image.
    3. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.
    4. Create security groups:
       SG_web
       SG_db
       SG_man
       SG_DNS
    5. Delete all default egress rules from
       SG_web
       SG_db
       SG_man
       SG_DNS
    6. Add rules to SG_web:
       Ingress rule with ip protocol 'http' , port range 80-80, ip range 0.0.0.0/0
       Ingress rule with ip protocol 'tcp ' , port range 3306-3306, SG group 'SG_db'
       Ingress rule with ip protocol 'tcp ' , port range 22-22, SG group 'SG_man
       Engress rule with ip protocol 'http' , port range 80-80, ip range 0.0.0.0/0
       Egress rule with ip protocol 'tcp ' , port range 3306-3306, SG group 'SG_db'
       Egress rule with ip protocol 'tcp ' , port range 22-22, SG group 'SG_man


    7. Add rules to SG_db:
       Egress rule with ip protocol 'http' , port range 80-80, ip range 0.0.0.0/0
       Egress rule with ip protocol 'https ' , port range 443-443, ip range 0.0.0.0/0
       Ingress rule with ip protocol 'http' , port range 80-80, ip range 0.0.0.0/0
       Ingress rule with ip protocol 'https ' , port range 443-443, ip range 0.0.0.0/0
       Ingress rule with ip protocol 'tcp ' , port range 3306-3306, SG group 'SG_web'
       Ingress rule with ip protocol 'tcp ' , port range 22-22, SG group 'SG_man'
       Egress rule with ip protocol 'tcp ' , port range 3306-3306, SG group 'SG_web'
       Egress rule with ip protocol 'tcp ' , port range 22-22, SG group 'SG_man'

    8. Add rules to SG_DNS:
       Ingress rule with ip protocol 'udp ' , port range 53-53, ip-prefix 'ip DNS server'
       Egress rule with ip protocol 'udp ' , port range 53-53, ip-prefix 'ip DNS server'
       Ingress rule with ip protocol 'tcp ' , port range 53-53, ip-prefix 'ip DNS server'
       Egress rule with ip protocol 'tcp ' , port range 53-53, ip-prefix 'ip DNS server'
    9. Add rules to SG_man:
       Ingress rule with ip protocol 'tcp ' , port range 22-22, ip range 0.0.0.0/0
       Egress rule with ip protocol 'tcp ' , port range 22-22, ip range 0.0.0.0/0
    10. Launch following instances in net_1 from image 'ubuntu':
        instance 'webserver' of vcenter az with SG_web, SG_DNS
        instance 'mysqldb ' of vcenter az with SG_db, SG_DNS
        instance 'manage' of nova az with SG_man, SG_DNS

    11. Verify that  traffic is enabled to instance 'webserver' from internet by http port 80.

    12. Verify that  traffic is enabled to instance 'webserver' from VM 'manage' by tcp port 22.
    13. Verify that traffic is enabled to instance 'webserver' from VM 'mysqldb' by tcp port 3306.
    14. Verify that traffic is enabled to internet from instance ' mysqldb' by https port 443.
    15. Verify that traffic is enabled to instance ' mysqldb' from VM 'manage' by tcp port 22.
    16. Verify that traffic is enabled to instance ' manage' from internet by tcp port 22.
    17. Verify that traffic is not enabled to instance ' webserver' from internet by tcp port 22.
    18. Verify that traffic is not enabled to instance ' mysqldb' from internet by tcp port 3306.
    19. Verify that traffic is not enabled to instance 'manage' from internet by http port 80.
    20. Verify that traffic is enabled to all instances from DNS server by udp/tcp port 53 and vice versa.


Expected result
###############

Network traffic is allowed/prohibited to instances according security groups
rules.


Security group rules with remote group id simple.
-------------------------------------------------


ID
##

dvs_remote_sg_simple


Description
###########

Verify that network traffic is allowed/prohibited to instances according security groups
rules.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.
    3. Create security groups:
       SG1
       SG2
    4. Delete all defaults egress rules of SG1 and SG2.
    5. Add icmp rule to SG1:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
    6. Add icmp rule to SG2:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG2'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG2'
    7. Launch 2 instance of vcenter az with SG1 in net1.
       Launch 2 instance of nova az with SG1 in net1.
    8. Launch 2 instance of vcenter az with SG2 in net1.
       Launch 2 instance of nova az with SG2 in net1.
    9. Verify that icmp ping is enabled between VMs from SG1.
    10. Verify that icmp ping is enabled between instances from SG2.
    11. Verify that icmp ping is not enabled between instances from SG1 and VMs from SG2.


Expected result
###############

Network traffic is allowed/prohibited to instances according security groups
rules.


Check attached/detached ports with security groups.
---------------------------------------------------


ID
##

dvs_attached_ports


Description
###########

Check attached/detached ports with security groups.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.
    3. Create security SG1 group with rules:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Ingress rule with ssh protocol 'tcp', port range 22, SG group 'SG1'
       Egress rule with ssh  protocol 'tcp ', port range 22, SG group 'SG1'
    4. Launch few instances with SG1 in net1.
    5. Launch few instances with Default SG in net1.
    6. Verify that icmp/ssh is enabled between instances from SG1.

    7. Verify that  that icmp/ssh isn't allowed to instances of SG1 from instances of Default SG.
    8. Detached ports of all instances from net_1.
    9. Attached ports of all instances to default internal net. For instances of Vcenter to activate new interface on cirros edit the  restart network: "sudo /etc/init.d/S40network restart"
    10. Check that all instances are in Default SG.
    11. Verify that icmp/ssh is enabled between instances.
    12. Change of some instances Default SG to SG1.
    13. Verify that icmp/ssh is enabled between instances from SG1.
    14. Verify that  that icmp/ssh isn't allowed to instances of SG1 from instances of Default SG.


Expected result
###############

Verify that network traffic is allowed/prohibited to instances according security groups
rules.


Check launch and remove instances in the one group simultaneously with few security groups.
-------------------------------------------------------------------------------------------


ID
##

dvs_instances_batch_mix_sg


Description
###########

Check launch and remove instances in the one group simultaneously with few security groups.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.
    2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.

    3. Create security SG1 group with rules:
       Ingress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Egress rule with ip protocol 'icmp ', port range any, SG group 'SG1'
       Ingress rule with ssh protocol 'tcp', port range 22, SG group 'SG1'
       Egress rule with ssh protocol 'tcp ', port range 22, SG group 'SG1'
    4. Create security Sg2 group with rules:
       Ingress rule with ssh protocol 'tcp', port range 22, SG group 'SG2'
       Egress rule with ssh protocol 'tcp ', port range 22, SG group 'SG2'
    5. Launch few instances of vcenter availability zone with Default SG +SG1+SG2  in net1 in one batch.
    6. Launch few instances of nova availability zone with Default SG +SG1+SG2  in net1 in one batch.
    7. Verify that icmp/ssh is enabled between instances.

    8. Remove all instances.
    9. Launch few instances of nova availability zone with Default SG +SG1+SG2  in net1 in one batch.
    10. Launch few instances of vcenter availability zone with Default SG +SG1+SG2  in net1 in one batch.
    11. Verify that icmp/ssh is enabled between instances.


Expected result
###############

Verify that network traffic is allowed/prohibited to instances according security groups
rules.


Security group rules with remote ip prefix.
-------------------------------------------


ID
##

dvs_remote_ip_prefix


Description
###########

Check connection between instances according security group rules with remote ip prefix.


Complexity
##########

core


Steps
#####

    1. Setup for system tests.


    2. Create net_1: net01__subnet, 192.168.1.0/24, and attach it to the router01.
    3. Create instance 'VM1' of vcenter availability zone in the default internal network. Associate floating ip.
    4. Create instance 'VM2' of nova availability zone in the 'net1'network.
    5. Create security groups:
       SG1
       SG2
    6. Delete all defaults egress rules of SG1 and SG2.
    7. Add icmp rule to SG1:
       Ingress rule with ip protocol 'icmp ', port range any, remote ip prefix <floating ip of VM1>
       Egress rule with ip protocol 'icmp ', port range any, remote ip prefix <floating ip of VM1>
    8. Add ssh rule to SG2:
       Ingress rule with ip protocol tcp ', port range any, <internal ip of VM2>
       Egress rule with ip protocol 'tcp ', port range any, <internal ip of VM2>
    9. Launch 2 instance 'VM3' and 'VM4' of vcenter az with SG1 and SG2 in net1.
       Launch 2 instance 'VM5' and 'VM6'  of nova az with SG1 and SG2 in net1.
    10. Verify that icmp ping is enabled from 'VM3',  'VM4' ,  'VM5' and 'VM6'  to VM1 and vice versa.
    11. Verify that icmp ping is blocked between 'VM3',  'VM4' ,  'VM5' and 'VM6' and vice versa.
    12. Verify that ssh is enabled from 'VM3',  'VM4' ,  'VM5' and 'VM6'  to VM2 and vice versa.
    13. Verify that ssh is blocked between 'VM3',  'VM4' ,  'VM5' and 'VM6' and vice versa.


Expected result
###############

Verify that network traffic is allowed/prohibited to instances according security groups
rules.


Fuel create mirror and update core repos on cluster with DVS
------------------------------------------------------------


ID
##

dvs_fuel_crate_mirror


Description
###########

Fuel create mirror and update core repos in custer with DVS plugin+


Complexity
##########

core


Steps
#####

    1. Setup for system tests
    2. Log into controller node via Fuel CLI and get PID of services which were
        launched by plugin and store them.
    3. Launch the following command on the Fuel Master node:
        `fuel-mirror create -P ubuntu -G mos ubuntu`
    4. Run the command below on the Fuel Master node:
        `fuel-mirror apply -P ubuntu -G mos ubuntu --env <env_id> --replace`
    5. Run the command below on the Fuel Master node:
        `fuel --env <env_id> node --node-id <node_ids_separeted_by_coma> --tasks setup_repositories`
        And wait until task is done.
    6. Log into controller node and check plugins services are alive and their PID are changed.
    7. Check all nodes remain in ready status.
    8. Rerun OSTF.


Expected result
###############

Cluster (nodes) should remain in ready state.
OSTF test should be passed on rerun