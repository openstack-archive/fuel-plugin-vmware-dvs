def parse_netmaps(netmaps, cluster, physnet)
  if netmaps.include? ':'
    netmaps = netmaps.split(";").select{|x| x.include?(cluster)}[0].split(":")
    if netmaps.length > 2
      physnet = netmaps[2]
      netmaps = netmaps[1]
    else
      netmaps = netmaps[1]
    end
  end
  return physnet + ":" + netmaps
end

module Puppet::Parser::Functions
  newfunction(:get_agents_data, :type => :rvalue,
              :doc => <<-EOS
              Create parameters for the agent resource
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'Shoud have 5 arguments!') if args.size < 4 or args[0] == ""
    vcenter = args[0]['computes']
    physnet = args[1]["predefined_networks"]["admin_internal_net"]["L2"]["physnet"]
    netmaps = args[2]["vmware_dvs_net_maps"]
    use_fw_driver = args[2]["vmware_dvs_fw_driver"]
    current_node = args[3].split(".")[0]
    controllersp = args[4].any? {|role| role.include?("controller")}
    primaryp = args[4].any? {|role| role.include?("primary")}
    agents = []
    vcenter.each {|vc|
      if (vc["target_node"] == "controllers" and controllersp) or current_node == vc["target_node"]
        agent = {}
        agent["host"] = vc["availability_zone_name"] + "-" + vc["service_name"]
        agent["vsphere_hostname"] = vc["vc_host"]
        agent["vsphere_login"] = vc["vc_user"]
        agent["vsphere_password"] = vc["vc_password"]
        agent["network_maps"] = parse_netmaps(netmaps, vc["vc_cluster"], physnet)
        agent["use_fw_driver"] = use_fw_driver
        agent["ha_enabled"] = controllersp
        agent["primary"] = primaryp
        agents.push(agent)
      end
    }
    Hash[agents.collect {|agent| [agent["host"], agent]}]
  end
end
