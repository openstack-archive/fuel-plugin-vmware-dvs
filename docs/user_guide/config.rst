.. _configure_env:

Configure an environment with VMware DVS plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuring and deploying an environment with VMware DVS plugin involves
creating an environment in Fuel and modifying the environment settings.

**To configure an OpenStack environment with VMware DVS plugin:**

#. Using Fuel Web UI, follow steps 1-5 of the `Create a new OpenStack
   environment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/create-environment/start-create-env.html>`_
   instruction.

#. In the :guilabel:`Compute` menu, select :guilabel:`vCenter`:

   .. image:: _static/compute.png
      :width: 100%

.. raw:: latex

   \pagebreak

3. In the :guilabel:`Networking Setup` menu, select
   :guilabel:`Neutron with VMware DVS`:

   .. image:: _static/net.png
      :width: 100%

#. Follow steps 8-10 of the `Create a new OpenStack
   environment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/create-environment/start-create-env.html>`_
   instruction.

#. In the :guilabel:`Nodes` tab of the Fuel Web UI, `add
   <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/configure-environment/add-nodes.html>`_
   at least 1 :guilabel:`Controller` node to the environment:

   .. image:: _static/nodes-controller.png
      :width: 100%

   (Optional) You can also add 1 dedicated :guilabel:`Compute VMware` node:

   .. image:: _static/nodes-vmware.png
      :width: 100%

.. raw:: latex

   \pagebreak

6. In the :guilabel:`Networks` tab, click :guilabel:`Other`:

   #. Select the :guilabel:`Neutron VMware DVS ML2 plugin` checkbox.
   #. Specify the :guilabel:`Cluster to VDSwitch mapping`.
   #. If you want to use security groups on your ports, select
      :guilabel:`Use the VMware DVS firewall driver`.

   .. image:: _static/settings.png
      :width: 100%

   .. caution::
      VMware DVS ML2 plugin does not support the Distributed Virtual Routers
      (DVR) feature. Therefore, do not select :guilabel:`Neutron DVR` in
      :menuselection:`Neutron L3 Configuration -> Neutron Advanced Configuration`.

.. raw:: latex

   \pagebreak

7. In the :guilabel:`VMware` tab, fill in the VMware configuration fields:

   .. image:: _static/vmware.png
      :width: 100%

   .. note:: In :guilabel:`Nova Computes` section, if your environment has
      the :guilabel:`Compute VMware` role, select it in the
      :guilabel:`Target node` drop-down menu.

#. If required, make additional configuration adjustments. For details, see
   `Configure your environment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/configure-environment.html>`_.

#. Proceed to the `environment deployment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/deploy-environment.html>`_.

.. raw:: latex

   \pagebreak
