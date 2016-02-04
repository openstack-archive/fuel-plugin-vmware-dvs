#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import paramiko

from netaddr import *
from proboscis.asserts import assert_true
from devops.helpers.helpers import wait
from devops.error import TimeoutError


from fuelweb_test.settings import SERVTEST_TENANT
from fuelweb_test import logger

#defaults
external_net_name = 'admin_floating_net'
zone_image_maps = {'vcenter': 'TestVM-VMDK',
                   'nova': 'TestVM'}


def create_instances(os_conn=None, vm_count=None, nics=None,
                     security_group=None):
    """Create Vms on available hypervisors
    :param os_conn: type object, openstack
    :param vm_count: type interger, count of VMs to create
    :param nics: type dictionary, neutron networks
                     to assign to instance
    :param security_group: type dictionary, security group to assign to
                        instances
    """
    boot_timeout = 300
    # Get list of available images,flavors and hipervisors
    images_list = os_conn.nova.images.list()
    flavors_list = os_conn.nova.flavors.list()
    available_hosts = os_conn.nova.services.list(binary='nova-compute')
    instances = []
    for host in available_hosts:
        for zone in zone_image_maps.keys():
            if host.zone == zone:
                image = [image for image
                         in images_list
                         if image.name == zone_image_maps[zone]][0]
        instance = os_conn.nova.servers.create(
            flavor=flavors_list[0],
            name='test_{0}'.format(image.name),
            image=image, min_count=vm_count,
            availability_zone='{0}:{1}'.format(host.zone, host.host),
            nics=nics
        )
        instances.append(instance)

    # Verify that current state of each VMs is Active
    #srv_list = os_conn.get_servers()
    #for srv in srv_list:
    for instance in instances:
        assert_true(os_conn.get_instance_detail(instance).status != 'ERROR',
                    "Current state of Vm {0} is {1}".format(
                        instance.name,
                        os_conn.get_instance_detail(instance).status))
        try:
            wait(
                lambda:
                os_conn.get_instance_detail(instance).status == "ACTIVE",
                timeout=boot_timeout)
        except TimeoutError:
            logger.error(
                "Timeout is reached.Current state of Vm {0} is {1}".format(
                instance.name, os_conn.get_instance_detail(instance).status))
        # assign security group
        if security_group:
            instance.add_security_group(security_group)


def check_connection_vms(os_conn, srv_list, remote, command,
                         result_of_command=0,
                         destination_ip=None, ip_ver='ipv4'):
    """Check network connectivity between instancea and destination ip
       with ping
    :param os_conn: type object, openstack
    :param srv_list: type list, instances
    :param packets: type int, packets count of icmp reply
    :param remote: SSHClient to primary controller
    :param destination_ip: type list, remote destination ip to
                           check by ping
    """
    creds = ("cirros", "cubswin:)")
    commands = {
                "pingv4": "ping -c 5 {}",
                "pingv6": "ping6 -c 5 {}",
                "arping": "sudo arping -I eth0 {}"}

    for srv in srv_list:
        addresses = srv.addresses[srv.addresses.keys()[0]]
        fip = [add['addr'] for add in addresses
               if add['OS-EXT-IPS:type'] == 'floating'][0]

        if not destination_ip:
            destination_ip = [s.networks[s.networks.keys()[0]][0]
                              for s in srv_list if s != srv]

        for ip in destination_ip:
            if ip != srv.networks[srv.networks.keys()[0]][0]:
                if ip_ver == 'ipv6':
                    ip = str(IPAddress(ip).ipv6())

                logger.info("Connect to VM {0}".format(fip))
                command_result = os_conn.execute_through_host(
                    remote, fip,
                    commands[command].format(ip), creds)
                logger.info("Command result: \n"
                            "{0}\n"
                            "{1}\n"
                            "exit_code={2}"
                            .format(command_result['stdout'],
                                    command_result['stderr'],
                                    command_result['exit_code']))
                assert_true(
                    result_of_command == command_result['exit_code'],
                    " Command {0} from Vm {1},"
                    " executed with code {2}".format(
                        commands[command].format(ip),
                        fip, command_result)
                )


def get_ssh_connection(ip, username, userpassword, timeout=30):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, port=22, username=username,
                             password=userpassword, timeout=timeout)
    return ssh


