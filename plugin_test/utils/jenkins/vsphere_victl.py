#!/usr/bin/python3
#    Copyright 2013 - 2014 Mirantis, Inc.
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
#    under the License

import textwrap
from os import environ
import atexit
import argparse
import ssl
import sys
import requests
import paramiko
import logging as log

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

requests.packages.urllib3.disable_warnings()
log.basicConfig(format='%(levelname)s: %(message)s', level=log.ERROR)

v_host = 'VCENTER_IP'
v_user = 'VCENTER_USERNAME'
v_passw = 'VCENTER_PASSWORD'
v_dcenter = 'VC_DATACENTER'
v_datastore = 'VC_DATASTORE'
v_cluster = 'VC_CLUSTER'

env_vars = {
    v_host: environ.get(v_host, False),
    v_user: environ.get(v_user, False),
    v_passw: environ.get(v_passw, False),
    v_dcenter: environ.get(v_dcenter, False),
    v_datastore: environ.get(v_datastore, False),
    v_cluster: environ.get(v_cluster, False),
}

script_name = sys.argv[0]
func_args = {}


def setup_arg(name, short_flag, help, required=True, default=None,
              env_var=None, example=None):
    """Save parameter info to the func_args list."""
    func_args[name] = {
        'short_flag': short_flag,
        'long_flag': name,
        'required': required,
        'default': default,
        'help': help,
        'env_var': env_var,
        'example': example,
    }


env_str = ''
env_maxlen = max(map(len, env_vars.keys())) + 1
for name, value in env_vars.items():
    if value:
        env_str += '\n\t{:<{ln}} =  {}'.format(name, value, ln=env_maxlen)

env_vars_msg = '\n    ------------------------------------' \
               '\n    You already have environment variables:' \
               '{vars}'.format(vars=env_str) if env_str else ''

setup_arg('host', 's', 'vSphere service to connect to', env_var=v_host,
          required=not env_vars[v_host], default=env_vars[v_host],
          example='172.16.0.254')

setup_arg('user', 'u', 'User name to use when connecting to host',
          env_var=v_user, required=not env_vars[v_user],
          default=env_vars[v_user], example='administrator@vsphere.local')

setup_arg('password', 'p', 'Password to use when connecting to host',
          env_var=v_passw, required=not env_vars[v_passw],
          default=env_vars[v_passw], example='Qwer!1234')

setup_arg('port', 'o', 'Port to connect on', required=False, default=443)

setup_arg('datacenter', 'd', 'Datacenter, which cluster exists',
          env_var=v_dcenter, required=False,
          default=env_vars[v_dcenter] or 'Datacenter')

setup_arg('cluster', 'c', 'Cluster name, where check vswitch',
          required=not env_vars[v_cluster], default=env_vars[v_cluster],
          env_var=v_cluster, example='Cluster1')

setup_arg('vdswitch', 'v', 'Distributed virtual switch name, which must be '
                           'configured on all esxi in vcenter cluster',
          required=False, default='dvSwitch')

setup_arg('vmnic', 'n', 'Network interface, which must be attached to vds',
          required=True, example='vmnic1')

setup_arg('portgroup', 'g', 'Portgroup name, which must be configured on all '
                            'esxi in vcenter cluster',
          required=True, example='br100')

setup_arg('datastore', 'ds', 'Datastore, which cluster exists',
          required=not env_vars[v_datastore], default=env_vars[v_datastore],
          env_var=v_datastore, example='nfs')

setup_arg('suser', 'su', 'User name fot connect via ssh to esxi host',
          default='root')

setup_arg('spassword', 'sp', 'Password for connect via ssh to esxi host',
          default='swordfish')


help_host = func_args['host']['example'] or func_args['host']['default']
help_username = func_args['user']['example'] or func_args['user']['default']

help_passw = func_args['password']['example'] \
             or func_args['password']['default']

help_cluster = func_args['password']['example'] \
               or func_args['password']['default']


