IPv6
====

Check abilities to create and terminate IPv6 networks on DVS.
-------------------------------------------------------------


ID
##

dvs_vcenter_networks_ipv6


Description
###########

Check abilities to create and terminate IPv6 networks on DVS.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Log in to Horizon Dashboard.
    3. Add private IPv6 networks net_01 and net_02.
    4. Check networks are present in the vSphere.
    5. Remove private network net_01.
    6. Check network net_01 is not present in the vSphere.
    7. Add private IPv6 network net_01.
    8. Check networks is present in the vSphere.


Expected result
###############

Networks were successfully created and presented in Horizon and vSphere.



Check abilities to enable/disable interfaces on instances with IPv6 network.
----------------------------------------------------------------------------


ID
##

dvs_vcenter_bind_port_ipv6


Description
###########

Check abilities to enable/disable interfaces on instances with IPv6 network.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Log in to Horizon Dashboard.
    3. Navigate to Project -> Compute -> Instances
    4. Create network net_1, subnet_1: FD12::/64
    5. Launch instance VM_1 with image supported ipv6, availability zone nova, net_1 and flavor m1.micro.
    6. Launch instance VM_2 with vmdk image supported ipv6, availability zone  vcenter, net_1 and flavor m1.micro.
    7. Verify instance communicate between each other. Send icmpv6 ping from VM_1 to VM_2 and vice versa.
    8. Disable interface of VM_1.
    9. Verify instances don't communicate between each other. Send icmpv6 ping from VM_2 to VM_1 and vice versa.
    10. Enable interface of VM_1.
    11. Verify instance communicate between each other. Send icmpv6 ping from VM_1 to VM_2 and vice versa.


Expected result
###############

We can enable/disable interfaces of instances via Horizon.



Check abilities to assign multiple vNICeith ipv6 to a single instance.
----------------------------------------------------------------------


ID
##

dvs_multi_vnic_ipv6


Description
###########

Check abilities to assign multiple vNIC with ipv6 to a single instance.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Log in to Horizon Dashboard.
    3. Add two private networks (net01, and net02).
    4. Add one subnet (net01_subnet01: FD11::/64, net02_subnet01, FD12::/64) to each network.
    5. Launch instance VM_1 with image supported ipv6 and flavor m1.micro in nova availability zone.
    6. Launch instance VM_2 with vmdk image supported ipv6 and flavor m1.micro vcenter availability zone.
    7. Check abilities to assign multiple vNIC net01 and net02 to VM_1.
    8. Check abilities to assign multiple vNIC net01 and net02 to VM_2.
    9. Check both interfaces on each instance have an IP address.
    10. Send icmpv6 ping from VM_1 to VM_2 and vice versa.


Expected result
###############

VM_1 and VM_2 should be attached to multiple vNIC net01 and net02. Pings should get a response.



Check connection between instances in one non default ipv6 network.
-------------------------------------------------------------------


ID
##

dvs_connect_nodefault_net_ipv6


Description
###########

Check connection between instances in one non default ipv6 network.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Log in to Horizon Dashboard.
    3. Create network net_01 with ipv6 subnet FD11::/64.
    4. Navigate to Project -> Compute -> Instances
    5. Launch instance VM_1 with image supported ipv6 and flavor m1.micro in nova availability zone in net_01
    6. Launch instance VM_2 with vmdk image supported ipv6 and flavor m1.micro in vcenter availability zone in net_01
    7. Verify instances in same network communicate between each other. Send icmpv6 ping from VM_1 to VM_2 and vice versa.


Expected result
###############

Pings should get a response.


Check connectivity between instances attached to different ipv6 networks with and within a router between them.
---------------------------------------------------------------------------------------------------------------


ID
##

dvs_different_networks_ipv6


Description
###########

Check connectivity between instances attached to different ipv6 networks with and within a router between them.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create private networks net01 and net02 with ipv6 subnets.
    3. Create Router_01, set gateway and add interface to external network.
    4. Create Router_02, set gateway and add interface to external network.
    5. Attach private networks to Router_01.
    6. Attach private networks to Router_02.
    7. Launch instance in the net01 with image supported ipv6 and flavor m1.micro in nova az.
    8. Launch instance in the net01 with vmdk image supported ipv6 and flavor m1.micro in vcenter az.
    9. Launch instance in the net02 with image supported ipv6 and flavor m1.micro in nova az.
    10. Launch instance in the net02 with vmdk image supported ipv6 and flavor m1.micro in vcenter az.
    11. Verify instances of same networks communicate between each other via private ip.
         Send icmpv6 ping between instances.
    12. Verify instances of different networks don't communicate between each other via private ip.
    13. Delete net_02 from Router_02 and add it to the Router_01.
    14. Verify instances of different networks communicate between each other via private ip.
         Send icmpv6 ping between instances.


