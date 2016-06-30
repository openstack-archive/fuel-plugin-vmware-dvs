Introduction
------------

The purpose of this document is to describe how to install, configure,
and use the VMware DVS plugin 3.0.0 for Fuel 9.0.

Mirantis OpenStack supports using vCenter as a hypervisor on vCenter-only or
heterogeneous environments that are mixed with KVM. The vmware_dvs driver for
Neutron ML2 plugin allows using Neutron for networking in such environments.
Therefore, you get the following advanced network features for your
environment:

- Create multi-tier networks (for example: web tier, database tier,
  application tier)

- Control over IP addressing and security groups' rules.

- Add and configure custom services (for example: firewall,
  intrusion-prevention system)

- VPN/Bridge to a remote physical hosting or customer premises.
