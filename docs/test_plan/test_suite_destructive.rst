Destructive tests
=================

Check abilities to bind port on DVS to VM, disable and enable this port.
------------------------------------------------------------------------

**ID**

dvs_enable_disable_port_on_dvs_to_vm

**Description**
::

 Check abilities to bind port on DVS to VM, disable and enable this port.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Setup for system tests.
 Log in to Horizon Dashboard.
 Navigate to Project ->  Compute -> Instances
 Launch instance VM_1 with image TestVMDK and flavor m1.micro.
 Launch instance VM_2  with image TestVMDK and flavor m1.micro.
 Verify that VMs  should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.
 Disable dvs_port of VM_1.
 Verify that VMs  should not communicate between each other. Send icmp ping from VM _2 to VM_1  and vice versa.
 Enable dvs_port of VM_1.
 Verify that VMs  should communicate between each other. Send icmp ping from VM _1 to VM_2  and vice versa.Pings should get a response

Verify that vmclusters should be migrate after shutdown controller.
-------------------------------------------------------------------

**ID**

dvs_shutdown_controller

**Description**
::

 Verify that vmclusters should be migrate after shutdown controller.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
  network setup : Neutron with Vlan segmentation.
  storage backends: default
 additional services: all by default
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 Add nodes:
 3 controllers
 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed)
 eth4 – storage

 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway 10.109.1.1
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR 10.109.4.0/24
 Vlan tag is not set
 Managment: CIDR 10.109.2.0/24
 Vlan tag is not set
 Neutron L2 configuration by default

 Neutron L3 configuration by default
 Click button 'save settings'
 Click button 'verify networks'

 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: administrator@vsphere.local
 vCenter password: Qwer!1234
 Add 2 vSphera Clusters:
 vSphera Cluster: Cluster1
 Service name: vmcluster1
 Datastore regex:.*
 vSphera Cluster: Cluster2
 Service name: vmcluster2
 Datastore regex: .*

 Deploy Cluster
 Run OSTF
 Shutdown controller with  vmclusters.
 Check that vmclusters should be migrate to another controller.Vmclusters should be migrate to another controller.

Deploy cluster with plugin, addition and deletion of nodes.
-----------------------------------------------------------

**ID**

dvs_vcenter_add_delete_nodes

**Description**
::

 Deploy cluster with plugin, addition and deletion of nodes.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
  as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select Vmware vcenter esxi datastore for images (glance)

 Add nodes:
 3 controllers
 2 computers
 1 cinder-vmdk
 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed)
 eth4 – storage

 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway 10.109.1.1
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR 10.109.4.0/24
 Vlan tag is not set
 Management: CIDR 10.109.2.0/24
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default
 Verify networks
 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: administrator@vsphere.local
 vCenter password: Qwer!1234

 Add 2 vSphera Clusters:
 vSphera Cluster: Cluster1
  Service name: vmcluster1
 Datastore regex:.*
 vSphera Cluster: Cluster2
 Service name: vmcluster2
 Datastore regex: .*

 Run OSTF
 Remove node with cinder-vmdk role.
 Add node with cinder role.
 Redeploy cluster.
  Run OSTF
 Remove node with compute role
 Add node with cinder-vmdk  role
 Redeploy cluster.
 Run OSTFCluster should be deployed and all OSTF test cases should be passed.

Deploy cluster with plugin and deletion one node with controller role.
----------------------------------------------------------------------

**ID**

dvs_vcenter_remove_controller

**Description**
::

 Deploy cluster with plugin and deletion one node with controller role.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
  as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select Vmware vcenter esxi datastore for images (glance)
 Add nodes:
 4 controller
 1 computer
 1 cinder-vmdk
 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed)
 eth4 – storage

 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway 10.109.1.1
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR 10.109.4.0/24
 Vlan tag is not set
 Management: CIDR 10.109.2.0/24
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default

 Verify networks
 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: administrator@vsphere.local
 vCenter password: Qwer!1234
 Add 2 vSphera Clusters:
 vSphera Cluster: Cluster1
  Service name: vmcluster1
 Datastore regex:.*
 vSphera Cluster: Cluster2
 Service name: vmcluster2
 Datastore regex: .*
 Run OSTF
 Remove node with controller role.
 Redeploy cluster
 Run OSTF
 Add controller
 Redeploy cluster
 Run OSTFCluster should be deployed and all OSTF test cases should be passed.

