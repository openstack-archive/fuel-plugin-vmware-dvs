module Puppet::Parser::Functions
  newfunction(:override_hiera, :type => :rvalue,
              :doc => <<-EOS
              Construct properly network_maps string
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'No file name provided!') if args.size < 1 or args[0] == ""
    require 'yaml'
    require 'fileutils'
    file=args[0]
    dir=File.dirname(file)
    # read data
    if File.exists?(file)
      old_data = YAML::load_file(file) || {}
      new_data = Hash.new{|h,k| h[k]=Hash.new(&h.default_proc) }.merge(old_data)
    else
      new_data = Hash.new{|h,k| h[k]=Hash.new(&h.default_proc) }
    end
    # modify data
    md = new_data["neutron_config"]["L2"]["mechanism_drivers"]
    if not md or md == {}
      md = "openvswitch,l2population,vmware_dvs"
    else
      if not md.include?('vmware_dvs')
        md << ',vmware_dvs'
      end
    end
    new_data["neutron_config"]["L2"]["mechanism_drivers"] = md
    # write data
    unless File.directory?(dir)
      FileUtils.mkdir_p(dir)
    end
    File.open(file, 'w') {|f| f.write new_data.to_yaml}
    end
end
