.. _configure_env:

Configure an environment with VMware DVS plugin
-----------------------------------------------

Configuring and deploying an environment with VMware DVS plugin involves
creating an environment in Fuel and modifying the environment settings.

**To configure an OpenStack environment with VMware DVS plugin:**

#. Using the Fuel web UI, follow steps 1 to 5 of the `Create a new OpenStack
   environment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/create-environment/start-create-env.html>`_
   instruction.

#. In the :guilabel:`Compute` menu, select :guilabel:`vCenter`:

   .. figure:: _static/compute.png
      :width: 90%

.. raw:: latex

   \pagebreak

#. In the :guilabel:`Networking Setup` menu, select
   :guilabel:`Neutron with VMware DVS`:

   .. figure:: _static/net.png
      :width: 90%

#. Follow steps 8-10 of the `Create a new OpenStack
   environment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/create-environment/start-create-env.html>`_
   instruction.

#. In the :guilabel:`Nodes` tab of the Fuel web UI, `add
   <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/configure-environment/add-nodes.html>`_
   at least one :guilabel:`Controller` node to the environment:

   .. figure:: _static/nodes-controller.png
      :width: 90%

   (Optional) You can also add one dedicated :guilabel:`Compute VMware` node:

   .. figure:: _static/nodes-vmware.png
      :width: 90%

.. raw:: latex

   \pagebreak

#. In the :guilabel:`Networks` tab, click :guilabel:`Other`:

   #. Select the :guilabel:`Neutron VMware DVS ML2 plugin` checkbox.
   #. Specify the :guilabel:`Cluster to VDSwitch mapping`. Please notice that
      in the 3.1 release it has new format:

      #. New string is used as a delimiter between clusters.
      #. There are 2 new columns: list of teaming uplinks and list of fallback
         uplinks. Both are optional.
      #. The semicolon is used as a delimiter between uplinks.
      #. There is no limitation for amount of uplinks.
      #. Thereby there are next options for a mapping-string:

         #. ClusterName:VDSName:TeamingUplink1;TeamingUplink2:FallBackUplink1;FallBackUplink2
         #. ClusterName:VDSName:TeamingUplink1;TeamingUplink2;...;TeamingUplinkN
         #. ClusterName:VDSName

      #. There is no option to set fallback uplinks without teaming uplinks.
      #. All uplinks should be presented on real VDS.
   #. If you want to use security groups on your ports, select
      :guilabel:`Use the VMware DVS firewall driver`.

   .. figure:: _static/settings.png
      :width: 90%
   See the `Teaming and Failover Policy <https://pubs.vmware.com/vsphere-55/index.jsp#com.vmware.vsphere.networking.doc/GUID-4D97C749-1FFD-403D-B2AE-0CD0F1C70E2B.html>`__ for more detail about uplinks usage on VDS.

   .. caution::
      The VMware DVS ML2 plugin does not support the Distributed Virtual
      Routers (DVR) feature. Therefore, do not select :guilabel:`Neutron DVR`
      in :menuselection:`Neutron L3 Configuration -> Neutron Advanced Configuration`.

.. raw:: latex

   \pagebreak

#. In the :guilabel:`VMware` tab, fill in the VMware configuration fields:

   .. figure:: _static/vmware.png
      :width: 90%

#. Make additional `configuration adjustments <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/configure-environment.html>`_.

#. Proceed to the `environment deployment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/deploy-environment.html>`_.

.. raw:: latex

   \pagebreak