Expected result
###############

Network connectivity must conform to each of the scenarios.



Check attach/detach ports with security groups for ipv6.
--------------------------------------------------------


ID
##

dvs_attached_ports_ipv6


Description
###########

Check attach/detach ports with security groups for ipv6.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create net_1: net01__subnet, FD11::/64, and attach it to the default router.
    3. Create security SG1 group with rules:
       Rule: ALL ICMP
         Direction: Ingress
         Remote: Security Group
         Security Group: SG1
       Rule: ALL ICMP
         Direction: Egress
         Remote: Security Group
         Security Group: SG1
       Rule: SSH
         Remote: Security Group
         Security Group: SG1
    4. Launch 4 instances with Default SG in net1.
    5. Attach SG1 to 2 launched instances and detach default sg.
    6. Verify icmp/ssh is allowed between instances from SG1.
    7. Verify icmp/ssh is denied to instances of SG1 from instances of Default SG.
    8. Detach ports of all instances from net_1.
    9. Attach ports of all instances to net_1.
    10. Check all instances are in Default SG.
    11. Verify icmp/ssh is allowed between instances.
    12. Change of some instances Default SG to SG1.
    13. Verify icmp/ssh is allowed between instances from SG1.
    14. Verify icmp/ssh is denied to instances of SG1 from instances of Default SG.


Expected result
###############

Verify network traffic is allowed/denied to instances according security groups
rules.



Check dualstack instance creation with ipv6 slaac
-------------------------------------------------


ID
##

dvs_dualstack_ipv6_slaac


Description
###########

Check dualstack instance creation with ipv6 slaac


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing network:
       network name: net_1
       subnet_v6: FD11::/64, ipv6_address_mode: SLAAC
       subnet_v4: 192.168.0.0/24, DNS: 8.8.8.8, 8.8.4.4
       and attach it to the default router.
    3. Launch instance vcenter_VM with vmdk image supported ipv6 in net_1 in vcenter az
    4. Launch instance nova_VM with image supported ipv6 in net_1 in nova az
    5. Verify instances have got an ipv4 and ipv6 addresses.
       IPv6 address should contain EUI-64 of interface.
    6. Verify icmp/ssh is allowed between instances by ipv4 address.
    7. Verify icmp/ssh is allowed between instances by ipv6 unique address.
    8. Verify icmp/ssh is allowed between instances by ipv6 link-local address.


Expected result
###############

Instances can ping each other and ssh is allowed between instances.



Check dualstack linc-local connectivity
---------------------------------------


ID
##

dvs_dualstack_linc_local


Description
###########

Check dualstack lonc-local connectivity


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing networks:
       network name: net_1
         subnet_v6: FD11::/64, ipv6_address_mode: SLAAC
         subnet_v4: 192.168.11.0/24, DNS: 8.8.8.8, 8.8.4.4
       network name: net_2
         subnet_v6: FD12::/64, ipv6_address_mode: SLAAC
         subnet_v4: 192.168.12.0/24, DNS: 8.8.8.8, 8.8.4.4
       and attach them to the default router.
    3. Launch instance vcenter_VM1 with vmdk image supported ipv6 in net_1 in vcenter az.
    4. Launch instance vcenter_VM2 with vmdk image supported ipv6 in net_1 in vcenter az.
    5. Verify instances have got an ipv4 and ipv6 addresses.
       IPv6 address should contain EUI-64 of interface.
    6. Verify icmp/ssh is allowed between instances by ipv4 address.
    7. Verify icmp/ssh is allowed between instances by ipv6 unique address.
    8. Verify icmp/ssh is allowed between instances by ipv6 link-local address.
    9. Detach net_1 interface from vcenter_VM2.
    10. Attach net_2 interface to vcenter_VM2 and reboot instance.
    11. Verify icmp/ssh is allowed between instances by ipv4 address.
    12. Verify icmp/ssh is allowed between instances by ipv6 unique address.
    13. Verify icmp/ssh is denied between instances by ipv6 link-local address.


Expected result
###############

Instances can ping each other and ssh is allowed between instances when
they are connected to the same network. Instances can not communicate between
each other by linc-local ip when they are in different networks.



Check ipv6 DHCPv6 stateless instances creation.
-----------------------------------------------


ID
##

dvs_dhcpv6_stateless_ipv6


Description
###########

