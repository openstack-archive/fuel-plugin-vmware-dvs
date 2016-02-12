The VMware DVS plugin
---------------------

MOS supports using vCenter as a hypervisor in a vCenter-only or
heterogeneous, mixed with KVM environments. There is the vmware\_dvs
driver for Neutron ML2 plugin which provides usage Neutron for
networking in such environments. Thereby environments receives an
advanced network features:

-  Ability to create multi-tier networks (e.g., web tier, db tier, app
   tier).

-  Control over IP addressing.

-  Ability to insert an configure their own services (e.g., firewall,
   IPS)

-  VPN/Bridge to remote physical hosting or customer premises.
