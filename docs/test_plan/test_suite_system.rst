System
======

Setup of System test
--------------------

**ID**

dvs_setup_system

**Description**
::

 Setup of System test: Deploy environment in DualHypervisors mode with 3 controlers, 1 compute and 1 cinder-vmware nodes. It is mandatory for all system tests.



**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.

 Create a new environment using the Fuel UI Wizard.
 add name of an env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default

 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 set VMware Datastore backend for Glance

 Add nodes:
 3 controller
 2 compute

 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed)
 eth4 – storage

 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway '10.109.1.1'
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR '10.109.4.0/24'
 Vlan tag is not set-Management: CIDR '10.109.2.0/24'
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default

 Verify networks.

 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: <login>
 vCenter password: <password>

 Add 2 vSphera Clusters:
 vSphera Cluster: Cluster1
 Service name: vmcluster1
 Datastore regex:.*
 vSphera Cluster: Cluster2
 Service name: vmcluster2
 Datastore regex: .*

 Deploy cluster
 Run OSTF
 Cluster should be deployed and all OSTF test cases should be passed.

Check abilities to create and terminate networks on DVS.
--------------------------------------------------------

**ID**

dvs_create_terminate_networks

**Description**
::

 Check abilities to create and terminate networks on DVS.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests.
 Log in to Horizon Dashboard.
 Add private networks net_01 and net_02.
 Check that networks are present in the vSphera.
 Remove private network net_01.
 Check that network net_01 is not present in the vSphere.
 Add private network net_01.Networks  net_01 and  net_02 should be added.
 Check that networks is  present in the vSphere.
 Networks  net_01 and  net_02 should present in the vSphere.

Check abilities to assign multiple vNIC to a single VM.
-------------------------------------------------------

**ID**

dvs_assign_multiple_vNIC_to_single_VM

**Description**
::

 Check abilities to assign multiple vNIC to a single VM.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Log in to Horizon Dashboard.
 Add two private networks (net01, and net02).
 Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
 Launch instance VM_1 with image TestVM and flavor m1.micro in nova az.
 Launch instance VM_2  with image TestVM-VMDK and flavor m1.micro vcenter az.
 Check abilities to assign multiple vNIC net01 and net02 to VM_1 .
 Check abilities to assign multiple vNIC net01 and net02 to VM_2 .
 Send icmp ping from VM _1 to VM_2  and vice versa.
 VM_1 and VM_2 should be attached to multiple vNIC net01 and net02. Pings should get a response.

Check connection between VMs in one default tenant.
---------------------------------------------------

**ID**

dvs_connection_between_VMs_in_one_default_tenant

**Description**
::

 Check connection between VMs in one default tenant.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Navigate to Project ->  Compute -> Instances

 Launch instance VM_1 with image TestVM and flavor m1.micro in nova availability zone.
 Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter availability zone.
 Verify that VM_1 and VM_2 on different hypervisors  should communicate between each other. Send icmp ping from VM_1 of vCenter to VM_2 from Qemu/KVM and vice versa.
 Pings should get a response.

Check connection between VMs in one non default tenant.
-------------------------------------------------------

**ID**

dvs_connection_between_VMs_in_one_tenant

**Description**
::

 Check connection between VMs in one tenant.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Log in to Horizon Dashboard.
 Create tenant net_01 with subnet.
 Navigate to Project ->  Compute -> Instances
 Launch instance VM_1 with image TestVM and flavor m1.micro in nova availability zone. in net_01
 Launch instance VM_2 with image TestVM-VMDK and flavor m1.micro in vcenter availability zone in net_01
 Verify that VMs on same tenants should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.
 Pings should get a response

Check connectivity between VMs attached to different networks with and within a router between them.
----------------------------------------------------------------------------------------------------

**ID**

dvs_connectivity_between_vms_different_networks

**Description**
::

 Check connectivity between VMs attached to different networks with and within a router between them.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Log in to Horizon Dashboard.
 Add two private networks (net01, and net02).
 Add one  subnet (net01_subnet01: 192.168.101.0/24, net02_subnet01, 192.168.102.0/24) to each network.
 Navigate to Project ->  Compute -> Instances
 Launch instances VM_1 and VM_2 in the network192.168.101.0/24 with image TestVM and flavor m1.micro in nova az.
 Launch instances VM_3 and VM_4 in the 192.168.102.0/24 with image TestVM-VMDK and flavor m1.micro in vcenter az.
 Verify that VMs of  same networks should communicate
 between each other. Send icmp ping from VM _1  to VM_2,  VM _3  to VM_4 and vice versa.
 Verify that VMs of  different networks should not communicate
 between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2  and vice versa.
 Create Router_01, set gateway and add interface to external network.
 Attach private networks to Router_01.
 Verify that VMs of  different networks should communicate
 between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2)  and vice versa. Pings should get a response.
 Add new Router_02, set gateway and add interface to external network.
 Deatach net_02 from Router_01 and attache to Router_02
 Verify that VMs of different networks should not communicate
 between each other. Send icmp ping from VM _1  to VM_3, VM_4 to VM_2  and vice versa.

