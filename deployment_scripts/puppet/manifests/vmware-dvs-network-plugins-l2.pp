notice('MODULAR: fuel-plugin-vmware-dvs/vmware-dvs-network-plugins-l2')

class neutron {}
class { 'neutron' :}

class {'::vmware_dvs::l2': }
