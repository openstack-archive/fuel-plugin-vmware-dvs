Using advanced neutron's possibilities with VMware DVS plugin
-------------------------------------------------------------

#. Once OpenStack has been deployed, we can start using Neutron for
   networking. The port group for admin\_internal\_net should appear
   on the vCenter:

   .. image:: _static/net04pg.png

.. raw:: latex

   \pagebreak

2. In Horizon, the network topology should look like:

   .. image:: _static/topology.png

   where VMware is the name of the instance located on the vCenter.

#. You can use Neutron for such instance brand the same way as for KVM-located instances.

#. DVS Security groups functionality differs from KVM implementatin. VMWare DVS does not
   support stateful firewall properties and ICMP types. DVS Plugin realises emulation logic
   to support the similar behavior. It installs reverse traffic rule for each SG rule.
   VMWare DVS plugin state emulation logic uses ephemeral port range filter to rise security
   of reverse rules implementation.

   Just add only those rules if you want to correctly launch EC2 compatible image with
   matadata request and DNS access:

   Implement Custom TCP Ergess rule to 169.254.169.254/32 CIDR port 80
   Implement Custom UDP Egress rule to '<DNS server IP or 0.0.0.0/0>' CIDR port 53

   DVS plugin will install four rules:

   TCP Egress from any IP ports 32768-65535 to metadata IP port 80
   TCP Ingress from metadata IP port 80 to any IP ports 32768-65535
   UDP Egress from any IP ports 32768-65535 to DNS IP port 53
   UDP Ingress from DNS IP port 53 to any IP ports 32768-65535

   32768-65535 is the useful ethemetal port range for most Linux kernels and Windows hosts.

   Common egress TCP rule looks like this:

   TCP Egress to any ports 0.0.0.0/0 CIDR

   It works like:

   TCP Egress from any IP ports 32768-65535 to any IP any port
   TCP Ingress from any IP any port to any IP ports 32768-65535

   and private ports of your VM like http or ssh will be closed.

   DVS plugin support only symmectric ICMP interaction. If your host can ping destination host,
   it means the destination host can ping your host by reverse rules.

#. Sometimes the error at log files happens "Cannot complete operation due to concurrent
   modification by another operation." due to absence of concurrent access to modify resources
   by vSphere. Do not panic. Driver has special wrapper for this exception.
