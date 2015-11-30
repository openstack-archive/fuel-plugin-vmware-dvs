Smoke
=====

Verify that Fuel VMware DVS plugin is installed.
------------------------------------------------

**ID**

dvs_install

**Description**
::

 Verify that Fuel VMware DVS plugin is installed.

**Complexity**

smoke

**Require to automate**

Yes

**Steps**
::

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
 Click on the Settings tab and check that section of  DVS  plugin is displayed with all required GUI elements.Section of  DVS  plugin is displayed with all required GUI elements.

Verify that Fuel VMware DVS plugin  is uninstalled.
---------------------------------------------------

**ID**

dvs_uninstall

**Description**
::

 Verify that Fuel VMware DVS plugin  is uninstalled.

**Complexity**

smoke

**Require to automate**

Yes

**Steps**
::

 Remove plugin from master node  fuel plugins --remove plugin-name==1.0.0
 Verify that plugin is removed, run command 'fuel plugins'.
 Connect to the Fuel web UI.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
  as hypervisor type: select vcenter check box and Qemu radio button
 network setup : Neutron with Vlan segmentation.
  storage backhands: default
 additional services: all by default
 Click on the Settings tab and check that section of  DVS  plugin is not displayedSection of  DVS  plugin is not displayed.

Deploy cluster with plugin and vmware datastore backend.
--------------------------------------------------------

**ID**

dvs_vcenter_smoke

**Description**
::

 Deploy cluster with plugin and vmware datastore backend.

**Complexity**

smoke

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
 additional services: all by default
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select Vmware vcenter esxi datastore for images (glance)
 Add nodes:
 1 controller
 1 compute
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

 Fill Glance credentials:
 vCenter host: 172.16.0.254
 vCenter username: <login>
 vCenter password: <password>
 Datacenter name: Datacenter
 Datastore name: nfs

 Deploy cluster
 Run OSTF

