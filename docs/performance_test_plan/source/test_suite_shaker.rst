Shaker scenarios
================


The Shaker tool is a tool used and developed by Mirantis to understand
the Data Plane capabilities of an OpenStack deployment. Data Plane testing
helps cloud administrators understand their deployment from the perspective
of the applications that are using the environment. This tool can be used for
deployment planning, environment verification, and troubleshooting.
Today, Shaker focuses on network based tests using iperf to drive load across
the network. Shaker has future plans to roll out testing to evaluate I/O and CPU.
Shaker utilizes Heat (OpenStack Orchestration) templates to deploy and execute
Data Plane tests. It deploys a number of agents/compute nodes that all report
back to a centralized Shaker server.
The server is executed by shaker command and is responsible for deployment
of instances, execution of tests as specified in the scenario, for results
processing and report generation. The agent is light-weight and polls tasks
from the server and replies with the results. Agents have connectivity to
the server, but the server does not (so it is easy to keep agents behind NAT).
Shaker runs three types of network tests with many different options
(including TCP and UDP).

Instances specification
-----------------------
+------------+---------------------------------------+
| Image      | ubuntu-14.04-server-cloudimg-amd64    |
+------------+------------------------------+--------+
| Disk format|For nova availability zone    | QCOW2  |
|            +------------------------------+--------+
|            |For vCenter Availability zone | VMDK   |
+------------+------------------------------+--------+
| Flavor     |RAM                           |4096 Mb |
|            +------------------------------+--------+
|            |Disk                          |  3Gb   |
|            +------------------------------+--------+
|            |VCPU                          |   4    |
+------------+------------------------------+--------+

Abbreviations
-------------
+---------------+------------------------------------------------------------+
|Abbreviation   | Definition                                                 |
+===============+============================================================+
|AZ             | Availability zone                                          |
+---------------+------------------------------------------------------------+
|East-West      | Network traffic travels between instances.Instances on the |
|               | different networks, which plugged to a single router       |
+---------------+------------------------------------------------------------+
|North-South    | Network traffic travels between instances. Instances on the|
|               | different networks relating to the different routers.      |
|               | Instances communicate via external network by floating ip. |
+---------------+------------------------------------------------------------+

Objectives
----------
 - Get max speed with lost of packets not more than 5%
 - Get difference between enabled and disabled Firewall
 - Get results for one-to-many TCP/UDP


Scenarios
---------

Single availability zone scenarios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OpenStack L2 Performance
########################

ID
..

perf_l2

Description
...........

In this scenario Shaker launches 1 pair of instances in the same tenant network.
Each instance is hosted on a separate compute node. The traffic goes within
the tenant network (L2 domain).

Configuration
.............

+------------------+---------+
| Deployment configurations  |
+------------------+---------+
|Parameter         | Value   |
+==================+=========+
|Availability zone | vCenter |
+------------------+---------+
|Compute nodes     |   2     |
+------------------+---------+

+-----------------------------------------+
|         Scenarios                       |
+------------------+----------------------+
|Parameters        | Value                |
+==================+======+=======+=======+
|Title             |Ping  | TCP   | UDP   |
+------------------+------+-------+-------+
|class             |flent | iperf3|iperf3 |
+------------------+------+-------+-------+
|bandwidth         |  -   |   -   | 9500  |
+------------------+------+-------+-------+
|buffer_size       |  -   |   -   | 8950  |
+------------------+------+-------+-------+
|time              | 10   | 600   | 600   |
+------------------+------+-------+-------+
| Datagram size    |      |       |       |
+------------------+------+-------+-------+
|SLA               |      |       |       |
+------------------+------+-------+-------+



OpenStack L3 East-West Performance
##################################

ID
..

perf_l3_east-west

Description
...........

In this scenario Shaker launches 1 pair of instances, each instance on its own
compute node. Instances are connected to one of 2 tenant networks, which
plugged into single router. The traffic goes from one network to the other
(L3 east-west).

Configuration
.............

+------------------+---------+
| Deployment configurations  |
+------------------+---------+
|Parameter         | Value   |
+==================+=========+
|Availability zone | vCenter |
+------------------+---------+
|Compute nodes     |   2     |
+------------------+---------+

