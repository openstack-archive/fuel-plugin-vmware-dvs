#!/usr/bin/env python3
#    Copyright 2013 - 2016 Mirantis, Inc.
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

import argparse
import atexit
import logging as log
import paramiko
import requests
import textwrap
import ssl
import sys

from os import environ
from pyVim import connect
from pyVmomi import vmodl, vim

requests.packages.urllib3.disable_warnings()
log.basicConfig(format='%(levelname)s: %(message)s', level=log.ERROR)


def ssl_connect(args):
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
            return sys.exit(1)

        atexit.register(connect.Disconnect, service_instance)

        return service_instance

    except vmodl.MethodFault as e:
        log.error('Caught vmodl fault: ' + e.msg)
        sys.exit(1)


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


def cluster_list(args):
    """Print list of clusters.

    from list_clusters.py"""

    service_instance = ssl_connect(args)

    def list_clusters(service_instance, datacenter):
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                host_folder = dc.hostFolder
                for cluster in host_folder.childEntity:
                    print(cluster.name)

    list_clusters(service_instance, args.datacenter)

    return 0


def check_dvs_attached(args):
    """Return 0 if dvs is attached to hosts. Exit with 1 if not.

    from check_dvs_attached_to_hosts.py"""

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
            hostname = host.config.host.name
            if hostname in hosts:
                nics = [nic.pnicDevice for nic in host.config.backing.pnicSpec]
                if vmnic not in nics:
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

    service_instance = ssl_connect(args)

    content = service_instance.RetrieveContent()
    dc = get_dc_object(content, args.datacenter)
    vds = get_vds_object(dc, args.vdswitch)
    hosts_in_cluster = get_hosts_in_cluster(dc, args.cluster)
    hosts_in_vds = get_hosts_in_vds(vds)

    check_all_cluster_host_in_vds(hosts_in_vds, hosts_in_cluster,
                                  args.cluster, args.vdswitch)
    check_all_cluster_host_attached_vnic_to_vds(hosts_in_cluster,
                                                vds, args.vmnic)

    return 0


def check_esxi(args):
    """Return 0 if esxi is connected to controller. Exit with 1 if not.

    from check_esxi.py"""

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

    service_instance = ssl_connect(args)

    content = service_instance.RetrieveContent()
    dc = get_dc_object(content, args.datacenter)
    hosts_in_cluster = get_hosts_in_cluster(dc, args.cluster)
    check_esxi_connect_to_controller(hosts_in_cluster, args.suser,
                                     args.spassword)

    return 0


def check_portgroup(args):
    """Return 0 if portgroup is configured on cluster. Exit with 1 if not.

    from check_portgroup_on_cluster.py"""

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

    service_instance = ssl_connect(args)

    return check_portgroup_configured(service_instance, args.datacenter,
                                      args.cluster, args.portgroup)


def check_datastore(args):
    """Return 0 if datastore is configured on cluster. Exit with 1 if not.

    from check_shared_datastore_on_cluster.py"""

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

    service_instance = ssl_connect(args)

    write_test_datastore(service_instance, args.datacenter,
                         args.datastore, args.host)
    return check_storage_configured(service_instance, args.datacenter,
                                    args.cluster, args.datastore)


def datastore_list(args):
    """Print list of datastores.

    list_datastore_in_cluster.py"""

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

    service_instance = ssl_connect(args)

    list_datastore(service_instance, args.datacenter, args.cluster)

    return 0


_script_name = sys.argv[0]

# settings for help message formatting
_ft = {
    't': ' ' * 4,  # tab
    's': '-' * 35  # separator
}

_func_args = {}  # information about parameters of functions
_env_vars = {}  # information about environment variables


def setup_env_var(name):
    """Save env variable info to the _env_vars list."""

    _env_vars[name] = environ.get(name, False)
    return name


def setup_arg(name, short_flag, help, required=True, default=None,
              env_var=None, example=None):
    """Save parameter info to the _func_args list."""

    _func_args[name] = {
        'short_flag': short_flag,
        'long_flag': name,
        'required': required,
        'default': default,
        'help': help,
        'env_var': env_var,
        'example': example,
    }


v_host = setup_env_var('VCENTER_IP')
v_user = setup_env_var('VCENTER_USERNAME')
v_passw = setup_env_var('VCENTER_PASSWORD')
v_dcenter = setup_env_var('VC_DATACENTER')
v_datastore = setup_env_var('VC_DATASTORE')
v_cluster = setup_env_var('VC_CLUSTER')


setup_arg('host', 's', 'vSphere service to connect to', env_var=v_host,
          required=not _env_vars[v_host], default=_env_vars[v_host],
          example='172.16.0.254')

setup_arg('user', 'u', 'User name to use when connecting to host',
          env_var=v_user, required=not _env_vars[v_user],
          default=_env_vars[v_user], example='administrator@vsphere.local')

setup_arg('password', 'p', 'Password to use when connecting to host',
          env_var=v_passw, required=not _env_vars[v_passw],
          default=_env_vars[v_passw], example='Qwer!1234')

setup_arg('port', 'o', 'Port to connect on', required=False, default=443)

