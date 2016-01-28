 module Puppet::Parser::Functions
  newfunction(:get_agents_data, :type => :rvalue,
              :doc => <<-EOS
              Create parameters for the agent resource
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'Shoud have 5 arguments!') if args.size < 4 or args[0] == ""
    vcenter = args[0]['computes']
    physnet = args[1]["predefined_networks"]["admin_internal_net"]["L2"]["physnet"]
    dvSwitch = args[2]["vmware_dvs_net_maps"]
    current_node = args[3].split(".")[0]
    controllersp = args[4].any? {|role| role.include?("controller")}
    agents = []
    vcenter.each {|vc|
      if (vc["target_node"] == "controllers" and controllersp) or current_node == vc["target_node"]
        agent = {}
        agent["host"] = vc["availability_zone_name"] + "-" + vc["service_name"]
        agent["vsphere_hostname"] = vc["vc_host"]
        agent["vsphere_login"] = vc["vc_user"]
        agent["vsphere_password"] = vc["vc_password"]
        agent["network_maps"] = physnet + ":" + dvSwitch
        agent["ha_enabled"] = controllersp
        agents.push(agent)
      end
    }
    Hash[agents.collect {|agent| [agent["host"], agent]}]
  end
end
