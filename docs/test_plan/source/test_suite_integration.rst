Integration
===========


Deploy HA cluster with Fuel DVS plugin.
---------------------------------------


ID
##

dvs_vcenter_ha_mode


Description
###########

Deploy  HA cluster with Fuel DVS plugin.


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
        * Controller
        * Controller
        * Compute
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin and Ceph for Glance and Cinder.
----------------------------------------------------------


ID
##

dvs_vcenter_ceph


Description
###########

Deploy cluster with Fuel DVS plugin and Ceph for Glance and Cinder.


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
        * Controller
        * Controller
        * Compute + CephOSD
        * CinderVMware + CephOSD
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
       select 'Ceph RBD for volumes'  (Cinder)  and  'Ceph RBD for images(Glance)'
    7. Configure settings:
       Enable Ceph RBD for volumes (Cinder)
       Enable Ceph RBD for images (Glance)
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Verify networks.
    10. Deploy cluster.
    11. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin ComputeVMware, Ceph for Glance and Cinder.
---------------------------------------------------------------------


ID
##

dvs_vcenter_ceph_2


Description
###########

Deploy cluster with Fuel DVS plugin with Compute-VMware and Ceph for Glance and Cinder.


Complexity
##########

core


Steps
#####

    1. Connect to a Fuel web UI with preinstalled plugin.
    2. Create a new environment with following parameters:
       Compute: KVM/QEMU with vCenter
       Networking: Neutron with VLAN segmentation
       Storage: default
       Additional services: default
    3. Add nodes with following roles:
        * Controller
        * Compute
        * ComputeVMware
        * CephOSD
        * CephOSD
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin and ceilometer.
------------------------------------------


ID
##

dvs_vcenter_ceilometer


Description
###########

Deploy cluster with Fuel VMware DVS plugin and ceilometer.


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
        * Additional services: Ceilometer
    3. Add nodes with following roles:
        * Controller + Mongo
        * Controller + Mongo
        * Controller + Mongo
        * Compute
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    8. Verify networks.
    9. Deploy cluster
    10. Run OSTF


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin, ComputeVMware and ceilometer.
---------------------------------------------------------


ID
##

dvs_vcenter_ceilometer_2


Description
###########

Deploy cluster with Fuel VMware DVS plugin, Compute-VMware and ceilometer.


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
        * Additional services: Ceilometer
    3. Add nodes with following roles:
        * Controller
        * Compute + Cinder
        * CinderVMware
        * ComputeVMware
        * Mongo
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    8. Verify networks.
    9. Deploy cluster.
    10. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin, Ceph for Cinder and VMware datastore backend for Glance.
------------------------------------------------------------------------------------


ID
##

dvs_vcenter_multiroles_ceph


Description
###########

Deploy cluster with Fuel VMware DVS plugin, Ceph for Cinder and VMware datastore backend for Glance.


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
        * Controller + CephOSD
        * Controller + CephOSD
        * Controller + CephOSD
        * Compute + CinderVMware
        * Compute + CinderVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure settings:
       Enable Ceph RBD for volumes (Cinder)
       Enable VMWare vCenter/ESXi datastore for images (Glance).
    8. Configure VMware vCenter Settings. Add 2 vSphere clusters and configure Nova Compute instances on conrollers.
    9. Configure Glance credentials on VMware tab.
    10. Verify networks.
    11. Deploy cluster.
    12. Run OSTF.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin, Ceph, Ceilometer and VMware datastore backend for Glance.
-------------------------------------------------------------------------------------


ID
##

dvs_vcenter_multiroles_ceilometer


Description
###########

Deploy cluster with plugin and check multiroles with Ceph and Mongo.


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
        * Additional services: Ceilometer
    3. Add nodes with following roles:
        * Controller + Mongo + CinderVMware
        * Compute + CephOSD
        * CinderVMware + CephOSD
        * ComputeVMware
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


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.


Deploy cluster with plugin on Fuel 7.0 and upgrade to Fuel 8.0.
---------------------------------------------------------------


ID
##

dvs_vcenter_upgrade


Description
###########

Deploy cluster with plugin on Fuel 7.0 and upgrade to Fuel 8.0.


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
        * CinderVMware
        * Cinder
        * ComputeVMware
    4. Configure interfaces on nodes.
    5. Configure network settings.
    6. Enable and configure DVS plugin.
    7. Configure VMware vCenter Settings. Add 1 vSphere clusters and configure Nova Compute instances on compute-vmware.
    8. Verify Networks.
    9. Deploy cluster.
    10. Run OSTF.
    11. Upgrade fuel node:
         * Upload upgrade script to master node in /var folder
         * Untar script and run ./upgrade.sh
    12. Check that all containers and version of iso were upgraded (docker ps).
    13. Check that previously created environment is present.
    14. Run OSTF tests again.


Expected result
###############

Cluster should be deployed and all OSTF test cases should be passed.