setup_arg('datacenter', 'd',
          'Datacenter, which cluster exists',
          env_var=v_dcenter,
          required=False,
          default=_env_vars[v_dcenter] or 'Datacenter')

setup_arg('cluster', 'c', 'Cluster name, where check vswitch',
          required=not _env_vars[v_cluster], default=_env_vars[v_cluster],
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
          required=not _env_vars[v_datastore], default=_env_vars[v_datastore],
          env_var=v_datastore, example='nfs')

setup_arg('suser', 'su', 'User name fot connect via ssh to esxi host',
          required=False, default='root')

setup_arg('spassword', 'sp', 'Password for connect via ssh to esxi host',
          required=False, default='swordfish')


_functions = {}


def setup_func(name, params, func):
    """Save function info to the _functions list."""

    _functions[name] = {
        'params': params,
        'func': func
    }

_common_params = ['host', 'port', 'user', 'password', 'datacenter']


setup_func('cluster-list', _common_params, cluster_list)

setup_func('check-dvs-attached',
           _common_params + ['cluster', 'vdswitch', 'vmnic'],
           check_dvs_attached)

setup_func('check-esxi', _common_params + ['cluster', 'suser', 'spassword'],
           check_esxi)

setup_func('check-portgroup', _common_params + ['cluster', 'portgroup'],
           check_portgroup)

setup_func('check-datastore', _common_params + ['cluster', 'datastore'],
           check_datastore)

setup_func('datastore-list', _common_params + ['cluster'], datastore_list)


def _form_env_help():
    """
    Return message about exported and available env variables.
    """

    exported = '\n\n{t}{s}\n' \
               '{t}You already have environment variables:'.format(**_ft)

    available = ''

    # length of the longest available env variable name
    av_var_maxlen = max(map(len, _env_vars)) + 1

    # length of the longest exported env variable name
    ex_var_mlen = max(map(len, filter(lambda x: _env_vars[x], _env_vars))) + 1

    for name, value in sorted(_env_vars.items()):
        if value:
            exported += '\n{t}{t}{name:<{ln}} =  {value}'.format(
                    name=name, value=value, ln=ex_var_mlen, **_ft
            )

        # corresponding parameter for env name
        p_name = filter(lambda x: _func_args[x]['env_var'] == name, _func_args)

        available += '{t}{t}{name:<{ln}}  --{param}\n'.format(
            name=name, param=list(p_name)[0], ln=av_var_maxlen, **_ft
        )

    return exported, available

_env_vars_msg, _env_available = _form_env_help()


def _form_func_help(func_name, with_env=True):
    """
    Return example of usage for function.

    with_env parameter adds examples for env variables export
    """

    func_call = '{t}{t}{script} {func}'.format(script=_script_name,
                                               func=func_name, **_ft)
    arg_example = " {flag} '{example}'"

    msg = '{func_call}'.format(func_call=func_call, **_ft)

    func_params = _functions[func_name]['params']

    for arg in sorted(func_params):
        params = _func_args.get(arg, None)
        msg += arg_example.format(
                flag='-' + params['short_flag'],
                example=params['example'] or params['default']
        )

    if with_env:
        msg += '\n{t}{t}{t}or\n'.format(**_ft)
        rest_args = ''  # required arguments without env variable
        for arg in sorted(func_params):
            params = _func_args.get(arg, None)

            if params.get('env_var', False):
                msg += "{t}{t}export {name}='{value}'\n".format(
                        name=params['env_var'],
                        value=params['example'] or params['default'], **_ft
                )
            else:
                if params.get('required', False):
                    rest_args += arg_example.format(
                            flag='-' + params['short_flag'],
                            example=params['example'] or params['default']
                    )
        msg += func_call + rest_args + _env_vars_msg

    return msg


def _def_parser(func_name):
    """
    Return subparser with func_name and parameters from func_args_names list.
    """

    func_params = _functions[func_name]['params']

    help_msg = '{t}{s}\n' \
               '{t}Examples of usage:\n' \
               '{func_call}'.\
        format(func_call=_form_func_help(func_name), **_ft)

    sub_parser = _subparser.add_parser(
            func_name, formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.indent(help_msg, '')
    )

    for arg in sorted(func_params):
        params = _func_args.get(arg, None)
        sub_parser.add_argument('-{flag}'.format(flag=params['short_flag']),
                                '--{flag}'.format(flag=params['long_flag']),
                                required=params.get('required', True),
                                default=params['default'],
                                help=params['help'])

    sub_parser.set_defaults(func=_functions[func_name]['func'])

    return sub_parser


def _form_help_msg():
    msg = '\n{t}{s}\n' \
          '{t}You can use these environment variables:\n' \
          '{vars}\n' \
          '{t}{s}\n' \
          '{t}Examples of usage:\n'.format(vars=_env_available, **_ft)

    for func in sorted(_functions):
        msg += _form_func_help(func, False) + '\n\n'

    msg += _env_vars_msg

    return msg


_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.indent(_form_help_msg(), '')
)

_subparser = _parser.add_subparsers()

for _func in _functions:
    _def_parser(_func)


if __name__ == '__main__':
    args = _parser.parse_args()
    exit(args.func(args))