Verify that it is not possibility to uninstall of Fuel DVS plugin with deployed environment.
--------------------------------------------------------------------------------------------

**ID**

dvs_uninstall_negative

**Description**
::

 Verify that it is not possibility to uninstall of Fuel DVS plugin with deployed environment.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Copy plugin to to the Fuel master node using scp.
 Install plugin
 fuel plugins --install plugin-name-1.0-0.0.1-0.noarch.rpm
 Ensure that plugin is installed successfully using cli, run command 'fuel plugins'.
 Connect to the Fuel web UI.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and Qemu radio button
  network setup : Neutron with Vlan segmentation
  storage backends: default
 additional services: all by default
 Click on the Settings tab.
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 Add nodes:
 1 controller
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
 vCenter username: administrator@vsphere.local
 vCenter password: Qwer!1234

 Add 2 vSphera Clusters:
 vSphera Cluster: Cluster1
 Service name: vmcluster1
 Datastore regex:.*

 Deploy cluster
 Run OSTF
 Try to delete plugin via cli Remove plugin from master node  fuel plugins --remove plugin-name==1.0.0Alert: "400 Client Error: Bad Request (Can't delete plugin which is enabled for some environment.)" should be displayed.

Check cluster functionality after reboot vcenter.
-------------------------------------------------

**ID**

dvs_vcenter_reboot_vcenter

**Description**
::

 Check cluster functionality after reboot vcenter.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
  as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default

 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select Vmware vcenter esxi datastore for images (glance)

 Add nodes:
 1 controller
 1 computer
 1 cinder-vmdk
 1 cinder

 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed)
 eth4 – storage
 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway 10.109.1.1
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR 10.109.4.0/24
 Vlan tag is not set
 Management: CIDR 10.109.2.0/24
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default

 Verify networks
 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: administrator@vsphere.local
 vCenter password: Qwer!1234
 Add Nova Compute Instance:
             Cluster: ‘Cluster1’
             Service name: any
             Datastore regex: .*
             Target node: controllers
 Run OSTF

 Launch instance VM_1 with image TestVMDK and flavor m1.micro.

 Launch instance VM_2  with image TestVMDK and flavor m1.micro.
 Check connection between VMs, send ping from VM_1 to VM_2 and vice verse.
 Reboot vcenter
 Check that controller lost connection with vCenter
 Wait for vCenter
 Ensure that all instances from vCenter displayed in dashboard.
 Ensure connectivity between Nova's and VMware's VM.
 Run OSTFCluster should be deployed and all OSTF test cases should be passed. ping shoul get response.

dvs_vcenter_reboot_vcenter_2
----------------------------

**ID**

dvs_vcenter_reboot_vcenter_2

**Description**
::

 TO DO

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
  as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default

 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select Vmware vcenter esxi datastore for images (glance)

 Add nodes:
 1 controller
 1 computer
 1 ComputeVMware
 1 cinder-vmdk
 1 cinder

 Interfaces on slaves should be setup this way in Fuel interface:
 eth0 - admin(PXE)
 eth1 - public
 eth2 - management
 eth3 - VM(Fixed)
 eth4 – storage
 Networks tab:
 Public network: start'10.109.1.2' end '10.109.1.127'
 CIDR '10.109.1.0/24'
 Gateway 10.109.1.1
 Floating ip range start'10.109.1.128' end '10.109.1.254'
 Storage: CIDR 10.109.4.0/24
 Vlan tag is not set
 Management: CIDR 10.109.2.0/24
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default

 Verify networks
 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: administrator@vsphere.local
 vCenter password: Qwer!1234
 Add Nova Compute Instance:
             Cluster: ‘Cluster1’
             Service name: any
             Datastore regex: .*
             Target node:ComputeVMware
 Run OSTF
 Launch instance VM_1 with image TestVMDK and flavor m1.micro.
 Launch instance VM_2  with image TestVMDK and flavor m1.micro.

 Check connection between VMs, send ping from VM_1 to VM_2 and vice verse.

 Reboot vcenter
 Check that ComputeVMware lost connection with vCenter

 Wait for vCenter
 Ensure that all instances from vCenter displayed in dashboard.
 Ensure connectivity between Nova's and VMware's VM.
 Run OSTFCluster should be deployed and all OSTF test cases should be passed. pings shoul get response.

