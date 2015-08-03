module Puppet::Parser::Functions
  newfunction(:get_network_maps, :type => :rvalue,
              :doc => <<-EOS
              Construct properly network_maps string
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'No name of dvSwitch provided!') if args.size < 1
    maps = args[0]
    physnet = args[1]
    if maps.include? ':'
      maps
    else
      physnet + ":" + maps
    end
  end
end
