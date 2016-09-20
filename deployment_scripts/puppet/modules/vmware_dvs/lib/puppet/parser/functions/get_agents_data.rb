 module Puppet::Parser::Functions
  newfunction(:get_agents_data, :type => :rvalue,
              :doc => <<-EOS
              Create parameters for the agent resource
              EOS
             ) do |args|
    raise(Puppet::ParseError, 'Shoud have 5 arguments!') if args.size < 4 or args[0] == ""
    vcenter = args[0]['computes']
    physnet = args[1]["predefined_networks"]["admin_internal_net"]["L2"]["physnet"]
    netmaps = args[2]["vmware_dvs_net_maps"].delete(' ').split("\n")
    use_fw_driver = args[2]["vmware_dvs_fw_driver"]
    current_node = args[3].split(".")[0]
    controllersp = args[4].any? {|role| role.include?("controller")}
    primaryp = args[4].any? {|role| role.include?("primary")}
    agents = []

    vcenter.each {|vc|
      if (vc["target_node"] == "controllers" and controllersp) or current_node == vc["target_node"]
        agent = {}
        ns = netmaps.dup
        agent["host"] = vc["availability_zone_name"] + "-" + vc["service_name"]
        agent["vsphere_hostname"] = vc["vc_host"]
        agent["vsphere_login"] = vc["vc_user"]
        agent["vsphere_password"] = vc["vc_password"]
        agent["vsphere_insecure"] = vc["vc_insecure"]
        agent["vsphere_ca_file"] = vc["vc_ca_file"]
        cluster = vc["vc_cluster"]
        ns = ns.keep_if {|s| s =~ /^#{cluster}/}.first.split(":")
        vds = ns[1]
        uplinks = false
        if ns.length == 4
          uplinks = ns[2] + ":" + ns[3]
        elsif ns.length == 3
          uplinks = ns[2]
        end
        agent["network_maps"] = physnet + ":" + vds
        agent["uplink_maps"] =  physnet + ":" + uplinks if uplinks
        agent["use_fw_driver"] = use_fw_driver
        agent["ha_enabled"] = controllersp
        agent["primary"] = primaryp
        agents.push(agent)
      end
    }
    Hash[agents.collect {|agent| [agent["host"], agent]}]
  end
end