Check ipv6 DHCPv6 stateless instances creation.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing networks:
       network name: net_1
         subnet_v6: FD11::/64, ipv6_address_mode: DHCPv6 stateless
       and attach it to the default router.
    3. Launch instance vcenter_VM1 with vmdk image supported ipv6 in net_1 in vcenter az.
    4. Launch instance vcenter_VM2 with vmdk image supported ipv6 in net_1 in nova az.
    5. Verify instances have got an ipv6 addresses.
       IPv6 address should contain EUI-64 of interface.
    6. Verify icmp/ssh is allowed between instances by ipv6 unique address.
    7. Verify icmp/ssh is allowed between instances by ipv6 link-local address.


Expected result
###############

Instances can ping each other and ssh is allowed between instances.



Check ipv6 DHCPv6 statefull instances creation.
-----------------------------------------------


ID
##

dvs_dhcpv6_statefull_ipv6


Description
###########

Check ipv6 DHCPv6 stateless instances creation.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing networks:
       network name: net_1
         subnet_v6: FD11::/64, ipv6_address_mode: DHCPv6 statefull
       and attach it to the default router.
    3. Launch instance vcenter_VM1 with vmdk image supported ipv6 in net_1 in vcenter az.
    4. Launch instance vcenter_VM2 with image supported ipv6 in net_1 in nova az.
    5. Verify instances have got an ipv6 addresses.
       IPv6 address should NOT contain EUI-64 of interface.
    6. Verify icmp/ssh is allowed between instances by ipv6 unique address.
    7. Verify icmp/ssh is allowed between instances by ipv6 link-local address.


Expected result
###############

Instances can ping each other and ssh is allowed between instances.



Check ipv6 DHCPv6 statefull duplicate detected.
-----------------------------------------------


ID
##

dvs_dhcpv6_statefull_duplicate_detected


Description
###########

Check ipv6 DHCPv6 statefull duplicate detected.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing networks:
       network name: net_1
         subnet_v6: FD11::/64,
         ipv6_address_mode: DHCPv6 statefull
         ipv6_address_range: fd11::2,fd11::3
    3. Launch instance vcenter_VM1 with vmdk image supported ipv6 in net_1 in vcenter az.
    4. Launch instance vcenter_VM2 with vmdk image supported ipv6 in net_1 in vcenter az.
    5. Verify instances vcenter_VM1 has got an ipv6 addresses fd11::3.
    6. Verify instances vcenter_VM2 is in ERROR state and has NOT got an ipv6 addresses.


Expected result
###############

Only vcenter_VM1 get an ipv6 address and was deployed successfully.




Security group rules for ipv6 in dualstack.
-------------------------------------------


ID
##

dvs_vcenter_dualstack_sg_ipv6


Description
###########

Verify network traffic is allowed/denied to instances according security groups
rules.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing networks:
       network name: net_1
         subnet_v6: FD11::/64, ipv6_address_mode: SLAAC
         subnet_v4: 192.168.11.0/24, DNS: 8.8.8.8, 8.8.4.4
         and attach it to the default router.
    4. Create security groups: SG_web, SG_db, SG_man, SG_DNS, SG_defaultv4_icmpv6
    5. Delete all default egress rules from: SG_web, SG_db, SG_man, SG_DNS
    6. Delete v6 rules from SG_defaultv4_icmpv6 and add:
       Rule: Other protocols
         direction: Ingress
         remote: Security Group
         Security Group: SG_default_v4
         ether type: IPv4
       Rule: ALL ICMP
         Direction: Ingress
         Remote: CIDR
         CIDR: ::/0
       Rule: ALL ICMP
         Direction: Egress
         Remote: CIDR
         CIDR: ::/0
    7. Add rules to SG_web:
       Rule: MYSQL
         remote: Security Group
         Security Group: SG_db
       Rule: SSH
         remote: Security Group
         Security Group: SG_man
       Rule: HTTP
         remote: CIDR
         CIDR: ::/0
    8. Add rules to SG_db:
       Rule: MYSQL
         remote: Security Group
         Security Group: SG_web
       Rule: HTTP
         remote: CIDR
         CIDR: ::/0
       Rule: HTTPS
         remote: CIDR
         CIDR: ::/0
       Rule: SSH
         remote: Security Group
         Security Group: SG_man
    9. Add rules to SG_DNS:
       Rule: DNS
         remote: CIDR
         CIDR: ::/0
    10. Add rules to SG_man:
       Rule: SSH
         remote: CIDR
         CIDR: ::/0
    11. Launch following instances in net_1 from image 'ubuntu':
        instance 'webserver' of vcenter az with SG_web, SG_DNS, SG_icmpv6, SG_defaultv4_icmpv6
        instance 'mysqldb ' of vcenter az with SG_db, SG_DNS, SG_icmpv6, SG_defaultv4_icmpv6
        instance 'manage' of nova az with SG_man, SG_DNS, SG_default_ipv6
    12. Verify traffic is allowed to vm 'webserver' from internet by ipv6 http port 80.
    13. Verify traffic is allowed to vm 'webserver' from vm 'manage' by ipv6 tcp port 22.
    14. Verify traffic is allowed to vm 'webserver' from vm 'mysqldb' by ipv6 tcp port 3306.
    15. Verify traffic is allowed to internet from instance 'mysqldb' by ipv6 https port 443.
    16. Verify traffic is allowed to instance 'mysqldb' from vm 'manage' by ipv6 tcp port 22.
    17. Verify traffic is allowed to vm 'manage' from internet by ipv4 tcp port 22.
    18. Verify traffic is denied to vm 'webserver' from internet by ipv6 tcp port 22.
    19. Verify traffic is denied to vm 'mysqldb' from internet by ipv6 tcp port 3306.
    20. Verify traffic is denied to vm 'manage' from internet by ipv6 http port 80.
    21. Verify traffic is allowed to all instances from DNS server by ipv6 udp/tcp port 53 and vice versa.
    22. Verify all ipv4 traffic is allowed.