def def_parser(func_name, func_args_names):
    """
    Return subparser with func_name and parameters from func_args_names list.
    """
    tab = ' ' * 4

    func_help_msg = '{t}{}\n{t}Examples of usage:\n'.format('-' * 35, t=tab)
    func_help_msg += '{t}{t}{script} {func}'.format(script=script_name,
                                                    func=func_name, t=tab)

    can_export = ''
    rest_args = func_name
    for arg in func_args_names:
        params = func_args.get(arg, None)
        func_help_msg += ' -{short_f} "{example_value}"'.format(
                short_f=params['short_flag'],
                example_value=params['example'] or params['default']
        )

        if params.get('env_var', False):
            can_export += "\n{t}\texport {0}='{1}'".format(params['env_var'],
                                                           params['default'],
                                                           t=tab)
        else:
            if params.get('required', False):
                rest_args += ' -{short_f} "{example_value}"'.format(
                    short_f=params['short_flag'],
                    example_value=params['example'] or params['default']
                )

    func_help_msg += '\n{t}{t}{t}or{exp}\n{t}{t}{script} {rest}\n'.format(
            exp=can_export, script=script_name, rest=rest_args, t=tab
    ) + env_vars_msg

    sub_parser = subparser.add_parser(
            func_name, formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(func_help_msg)
    )

    for arg in func_args_names:
        params = func_args.get(arg, None)
        sub_parser.add_argument('-{flag}'.format(flag=params['short_flag']),
                                '--{flag}'.format(flag=params['long_flag']),
                                required=params.get('required', True),
                                default=params['default'],
                                help=params['help'])

    return sub_parser


help_msg = '''

    ------------------------------------
    You can use these environment variables:
        {v_ip:<{ln}} --host
        {v_us:<{ln}} --user
        {v_pw:<{ln}} --password
        {v_dc:<{ln}} --datacenter
        {v_ds:<{ln}} --datastore
        {v_cl:<{ln}} --cluster

    ------------------------------------
    Examples of usage:
        {script} cluster-list --host {ip} -u '{user}' -p '{passw}'
            or
        export {v_ip}=172.16.0.254
        export {v_us}='{user}'
        export {v_pw}='{passw}'
        {script} cluster-list

        {script} check-dvs-attached -s '{ip}'  -u '{user}' -d Datacenter
                                    -p '{passw}' -c {cl} -v dvSwitch -n vmnic1

        {script} check-esxi -s '{ip}' -o 443 -u '{user}' -d Datacenter
                            -p '{passw}' -c {cl}

        {script} check-portgroup -s '{ip}' -o 443 -u '{user}' -d Datacenter
                                 -p '{passw}' -c {cl} -g br100

        {script} check-datastore -s '{ip}' -o 443 -u '{user}' -d Datacenter
                                 -p '{passw}' -c {cl} -ds nfs

        {script} datastore-list -s '{ip}' -o 443 -u '{user}' -d Datacenter
                                -p '{passw}' -c {cl}

           '''.format(script=script_name, ip=help_host, user=help_username,
                      passw=help_passw, cl=help_cluster, ln=env_maxlen,
                      v_ip=v_host, v_us=v_user, v_pw=v_passw, v_dc=v_dcenter,
                      v_ds=v_datastore, v_cl=v_cluster) + env_vars_msg

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(help_msg))
subparser = parser.add_subparsers()


# *****************************************************************************
# list_clusters.py

def cluster_list(args):
    """Print list of clusters."""
    try:
        # workaround https://github.com/vmware/pyvmomi/issues/235
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port),
                                                sslContext=context)

        if not service_instance:
            log.error('Could not connect to the specified host using '
                      'specified username and password')
            return 1

        atexit.register(connect.Disconnect, service_instance)

        def list_clusters(service_instance, datacenter):
            content = service_instance.RetrieveContent()
            for dc in content.rootFolder.childEntity:
                if dc.name == datacenter:
                    host_folder = dc.hostFolder
                    for cluster in host_folder.childEntity:
                        print(cluster.name)

        list_clusters(service_instance, args.datacenter)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        sys.exit(1)

    return 0


# *****************************************************************************
# check_dvs_attached_to_hosts.py

