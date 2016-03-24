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
        cluster = vc["vc_cluster"]
        if netmaps.include? ':'
          vds = netmaps.delete(' ').split(";").collect{|k| k.split(":")}.select{|x| x[0] == cluster}.collect{|x| x[1]}[0]
        else
          vds = netmaps
        end
        agent["network_maps"] = physnet + ":" + vds
        agent["use_fw_driver"] = use_fw_driver
        agent["ha_enabled"] = controllersp
        agent["primary"] = primaryp
        agents.push(agent)
      end
    }
    Hash[agents.collect {|agent| [agent["host"], agent]}]
  end
end
