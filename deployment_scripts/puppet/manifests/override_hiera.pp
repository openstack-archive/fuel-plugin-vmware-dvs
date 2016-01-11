notice('MODULAR: fuel-plugin-vmware-dvs/overrride_hiera')

$src = '/etc/hiera/override/plugins.yaml'
$res   = override_hiera($src)
