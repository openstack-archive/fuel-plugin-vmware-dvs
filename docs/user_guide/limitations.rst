Limitations
-----------

The VMware DVS plugin 3.1.0 for Fuel has the following limitations:

* The plugin is enabled only on environments with Neutron as the
  networking option.
* Only VLANs are supported for the tenant network separation.
* Only vSphere versions 5.5 and 6.0 are supported.
* Neutron Distributed Virtual Routers (DVR) feature is not supported.
* Each vSphere cluster should be connected to one (and only one) VDS.