+-----------------------------------------+
|         Scenarios                       |
+------------------+----------------------+
|Parameters        | Value                |
+==================+======+=======+=======+
|Title             |Ping  | TCP   | UDP   |
+------------------+------+-------+-------+
|class             |flent | iperf3|iperf3 |
+------------------+------+-------+-------+
|bandwidth         |  -   |   -   | 9500  |
+------------------+------+-------+-------+
|buffer_size       |  -   |   -   | 8950  |
+------------------+------+-------+-------+
|time              | 10   | 600   | 600   |
+------------------+------+-------+-------+
| Datagram size    |      |       |       |
+------------------+------+-------+-------+
|SLA               |      |       |       |
+------------------+------+-------+-------+

OpenStack L3 North-South Performance
####################################

ID
..

perf_l3_north-south

Description
...........

In this scenario Shaker launches 1 pair of instances on different compute nodes.
Instances are in different networks connected to different routers,
master accesses slave by floating ip. The traffic goes from one network
via external network to the other network.

Configuration
.............

+------------------+---------+
| Deployment configurations  |
+------------------+---------+
|Parameter         | Value   |
+==================+=========+
|Availability zone | vCenter |
+------------------+---------+
|Compute nodes     |   2     |
+------------------+---------+

+-----------------------------------------+
|         Scenarios                       |
+------------------+----------------------+
|Parameters        | Value                |
+==================+======+=======+=======+
|Title             |Ping  | TCP   | UDP   |
+------------------+------+-------+-------+
|class             |flent | iperf3|iperf3 |
+------------------+------+-------+-------+
|bandwidth         |  -   |   -   | 9500  |
+------------------+------+-------+-------+
|buffer_size       |  -   |   -   | 8950  |
+------------------+------+-------+-------+
|time              | 10   | 600   | 600   |
+------------------+------+-------+-------+
| Datagram size    |      |       |       |
+------------------+------+-------+-------+
|SLA               |      |       |       |
+------------------+------+-------+-------+


OpenStack L2 Dense
##################


ID
..

dense_l2

Description
...........

In this scenario Shaker launches several pairs of instances on a single
compute node. Instances are plugged into the same tenant network.
The traffic goes within the tenant network (L2 domain).

Configuration
.............

+------------------+---------+
| Deployment configurations  |
+------------------+---------+
|Parameter         | Value   |
+==================+=========+
|Availability zone | vCenter |
+------------------+---------+
|Density           |   8     |
+------------------+---------+
|Compute nodes     |   1     |
+------------------+---------+

OpenStack L3 East-West Dense
############################

ID
..

dense_l3_east-west

Description
...........

In this scenario Shaker launches pairs of instances on the same compute node.
Instances are connected to different tenant networks connected to one router.
The traffic goes from one network to the other (L3 east-west).

Configuration
.............

+------------------+----------------------+
| Deployment configurations               |
+------------------+----------------------+
|Parameter         | Value                |
+==================+=========+============+
|Availability zone | Nova az | vCenter az |
+------------------+---------+------------+
|Density           |   8     |    8       |
+------------------+---------+------------+
|Compute nodes     |   1     |    1       |
+------------------+---------+------------+

OpenStack L3 North-South Dense
##############################

ID
..

dense_l3_north-south

Description
...........

In this scenario Shaker launches pairs of instances on the same compute node.
Instances are connected to different tenant networks, each connected to own router.
Instances in one of networks have floating IPs.
The traffic goes from one network via external network to the other network.


Configuration
.............

+------------------+----------------------+
| Deployment configurations               |
+------------------+----------------------+
|Parameter         | Value                |
+==================+=========+============+
|Availability zone | Nova az | vCenter az |
+------------------+---------+------------+
|Density           |   8     |    8       |
+------------------+---------+------------+
|Compute nodes     |   1     |    1       |
+------------------+---------+------------+

OpenStack L2
############

ID
..

full_l2


OpenStack L3 East-West
######################

ID
..

full_l3_east-west


OpenStack L3 North-South
########################

ID
..

full_l3_north-south


OpenStack L2 UDP
################

ID
..

udp_l2


OpenStack L3 East-West UDP
##########################

ID
..

udp_3_east-west


OpenStack L3 North-South UDP
############################

ID
..

udp_l3_north-south