Check isolation between VMs in different tenants.
-------------------------------------------------

**ID**

dvs_no_connectivity_between_Vms_different_tenants

**Description**
::

 Check isolation between VMs in different tenants.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Log in to Horizon Dashboard.
 Create non-admin tenant.
 Navigate to Identity -> Projects.
 Click on Create Project.
 Type name test_tenant.
 On tab Project Members add admin with admin and member
 Navigate to Project -> Network -> Networks
 Create network  with  subnet.
 Navigate to Project ->  Compute -> Instances
 Launch instance VM_1
 Navigate to test_tenant
 Navigate to Project -> Network -> Networks
 Create network  with subnet.
 Create Router, set gateway and add interface
 Navigate to Project ->  Compute -> Instances
 Launch instance VM_2
 Verify that VMs on different tenants should not communicate
 between each other. Send icmp ping from VM _1 of admin tenant to VM_2  of test_tenant and vice versa.
 Pings should not get a response.

Check connectivity Vms to public network without floating ip
------------------------------------------------------------

**ID**

dvs_connectivity_vms_to_public_net_without_floating_ip

**Description**
::

 Check connectivity Vms to public network without floating ip.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests.
 Log in to Horizon Dashboard.
 Create net01: net01__subnet, 192.168.112.0/24 and attach it to the router04
 Launch instance VM_1 of nova AZ with image TestVM and flavor m1.micro in the net_04.
 Launch instance VM_1 of vcenter AZ with image TestVM-VMDK and flavor m1.micro in the net_01.
 Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.
 Pings should  get a response

Check abilities to create and delete security group.
----------------------------------------------------

**ID**

dvs_create_delete_security_group

**Description**
::

 Check abilities to create and delete security group.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Log in to Horizon Dashboard.

 Launch instance VM_1 in the tenant network net_02 with image TestVM and flavor m1.micro in the nova availability zone.
 Launch instance VM_2  in the tenant net_02  with image TestVM-VMDK and flavor m1.micro in the vcenter availability zone.
 Create security groups SG_1 to allow ICMP traffic.
 Add Ingress rule for ICMP protocol to SG_1
 Attach SG_1 to VMs
 Check ping between VM_1 and VM_2 and vice verse
 Create security groups SG_2 to allow TCP traffic 80 port.
 Add Ingress rule for TCP protocol to SG_2

 Attach SG_2 to VMs
 SSh from VM_1 to VM_2 and vice verse
 Delete all rules from SG_1 and SG_2
 Check that ping and ssh aren’t available from VM_1 to VM_2  and vice verse
 Add Ingress rule for ICMP protocol to SG_1
 Add Ingress rule for TCP protocol to SG_2
 Check ping between VM_1 and VM_2 and vice verse
 Check SSh from VM_1 to VM_2 and vice verse
 Delete security group.
 Attach Vms to default security group.
 Check ping between VM_1 and VM_2 and vice verse
 Check SSh from VM_1 to VM_2 and vice verse
 We should have the ability to send ICMP and TCP traffic between VMs in different tenants.

Verify that only the associated MAC and IP addresses can communicate on the logical port.
-----------------------------------------------------------------------------------------

**ID**

dvs_port_security_group

**Description**
::

 Verify that only the associated MAC and IP addresses can communicate on the logical port.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests.
 Log in to Horizon Dashboard.
 Launch 2 instances on each of hypervisors.
 Verify that traffic can be successfully sent from and received on the MAC and IP address associated with the logical port.
 Configure a new IP address on the instance associated with the logical port.
 Confirm that the instance cannot communicate with that IP address.
 Configure a new MAC address on the instance associated with the logical port.
 Confirm that the instance cannot communicate with that MAC address and the original IP address.
 Instance should not communicate with new ip and mac addresses but it should communicate with old IP.

Check connectivity Vms to public network with floating ip.
----------------------------------------------------------

**ID**

dvs_connectivity_vms_to_public_net_with_floating_ip