def check_dvs_attached(args):
    """Return 0 if dvs is attached to hosts. Exit with 1 if not."""
    def get_dc_object(content, datacenter):
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                return dc
        log.error("Can not find dc '{dc_name}'".format(dc_name=datacenter))
        sys.exit(1)

    def get_vds_object(dc, vds):
        network_folder = dc.networkFolder
        for net in network_folder.childEntity:
            if isinstance(net, vim.DistributedVirtualSwitch):
                if net.name == vds:
                    return net
        log.error("dvSwitch '{vds}' not found".format(vds=vds))
        sys.exit(1)

    def get_hosts_in_vds(vds):
        return [host.config.host.name for host in vds.config.host]

    def get_hosts_in_cluster(dc, in_cluster):
        host_folder = dc.hostFolder
        for cluster in host_folder.childEntity:
            if cluster.name == in_cluster:
                return [host.name for host in cluster.host]
        log.error("Cluster '{cl_name}' empty".format(cl_name=in_cluster))
        sys.exit(1)

    def check_all_cluster_host_in_vds(vds_hosts, cluster_hosts, cluster,
                                      vdswitch):
        host_not_in_vds = set(cluster_hosts) - set(vds_hosts)
        if host_not_in_vds:
            log.error("In cluster '{cl_name}' on dvSwitch '{vds}' not found "
                      "hosts:".format(cl_name=cluster, vds=vdswitch))
            for host in host_not_in_vds:
                log.error("  {host}".format(host=host))
            sys.exit(1)

    def check_all_cluster_host_attached_vnic_to_vds(hosts, vds, vmnic):
        for host in vds.config.host:
            vmnic_attached = False
            hostname = host.config.host.name
            if hostname in hosts:
                nics = [nic.pnicDevice for nic in host.config.backing.pnicSpec]
                if vmnic in nics:
                    vmnic_attached = True
                if not vmnic_attached:
                    log.error("Host '{host}' not have attached nic '{nic}' to "
                              "dvSwitch '{vds}'".format(host=hostname,
                                                        nic=vmnic,
                                                        vds=vds.name))
                    sys.exit(1)
                extra_nic = set(nics) - {vmnic}
                if extra_nic:
                    print("Host '{host}' have extra nic '{nic}' attached to "
                          "dvSwitch '{vds}'".format(host=hostname,
                                                    nic=','.join(extra_nic),
                                                    vds=vds.name))

    try:
        # workaround https://github.com/vmware/pyvmomi/issues/235
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port),
                                                sslContext=context)

        if not service_instance:
            log.error("Could not connect to the specified host using "
                      "specified username and password")
            sys.exit(1)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        dc = get_dc_object(content, args.datacenter)
        vds = get_vds_object(dc, args.vdswitch)
        hosts_in_cluster = get_hosts_in_cluster(dc, args.cluster)
        hosts_in_vds = get_hosts_in_vds(vds)

        check_all_cluster_host_in_vds(hosts_in_vds, hosts_in_cluster,
                                      args.cluster, args.vdswitch)
        check_all_cluster_host_attached_vnic_to_vds(hosts_in_cluster,
                                                    vds, args.vmnic)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        sys.exit(1)

    return 0


# *****************************************************************************
# check_esxi.py

