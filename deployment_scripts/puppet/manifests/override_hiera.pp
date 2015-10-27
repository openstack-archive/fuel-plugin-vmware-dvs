notice('MODULAR: vmware_dvs overrride hiera task')
$src = '/etc/hiera/override/plugins.yaml'
$res   = override_hiera($src)
