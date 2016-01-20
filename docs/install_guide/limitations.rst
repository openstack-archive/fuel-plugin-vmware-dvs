Limitations
+++++++++++

-  VMware DVS plugin be enabled only in environments with Neutron as the
   networking option.

-  Only VLANs are supported for tenant network separation.

-  Only vSphere 5.5 & 6.0 are supported.

-  Only alphanumeric, underscore and hyphen symbols for network 
   name are allowed. Network name must contain no more than 43 symbols.

-  The plugin leaves the artefact after removing. See
   :ref:`Removing the VMware DVS plugin <remove-issue>` for details.