**Description**
::

 Check connectivity Vms to public network with floating ip.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Log in to Horizon Dashboard.
 Create net01: net01__subnet, 192.168.112.0/24 and attach it to the router04
 Launch instance VM_1 of nova AZ with image TestVM and flavor m1.micro in the net_04. Associate floating ip.
 Launch instance VM_1 of vcenter AZ with image TestVM-VMDK and flavor m1.micro in the net_01. Associate floating ip.
 Send ping from instances VM_1 and VM_2 to 8.8.8.8 or other outside ip.

Check connectivity between VMs with same ip in different tenants.
-----------------------------------------------------------------

**ID**

dvs_connectivity_between_Vms_in_different_tenants

**Description**
::

 Check connectivity between VMs with same ip in different tenants.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests
 Log in to Horizon Dashboard.
 Create 2 non-admin tenants ‘test_1’ and ‘test_2’.
 Navigate to Identity -> Projects.
 Click on Create Project.
 Type name ‘test_1’ of tenant.
 Click on Create Project.
 Type name ‘test_2’ of tenant.
 On tab Project Members add admin with admin and member.
 In tenant ‘test_1’  create net1 and subnet1 with CIDR 10.0.0.0/24
 In tenant ‘test_1’  create security group ‘SG_1’ and add rule that allows ingress icmp traffic
 In tenant ‘test_2’  create net2 and subnet2 with CIDR 10.0.0.0/24
 In tenant ‘test_2’ create security group ‘SG_2’
  In tenant ‘test_1’  add  VM_1 of vcenter  in net1 with ip 10.0.0.4 and  ‘SG_1’ as security group.
 In tenant ‘test_1’  add  VM_2 of nova  in net1 with ip 10.0.0.5 and  ‘SG_1’ as security group.
 In tenant ‘test_2’  create net1 and subnet1 with CIDR 10.0.0.0/24
 In tenant ‘test_2’  create security group ‘SG_1’ and add rule that allows ingress icmp traffic
 In tenant ‘test_2’  add  VM_3 of nova  in net1 with ip 10.0.0.4 and  ‘SG_1’ as security group.
 In tenant ‘test_2’  add  VM_4 of  vcenter in net1 with ip 10.0.0.5 and  ‘SG_1’ as security group.
 Verify that VMs with same ip on different tenants should communicate
 between each other. Send icmp ping from VM _1 to VM_3,  VM_2 to Vm_4 and vice versa.
 Pings should  get a response.

Check creation instance in the one group simultaneously.
--------------------------------------------------------

**ID**

dvs_vcenter_10_instances

**Description**
::

 TO DO

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Setup for system tests.
 Navigate to Project -> Compute -> Instances
 Launch 10 instance VM_1 simultaneously with image TestVM and flavor m1.micro in nova az in default net_04
 All instance should be created without any error.
 Launch 10 instance VM_2 simultaneously with image TestVM-VMDK and flavor m1.micro in vcenter az in default net_04
 All instance should be created without any error.
 Check connection between VMs(ping, ssh)
 Delete all Vms from horizon simultaneously.

Check that we can create volumes and launch instances from different availability zones, which have different types of hypervisors
----------------------------------------------------------------------------------------------------------------------------------

**ID**

dvs_vcenter_volume

**Description**
::

 TO DO

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Create a new environment using the Fuel UI Wizard.
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by defaultEach volume should be attached to his instance
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 Add nodes:
 1 controller
 1 compute
 1 cinder
 1cinder-vmware
 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed) ID:103
 eth4 – storage
 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway '10.109.1.1'
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR '10.109.4.0/24'
 Vlan tag is not set-Managment: CIDR '10.109.2.0/24'
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default

 Verify networks.

 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: <login>
 vCenter password: <password>

 Add 2 vSphera Clusters:
 vSphera Cluster: Cluster1
 Service name: vmcluster1
 Datastore regex:.*
 vSphera Cluster: Cluster2
 Service name: vmcluster2
 Datastore regex: .*
 Deploy cluster
 Run OSTF
 Create 2 volumes each in his own availability zone
 Launch instances from volume

Check abilities to update network name
--------------------------------------

**ID**

dvs_update_network

**Description**
::

 Check abilities to update network name

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Log in Horizon
 Create network net_1
 Update network name net_1 to net_2
 Update default network name net04 to net4

Check abilities to stack heat from template.
--------------------------------------------

**ID**

dvs_vcenter_heat

**Description**
::

 Check abilities to stack heat from template.

**Complexity**

core

**Require to automate**

Yes

**Steps**
::

 Create stack with heat template
 heat_template_version: 2013-05-23