def check_ssh_between_instances(instance1, instance2):
    """Check ssh conection between instances
    :param instance1: dictionary with keys ip, username and userpassword
    :param instance2: dictionary with keys ip, username and userpassword
    """

    ssh = self.get_ssh_connection(instance1['ip'], instance1['username'],
                         instance1['userpassword'], timeout=30)

    interm_transp = ssh.get_transport()
    logger.info("Opening channel to VM")
    interm_chan = interm_transp.open_channel('direct-tcpip',
                                             (instance2['ip'], 22),
                                             (instance1['ip'], 0))
    logger.info("Opening paramiko transport")
    transport = paramiko.Transport(interm_chan)
    logger.info("Starting client")
    transport.start_client()
    logger.info("Passing authentication to VM")
    self.assertTrue(transport.auth_password(
        instance2['username'], instance2['userpassword']))


def create_and_assign_floating_ip(os_conn, srv_list=None,
                                  ext_net=None, tenant_id=None):
    """Create Vms on available hypervisors
    :param os_conn: type object, openstack
    :param srv_list: type list, objects of created instances
    :param ext_net: type object, neutron external network
    :param tenant_id: type string, tenant id
    """

    if not ext_net:
        ext_net = [net for net
                   in os_conn.neutron.list_networks()["networks"]
                   if net['name'] == external_net_name][0]
    if not tenant_id:
        tenant_id = os_conn.get_tenant(SERVTEST_TENANT).id

    if not srv_list:
        srv_list = os_conn.get_servers()
    for srv in srv_list:
        fip = os_conn.neutron.create_floatingip(
            {'floatingip': {
                'floating_network_id': ext_net['id'],
                'tenant_id': tenant_id}})
        os_conn.nova.servers.add_floating_ip(
            srv, fip['floatingip']['floating_ip_address']
        )


def add_router(os_conn, router_name, ext_net_name=external_net_name,
               tenant_name=SERVTEST_TENANT):
    """Create router with gateway
    :param router_name: type string
    :param ext_net_name: type string
    :param tenant_name: type string
    """

    ext_net = [net for net
               in os_conn.neutron.list_networks()["networks"]
               if net['name'] == ext_net_name][0]

    gateway = {"network_id": ext_net["id"],
               "enable_snat": True
               }
    tenant_id = os_conn.get_tenant(tenant_name).id
    router_param = {'router': {'name': router_name,
                               'external_gateway_info': gateway,
                               'tenant_id': tenant_id}}
    router = os_conn.neutron.create_router(body=router_param)['router']
    return router


def add_subnet_to_router(os_conn, router_id, sub_id):
    os_conn.neutron.add_interface_router(
        router_id,
        {'subnet_id': sub_id}
    )


def create_network(os_conn, name,
                   tenant_name=SERVTEST_TENANT):
    tenant_id = os_conn.get_tenant(tenant_name).id

    net_body = {"network": {"name": name,
                            "tenant_id": tenant_id
                            }
                }
    network = os_conn.neutron.create_network(net_body)['network']
    return network


def create_subnet(os_conn, network,
                  cidr, tenant_name=SERVTEST_TENANT):
    tenant_id = os_conn.get_tenant(tenant_name).id
    subnet_body = {"subnet": {"network_id": network['id'],
                              "ip_version": 4,
                              "cidr": cidr,
                              "name": 'subnet_{}'.format(
                                  network['name'][-1]),
                              "tenant_id": tenant_id
                              }
                   }
    subnet = os_conn.neutron.create_subnet(subnet_body)['subnet']
    return subnet


def get_role(os_conn, role_name):
    role_list = os_conn.keystone.roles.list()
    for role in role_list:
        if role.name == role_name:
            return role
    return None


def add_role_to_user(os_conn, user_name, role_name, tenant_name):
    tenant_id = os_conn.get_tenant(tenant_name).id
    user_id = os_conn.get_user(user_name).id
    role_id = get_role(os_conn, role_name).id
    os_conn.keystone.roles.add_user_role(user_id, role_id, tenant_id)


def check_service(ssh, commands):
        """Check that required nova services are running on controller
        :param ssh: SSHClient
        :param commands: type list, nova commands to execute on controller,
                         example of commands:
                         ['nova-manage service list | grep vcenter-vmcluster1'
        """
        ssh.execute('source openrc')
        for cmd in commands:
            wait(
                lambda:
                ':-)' in list(ssh.execute(cmd)['stdout'])[-1].split(' '),
                timeout=200)
