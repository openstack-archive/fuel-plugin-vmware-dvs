Create and Configure an environment with VMware DVS plugin
----------------------------------------------------------

#. `Create a new OpenStack
   environment <https://docs.mirantis.com/openstack/fuel/fuel-8.0/user-guide.html#create-a-new-openstack-environment>`_
   with Fuel UI wizard.

   .. image:: _static/create.png

.. raw:: latex

   \pagebreak

2. In *Compute* menu, select *vCenter* checkbox:

   .. image:: _static/compute.png

#. Select *Neutron with VMware DVS* for *Networking Setup*

   .. image:: _static/net.png

.. raw:: latex

   \pagebreak

4. Finish environment creation following
   `documentation <https://docs.mirantis.com/openstack/fuel/fuel-8.0/user-guide.html#create-a-new-openstack-environment>`_.

#. Open the *Nodes* tab and `add
   <https://docs.mirantis.com/openstack/fuel/fuel-8.0/user-guide.html#configure-your-environment>`__
   at least 1 Controller node to the environment:

   .. image:: _static/nodes-controller.png

   (Optional) You can also add 1 dedicated Compute VMware node:

   .. image:: _static/nodes-vmware.png

#. Open the *Networks* tab of the Fuel Web UI and chose the *Other* subtab. Select the
   *Neutron VMware DVS ML2 plugin* checkbox and specify the Cluster to VDS mapping :

   .. image:: _static/settings.png

   That mapping is forming by the specail format's string. It uses ";" for
   splitting different mappings and ":" for splitting values whithin mapping.
   There are 2 templates for mapping:

   #. ClusterName:VDSName

      where VDSName is the name of VDS on vSphere and ClusterName is the name
      of cluster that connected to this VDS.

   #. ClusterName:VDSName:PhysNet:BridgeName:VLANStart:VLANEnd

      This option is needed for case where the VDS has to use an individual
      physnet. There are 4 steps that shoud be done for using this possibility:

      #. Create networking template according to the `specification <https://specs.openstack.org/openstack/fuel-specs/specs/7.0/networking-templates.html>`_.
         That template describes new network, bridge and assign it to an
	 interface.

      #. Upload that template using command like:
	 ::

	    # fuel --env $env network-template --upload

      #. Create fake network-group with name from template:
	 ::

	    # fuel network-group --node-group $env --create --name $network ...

      #. Describe it in the network-mapping string, where PhysNet is any unique
	 name for physnet, BridgeName is bridge from the template, VLANStart
	 and VLANEnd are define vlan range for neutron networks.

   Set the checkbox "Use the VMware DVS firewall driver" if you want to use
   security groups on your ports.

   VMware DVS ML2 plugin does not support DVR feature. Keep Neutron DVR
   checkbox on Neutron Advanced Configuration tab at unchecked state.

.. raw:: latex

   \pagebreak

7. Fill in the VMware configuration fields on the *VMware* tab:

   .. image:: _static/vmware.png

   (Optional) Choose Compute VMware node if your environment has the role:

   .. image:: _static/vmware2.png

#. The rest of configuration is up to you.
   See `Mirantis OpenStack User Guide <https://docs.mirantis.com/openstack/fuel/fuel-8.0/user-guide.html>`__
   for instructions.

#. Click *Deploy changes* button to finish.

.. raw:: pdf

   PageBreak
