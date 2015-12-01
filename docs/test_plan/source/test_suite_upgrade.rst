Upgrade
=======


Deploy cluster with plugin on Fuel 8.0 and upgrade to Fuel 9.0.
---------------------------------------------------------------


ID
##

dvs_vcenter_upgrade


Description
###########

Deploy cluster with plugin on Fuel 8.0 and upgrade to Fuel 9.0.


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

