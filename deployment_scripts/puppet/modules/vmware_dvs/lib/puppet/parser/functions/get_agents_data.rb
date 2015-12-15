module Puppet::Parser::Functions
  newfunction(:get_agents_data, :type => :rvalue,
              :doc => <<-EOS
              Create parameters for the agent resource
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'Shoud have 3 arguments!') if args.size < 2 or args[0] == ""
    vcenter = args[0]['computes']
    physnet = args[1]["predefined_networks"]["admin_internal_net"]["L2"]["physnet"]
    dvSwitch = args[2]["vmware_dvs_net_maps"]
    agents = []
    vcenter.each {|vc|
      agent = {}
      agent["host"] = vc["availability_zone_name"] + "-" + vc["service_name"]
      agent["vsphere_hostname"] = vc["vc_host"]
      agent["vsphere_login"] = vc["vc_user"]
      agent["vsphere_password"] = vc["vc_password"]
      agent["network_maps"] = physnet + ":" + dvSwitch
      agents.push(agent)
    }
    Hash[agents.collect {|agent| [agent["host"], agent]}]
  end
end
