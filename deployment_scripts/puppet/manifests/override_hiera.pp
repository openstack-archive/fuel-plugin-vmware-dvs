notice('MODULAR: fuel-plugin-vmware-dvs/overrride_hiera')

$src        = '/etc/hiera/override/plugins.yaml'
$vmware_dvs = hiera_hash('fuel-plugin-vmware-dvs', {})
$netmaps    = $vmware_dvs['vmware_dvs_net_maps']

$res        = override_hiera($src, $netmaps)
