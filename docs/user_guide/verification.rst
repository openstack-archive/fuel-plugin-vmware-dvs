Verify a deployed environment with VMware DVS plugin
----------------------------------------------------

After you deploy an environment with VMware DVS plugin, complete the
following verification steps:

#. Log in to the Fuel Master node CLI.
#. Verify whether the DVS agent is available in the list of Neutron agents:

   .. code-block:: console

    $ neutron agent-list
    +----+-----------+-----------+-----------------+------+---------------+-----------------+
    |id  |agent_type |host       |availability_zone|alive |admin_state_up |binary           |
    +----+-----------+-----------+-----------------+----------------------+-----------------+
    |... |DVS agent  |vcenter-sn2|                 |:-)   |True           |neutron-dvs-agent|
    +----+-----------+-----------+-----------------+------+---------------+-----------------+

#. Log in to the Fuel web UI.
#. Click the :guilabel:`Health Check` tab.
#. Run necessary health tests. For details, see:
   `Verify your OpenStack environment <http://docs.openstack.org/developer/fuel-docs/userdocs/fuel-user-guide/verify-environment.html>`_.
