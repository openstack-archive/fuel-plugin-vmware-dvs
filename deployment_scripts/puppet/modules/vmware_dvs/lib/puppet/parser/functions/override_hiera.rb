def from_hiera(fname)
  # read data
  old_data = {}
  if File.exists?(fname)
    old_data = YAML::load_file(fname)
  end
  # Hash with default value
  return Hash.new{|h,k| h[k]=Hash.new(&h.default_proc) }.merge(old_data)
end

def add_mech(hiera)
  # modify data
  md = hiera["neutron_config"]["L2"]["mechanism_drivers"]
  if not md or md == {}
    md = "openvswitch,l2population,vmware_dvs"
  else
    if not md.include?('vmware_dvs')
      md << ',vmware_dvs'
    end
  end
  hiera["neutron_config"]["L2"]["mechanism_drivers"] = md
end

def add_physnet(hiera, netmaps)
  d = {}
  np = netmaps.split(';').collect{|k| k.split(":")}.select{|x| x.length > 2}
  np.each{|k| d = d.merge({k[2] => {"bridge" => k[3],
                                    "vlan_range" => k[4] + ":" + k[5]}})}
  hiera["neutron_config"]["L2"]["phys_nets"] = d
  return hiera
end

def to_hiera(fname, hiera)
  dir=File.dirname(fname)
  unless File.directory?(dir)
    FileUtils.mkdir_p(dir)
  end
  File.open(fname, 'w') {|f| f.write hiera.to_yaml}
end

module Puppet::Parser::Functions
  newfunction(:override_hiera, :type => :rvalue,
              :doc => <<-EOS
              Construct properly network_maps string
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'No file name provided!') if args.size < 1 or args[0] == ""
    require 'yaml'
    require 'fileutils'
    fname=args[0]
    netmaps = args[1]
    hiera = from_hiera(fname)
    add_mech(hiera)
    add_physnet(hiera, netmaps)
    to_hiera(fname, hiera)
    end
end
