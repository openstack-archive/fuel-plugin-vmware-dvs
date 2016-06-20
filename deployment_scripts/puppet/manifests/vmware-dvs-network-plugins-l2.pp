notice('MODULAR: fuel-plugin-vmware-dvs/plugins/ml2.pp')

class neutron {}
class { 'neutron' :}

class {'::vmware_dvs::l2': }