def check_esxi(args):
    """Return 0 if esxi is connected to controller. Exit with 1 if not."""
    def get_dc_object(content, datacenter):
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                return dc
        log.error("Can not find dc '{dc_name}'".format(dc_name=datacenter))
        sys.exit(1)

    def get_hosts_in_cluster(dc, in_cluster):
        host_folder = dc.hostFolder
        for cluster in host_folder.childEntity:
            if cluster.name == in_cluster:
                return [host.name for host in cluster.host]
        log.error("Cluster '{cl_name}' empty".format(cl_name=in_cluster))
        sys.exit(1)

    def exec_command(host, user, password, cmd):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=password, timeout=3)
        (ssh_stdin, ssh_stdout, ssh_stderr) = ssh.exec_command(cmd)
        out = ssh_stdout.read()
        ssh.close()
        return out

    def check_esxi_connect_to_controller(hosts, user, password):
        def check_netcpad(host, user, password, print_error=False):
            cmd = r"esxcli network ip connection list| grep tcp | grep 1234|" \
                  r"grep ESTABLISHED"
            out = exec_command(host, user, password, cmd)
            if not out:
                if print_error:
                    log.error("Host '{host}' not connected to nsxv "
                              "controller".format(host=host))
                return False
            return True

        def restart_netcpad(host, user, password):
            cmd = r"/etc/init.d/netcpad restart || /etc/init.d/netcpad start"
            log.error("Host '{host}', try restart netcpad".format(host=host))
            exec_command(host, user, password, cmd)

        for host in hosts:
            if not check_netcpad(host, user, password):
                restart_netcpad(host, user, password)
                if check_netcpad(host, user, password, True):
                    print('Host {host} reconnected to nsxv '
                          'controller'.format(host=host))
                else:
                    print('Host {host} NOT reconnected to nsxv '
                          'controller'.format(host=host))

    try:
        # workaround https://github.com/vmware/pyvmomi/issues/235
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port),
                                                sslContext=context)

        if not service_instance:
            log.error("Could not connect to the specified host using "
                      "specified username and password")
            sys.exit(1)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        dc = get_dc_object(content, args.datacenter)
        hosts_in_cluster = get_hosts_in_cluster(dc, args.cluster)
        check_esxi_connect_to_controller(hosts_in_cluster, args.suser,
                                         args.spassword)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        sys.exit(1)

    return 0


# *****************************************************************************
# check_portgroup_on_cluster.py

def check_portgroup(args):
    """Return 0 if portgroup is configured on cluster. Exit with 1 if not."""
    def check_portgroup_configured(service_instance, datacenter, in_cluster,
                                   portgroup):
        bad_exit = False
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                host_folder = dc.hostFolder
            for cluster in host_folder.childEntity:
                if cluster.name == in_cluster:
                    for esxi in cluster.host:
                        if portgroup not in [pg.name for pg in esxi.network]:
                            bad_exit = True
                            log.error("On esxi '{esxi}' portgroup '{portgr}' "
                                      "not found".format(esxi=esxi.name,
                                                         portgr=portgroup))
                    if bad_exit:
                        sys.exit(1)
        return 0

    try:
        # workaround https://github.com/vmware/pyvmomi/issues/235
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port),
                                                sslContext=context)

        if not service_instance:
            log.error("Could not connect to the specified host using "
                      "specified username and password")
            sys.exit(1)

        atexit.register(connect.Disconnect, service_instance)

        return check_portgroup_configured(service_instance, args.datacenter,
                                          args.cluster, args.portgroup)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        sys.exit(1)


# *****************************************************************************
# check_shared_datastore_on_cluster.py