Expected result
###############

Network traffic is allowed/denied to instances according security groups
rules.



Security group rules for ipv4 in dualstack.
-------------------------------------------


ID
##

dvs_vcenter_dualstack_sg_ipv4


Description
###########

Verify network traffic is allowed/denied to instances according security groups
rules.


Complexity
##########

core


Steps
#####

    1. Set up for system tests.
    2. Create folowing networks:
       network name: net_1
         subnet_v6: FD11::/64, ipv6_address_mode: SLAAC
         subnet_v4: 192.168.11.0/24, DNS: 8.8.8.8, 8.8.4.4
         and attach it to the default router.
    4. Create security groups: SG_web, SG_db, SG_man, SG_DNS, SG_default_ipv6
    5. Delete all default egress rules from: SG_web, SG_db, SG_man, SG_DNS
    6. Delete IPv4 rules from SG_default_ipv6 and add:
       Rule: Other protocols
         direction: Ingress
         remote: Security Group
         Security Group: SG_default_ipv6
    7. Add rules to SG_web:
       Rule: MYSQL
         remote: Security Group
         Security Group: SG_db
       Rule: SSH
         remote: Security Group
         Security Group: SG_man
       Rule: HTTP
         remote: CIDR
         CIDR: 0.0.0.0/0
    8. Add rules to SG_db:
       Rule: MYSQL
         remote: Security Group
         Security Group: SG_web
       Rule: HTTP
         remote: CIDR
         CIDR: 0.0.0.0/0
       Rule: HTTPS
         remote: CIDR
         CIDR: 0.0.0.0/0
       Rule: SSH
         remote: Security Group
         Security Group: SG_man
    9. Add rules to SG_DNS:
       Rule: DNS
         remote: CIDR
         CIDR: 0.0.0.0/0
    10. Add rules to SG_man:
       Rule: SSH
         remote: CIDR
         CIDR: 0.0.0.0/0
    11. Launch following instances in net_1 from image 'ubuntu':
        instance 'webserver' of vcenter az with SG_web, SG_DNS, SG_default_ipv6
        instance 'mysqldb ' of vcenter az with SG_db, SG_DNS, SG_default_ipv6
        instance 'manage' of nova az with SG_man, SG_DNS, SG_default_ipv6
    12. Verify traffic is allowed to vm 'webserver' from internet by ipv4 http port 80.
    13. Verify traffic is allowed to vm 'webserver' from vm 'manage' by ipv4 tcp port 22.
    14. Verify traffic is allowed to vm 'webserver' from vm 'mysqldb' by ipv4 tcp port 3306.
    15. Verify traffic is allowed to internet from instance 'mysqldb' by ipv4 https port 443.
    16. Verify traffic is allowed to instance 'mysqldb' from vm 'manage' by ipv4 tcp port 22.
    17. Verify traffic is allowed to vm 'manage' from internet by ipv4 tcp port 22.
    18. Verify traffic isn denied to vm 'webserver' from internet by ipv4 tcp port 22.
    19. Verify traffic isn denied to vm 'mysqldb' from internet by ipv4 tcp port 3306.
    20. Verify traffic isn denied to vm 'manage' from internet by ipv4 http port 80.
    21. Verify traffic is allowed to all instances from DNS server by ipv4 udp/tcp port 53 and vice versa.
    22. Verify all ipv6 traffic is allowed.


Expected result
###############

Network traffic is allowed/denied to instances according security groups
rules.