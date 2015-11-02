
Integration
===========

Deploy  HA cluster with Fuel DVS plugin.
----------------------------------------

**ID**

dvs_vcenter_ha_mode

**Description**
::

 Deploy  HA cluster with Fuel DVS plugin.

**Complexity**

core

**Requre to automate**

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
 Cluster should be deployed and all OSTF test cases should be passed.

Deploy cluster with Fuel DVS plugin and Ceph for Glance and Cinder.
-------------------------------------------------------------------

**ID**

dvs_vcenter_ceph

**Description**
::

 Deploy cluster with Fuel DVS plugin and Ceph for Glance and Cinder.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Create a new environment using the Fuel UI Wizard.
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
  network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default
 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select 'Ceph RBD for volumes'  (Cinder)  and  'Ceph RBD for images(Glance)'
 Add nodes:
 3 controller
 1 cinder-vmdk + ceph-osd
 1 compute  + ceph-osd

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

Deploy cluster with plugin on Fuel 6.1 and upgrade to Fuel 7.0.
---------------------------------------------------------------

**ID**

dvs_vcenter_upgrade

**Description**
::

 Deploy cluster with plugin on Fuel 6.1 and upgrade to Fuel 7.0.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install plugin on master node.
 Create a new environment using the Fuel UI Wizard:
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
  network setup : Neutron with Vlan segmentation.
 storage backends:  by default
 additional services: all by default
 Enable DVS plugin in the Setting Tab.
 set dvSwitch name
 Add nodes:
 1 controller
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
 Managment: CIDR 10.109.2.0/24
 Vlan tag is not set
 Neutron L2 configuration by default
 Neutron L3 configuration by default
 Verify Networks.
 Fill vcenter credentials:
 Availability zone: vcenter
 vCenter host: '172.16.0.254'
 vCenter username: <login>
 vCenter password: <password>
 Add 1 vSphera Clusters:
 vSphera Cluster: Cluster1
 Service name: vmcluster1
 Datastore regex:.*

 Deploy cluster
 Run OSTF
 Upgrade Fuel from 6.1 to 7.0:
 Upload upgrade script to master to /var section
 Untar script and run ./upgrade.sh
 Run OSTF
 Cluster should be deployed and all OSTF test cases should be passed.

Deploy cluster with Fuel VMware DVS plugin and ceilometer.
----------------------------------------------------------

**ID**

dvs_vcenter_ceilometer

**Description**
::

 Deploy cluster with Fuel VMware DVS plugin and ceilometer.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install DVS plugin on master node.
 Create a new environment using the Fuel UI Wizard.
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
  network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: install  ceilometer

 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 Add nodes:
 3 controller + mongo
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

 Add 1 vSphera Clusters:
 vSphera Cluster: Cluster1
 Service name: vmcluster1
 Datastore regex:.*

 Deploy cluster
 Run OSTF
 Cluster should be deployed and all OSTF test cases should be passed.

Deploy cluster with Fuel VMware DVS plugin, Ceph for Cinder and VMware datastore backend for Glance.
----------------------------------------------------------------------------------------------------

**ID**

dvs_vcenter_multiroles

**Description**
::

 Deploy cluster with Fuel VMware DVS plugin, Ceph for Cinder and VMware datastore backend for Glance.

**Complexity**

core

**Requre to automate**

Yes

**Steps**
::

 Install plugin on master node.


 Create a new environment using the Fuel UI Wizard.
 add name of env and select release version with OS
 as hypervisor type: select vcenter check box and QEMU/KVM radio button
 network setup : Neutron with Vlan segmentation.
 storage backends: default
 additional services: all by default

 In Settings tab:
 enable DVS plugin
 set dvSwitch name
 select 'Ceph RBD for volumes' (Cinder) and 'Vmware Datastore for images(Glance)'
 Add nodes:
 3 controller + ceph-osd
 2 cinder-vmdk + compute

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

