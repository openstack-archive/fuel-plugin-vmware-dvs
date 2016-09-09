notice('MODULAR: fuel-plugin-vmware-dvs/override_hiera')

$src = '/etc/hiera/plugins/fuel-plugin-vmware-dvs.yaml'
$res = override_hiera($src)