def check_datastore(args):
    """Return 0 if datastore is configured on cluster. Exit with 1 if not."""
    def check_storage_configured(service_instance, datacenter, in_cluster,
                                 datastore):
        bad_exit = False
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                host_folder = dc.hostFolder
            for cluster in host_folder.childEntity:
                if cluster.name == in_cluster:
                    for esxi in cluster.host:
                        if datastore not in [ds.name for ds in esxi.datastore]:
                            log.error("On esxi '{esxi}' datastore '{ds}' not "
                                      "found".format(esxi=esxi.name,
                                                     ds=datastore))
                            bad_exit = True
                if bad_exit:
                    sys.exit(1)
        return 0

    def write_test_datastore(service_instance, datacenter, datastore, vcenter):
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                if datastore not in [ds.name for ds in dc.datastore]:
                    log.error("Datastore '{ds}' not found on '{dc}' "
                              "datacenter".format(ds=datastore, dc=datacenter))
                    sys.exit(1)

        # Build the url to put the file - https://hostname:port/resource?params
        resource = "/folder/test_upload"
        params = {"dsName": datastore,
                  "dcPath": datacenter}
        http_url = "https://" + vcenter + ":443" + resource

        # Get the cookie built from the current session
        client_cookie = service_instance._stub.cookie
        # Break apart the cookie into it's component parts - This is more than
        # is needed, but a good example of how to break apart the cookie
        # anyways. The verbosity makes it clear what is happening.
        cookie_name = client_cookie.split("=", 1)[0]
        cookie_value = client_cookie.split("=", 1)[1].split(";", 1)[0]
        cookie_path = client_cookie.split("=", 1)[1].split(";", 1)[1].split(
            ";", 1)[0].lstrip()
        cookie_text = " " + cookie_value + "; $" + cookie_path
        # Make a cookie
        cookie = dict()
        cookie[cookie_name] = cookie_text

        # Get the request headers set up
        headers = {'Content-Type': 'application/octet-stream'}

        # Get the file to upload ready, extra protection by using with against
        # leaving open threads
        # Connect and upload the file
        request = requests.put(http_url,
                               params=params,
                               data='Test upload file',
                               headers=headers,
                               cookies=cookie,
                               verify=False)
        if not request.ok:
            log.error("Can not write test file to datastore "
                      "'{ds}'".format(ds=datastore))
            sys.exit(1)

    try:
        # workaround https://github.com/vmware/pyvmomi/issues/235
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port),
                                                sslContext=context)

        if not service_instance:
            log.error("Could not connect to the specified host using "
                      "specified username and password")
            sys.exit(1)

        atexit.register(connect.Disconnect, service_instance)

        write_test_datastore(service_instance, args.datacenter,
                             args.datastore, args.host)
        return check_storage_configured(service_instance, args.datacenter,
                                        args.cluster, args.datastore)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        sys.exit(1)


# *****************************************************************************
# list_datastore_in_cluster.py

def datastore_list(args):
    """Print list of datastores."""
    def list_datastore(service_instance, datacenter, in_cluster):
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            # if dc.name == datacenter:
                # host_folder = dc.hostFolder
            host_folder = dc.hostFolder
            for cluster in host_folder.childEntity:
                if cluster.name == in_cluster:
                    print("In cluster '{cl_name}'".format(cl_name=in_cluster))
                    for esxi in cluster.host:
                        print("  On esxi '{esxi}' "
                              "datastores:".format(esxi=esxi.name))
                        for ds in esxi.datastore:
                            print("    '{ds}'".format(ds=ds.name))
                    break
        return

    try:
        # workaround https://github.com/vmware/pyvmomi/issues/235
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=int(args.port),
                                                sslContext=context)

        if not service_instance:
            log.error("Could not connect to the specified host using "
                      "specified username and password")
            sys.exit(1)

        atexit.register(connect.Disconnect, service_instance)

        list_datastore(service_instance, args.datacenter, args.cluster)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        sys.exit(1)

    return 0


cl_parser = def_parser('cluster-list',
                       ['host', 'port', 'user', 'password', 'datacenter'])

dac_parser = def_parser('check-dvs-attached',
                        ['host', 'port', 'user', 'password', 'datacenter',
                         'cluster', 'vdswitch', 'vmnic'])

ce_parser = def_parser('check-esxi',
                       ['host', 'port', 'user', 'password', 'datacenter',
                        'cluster', 'suser', 'spassword'])

cp_parser = def_parser('check-portgroup',
                       ['host', 'port', 'user', 'password', 'datacenter',
                        'cluster', 'portgroup'])

cd_parser = def_parser('check-datastore',
                       ['host', 'port', 'user', 'password', 'datacenter',
                        'cluster', 'datastore'])

dl_parser = def_parser('datastore-list',
                       ['host', 'port', 'user', 'password', 'datacenter',
                        'cluster'])

cl_parser.set_defaults(func=cluster_list)
dac_parser.set_defaults(func=check_dvs_attached)
ce_parser.set_defaults(func=check_esxi)
cp_parser.set_defaults(func=check_portgroup)
cd_parser.set_defaults(func=check_datastore)
dl_parser.set_defaults(func=datastore_list)


if __name__ == '__main__':
    args = parser.parse_args()
    exit(args.func(args))
