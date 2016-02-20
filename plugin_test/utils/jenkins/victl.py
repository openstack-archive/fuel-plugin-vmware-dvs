#!/usr/bin/env python3
"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import argparse
import atexit
import logging as log
import ssl
import sys
import textwrap

from os import environ

import paramiko

from pyVim import connect

from pyVmomi import vim
from pyVmomi import vmodl

import requests

requests.packages.urllib3.disable_warnings()
log.getLogger("requests").setLevel(log.WARNING)
log.basicConfig(format='%(message)s', level=log.INFO)  # %(levelname)s:


class NotFoundException(Exception):
    """Raise when some object cannot be found."""

    pass


class Victl(object):
    """VMware base actions."""

    _service_instance = None
    content = None

    def __init__(self, host, user, password, port):
        """Create ssl context."""
        try:
            # workaround https://github.com/vmware/pyvmomi/issues/235
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
            context.verify_mode = ssl.CERT_NONE
            self._service_instance = connect.SmartConnect(host=host,
                                                          user=user,
                                                          pwd=password,
                                                          port=int(port),
                                                          sslContext=context)

            if not self._service_instance:
                raise Exception('Could not connect to the specified host using'
                                ' specified username and password')

            atexit.register(connect.Disconnect, self._service_instance)

            self.content = self._service_instance.RetrieveContent()

        except vmodl.MethodFault as e:
            raise Exception('Caught vmodl fault: ' + e.msg)

    def get_dc_object(self, datacenter):
        """Return datacenter object with specified name."""
        for dc in self.content.rootFolder.childEntity:
            if dc.name == datacenter:
                return dc

        raise NotFoundException("Can not find dc "
                                "'{dc_name}'".format(dc_name=datacenter))

    def get_cluster_hosts(self, dc, cluster):
        """Return list of hosts names in specified cluster."""
        host_folder = dc.hostFolder
        for _cluster in host_folder.childEntity:
            if _cluster.name == cluster:
                return [host.name for host in _cluster.host]

        raise Exception("Cluster '{cl_name}' is empty".format(cl_name=cluster))

    def get_cluster_hosts_objects(self, dc, cluster):
        """Return list of hosts names in specified cluster."""
        host_folder = dc.hostFolder
        for _cluster in host_folder.childEntity:
            if _cluster.name == cluster:
                return _cluster.host

    def get_vds_object(self, dc, vds):
        """Return dvSwitch object with specified name."""
        network_folder = dc.networkFolder
        for net in network_folder.childEntity:
            if isinstance(net, vim.DistributedVirtualSwitch):
                if net.name == vds:
                    return net

        raise NotFoundException("dvSwitch '{vds}' not found".format(vds=vds))

    def get_vds_hosts(self, datacenter, vdswitch):
        """Return list of hosts names in specified dvSwitch."""
        dc = self.get_dc_object(datacenter)
        vds = inst.get_vds_object(dc, vdswitch)
        return [host.config.host.name for host in vds.config.host]

    def get_nics_for_hosts_in_vds(self, hosts, vds):
        """Return list of nics for specified hosts in dvSwitch."""
        nics = []
        for host in vds.config.host:
            if host.config.host.name in hosts:
                nics.append([nic.pnicDevice for nic
                             in host.config.backing.pnicSpec])

        return nics

    def get_clusters(self, datacenter):
        """Return list of clusters names in specified datacenter."""
        dc = self.get_dc_object(datacenter)
        host_folder = dc.hostFolder
        return [cluster.name for cluster in host_folder.childEntity]

    def _exec_command(self, host, user, password, cmd):
        """Execute command remotely and return output."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(host, username=user, password=password, timeout=3)
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read()
        except TypeError:
            raise Exception('There are no valid connections')
        finally:
            if client:
                client.close()
        return out

    def check_netcpad(self, host, user, password, print_error=False):
        """Check up whether connection with nsxv controller is established."""
        cmd = r"esxcli network ip connection list | grep tcp | grep 1234 | " \
              r"grep ESTABLISHED"
        out = self._exec_command(host, user, password, cmd)
        if not out:
            if print_error:
                raise Exception("Host '{host}' not connected to nsxv "
                                "controller".format(host=host))
            return False
        return True

    def restart_netcpad(self, host, user, password):
        """Restart netcpad."""
        log.info("Host '{host}', try restart netcpad".format(host=host))

        cmd = r"/etc/init.d/netcpad restart"
        self._exec_command(host, user, password, cmd)

    def check_portgroup_configured(self, datacenter, cluster, portgroup):
        """Check up whether portgroup is configured."""
        err = ''
        dc = self.get_dc_object(datacenter)
        hosts = self.get_cluster_hosts_objects(dc, cluster)
        for esxi in hosts:
            if portgroup not in [pg.name for pg in esxi.network]:
                err += "On esxi '{esxi}' portgroup '{portgr}' "\
                       "not found".format(esxi=esxi.name,
                                          portgr=portgroup)
        if err:
            raise NotFoundException(err)
        return True

    def check_storage_configured(self, datacenter, cluster, datastore):
        """Check up whether datastore is configured on cluster."""
        dc = self.get_dc_object(datacenter)
        hosts = self.get_cluster_hosts_objects(dc, cluster)

        err = {}

        for esxi in hosts:
            for ds in esxi.datastore:
                if ds.name == datastore:
                    break
            else:
                log.error('ERROR: On esxi "{esxi}" datastore "{ds}" is not '
                          'found'.format(esxi=esxi.name, ds=datastore))
                err[0] = 'Some datastores not found'
                continue

            for attached_host in ds.host:
                if attached_host.key == esxi:
                    break

            if attached_host.mountInfo.mounted:
                log.info('On esxi "{esxi}" datastore "{ds}" is mounted'
                         ''.format(ds=ds.name, esxi=esxi.name))
            else:
                log.error('ERROR: On esxi "{esxi}" datastore "{ds}" is NOT '
                          'mounted'.format(ds=ds.name, esxi=esxi.name))
                err[1] = 'Some datastores not mounted'

            if attached_host.mountInfo.accessible:
                log.info('On esxi "{esxi}" datastore "{ds}" is accessible'
                         ''.format(ds=ds.name, esxi=esxi.name))
            else:
                log.error('ERROR: On esxi "{esxi}" datastore "{ds}" is NOT '
                          'accessible'.format(ds=ds.name, esxi=esxi.name))
                err[2] = 'Some datastores not accessible'

        if err:
            raise NotFoundException('. '.join(err.values()))

        return True

    def write_test_datastore(self, datacenter, datastore, host):
        """Put the file with test data to specified datastore."""
        dc = self.get_dc_object(datacenter)
        if datastore not in [ds.name for ds in dc.datastore]:
            raise NotFoundException("Datastore '{ds}' not found on '{dc}' "
                                    "datacenter".format(ds=datastore,
                                                        dc=datacenter))

        # Build the url to put the file - https://hostname:port/resource?params
        resource = '/folder/test_upload'
        params = {'dsName': datastore, 'dcPath': datacenter}
        http_url = 'https://{vcenter}:443{resource}'.format(vcenter=host,
                                                            resource=resource)

        # Get the cookie built from the current session
        client_cookie = self._service_instance._stub.cookie
        # Break apart the cookie into it's component parts - This is more than
        # is needed, but a good example of how to break apart the cookie
        # anyways. The verbosity makes it clear what is happening.
        cookie_name = client_cookie.split('=', 1)[0]
        _path_etc = client_cookie.split('=', 1)[1]
        cookie_value = _path_etc.split(';', 1)[0]
        cookie_path = _path_etc.split(';', 1)[1].split(';', 1)[0].lstrip()
        cookie_text = " {value}; ${path}".format(value=cookie_value,
                                                 path=cookie_path)
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
            raise Exception("Can not write test file to datastore "
                            "'{ds}'".format(ds=datastore))

        return True


def cluster_list(args, inst):
    """Print list of clusters."""
    clusters = inst.get_clusters(args.datacenter)
    for cluster in clusters:
        log.info(cluster)

    return 0


def check_dvs_attached(args, inst):
    """Return 0 if dvs is attached to hosts."""
    dc = inst.get_dc_object(args.datacenter)
    vds = inst.get_vds_object(dc, args.vdswitch)
    hosts_in_cluster = inst.get_cluster_hosts(dc, args.cluster)
    hosts_in_vds = inst.get_vds_hosts(args.datacenter, args.vdswitch)

    # Check up whether all cluster hosts are in dvSwitch
    host_not_in_vds = set(hosts_in_cluster) - set(hosts_in_vds)
    if host_not_in_vds:
        err = "In cluster '{cl_name}' on dvSwitch '{vds}' not found " \
              "hosts:".format(cl_name=args.cluster, vds=args.vdswitch)
        for host in host_not_in_vds:
            err += "\n  {host}".format(host=host)
        raise NotFoundException(err)

    # Check up whether all cluster hosts have vmnic attached
    nics = inst.get_nics_for_hosts_in_vds(hosts_in_cluster, vds)
    for hostname, host_nics in zip(hosts_in_cluster, nics):
        if args.vmnic not in host_nics:
            raise Exception("Host '{host}' has not attached nic '{nic}' to "
                            "dvSwitch '{vds}'".format(host=hostname,
                                                      nic=args.vmnic,
                                                      vds=vds.name))
        extra_nic = set(host_nics) - {args.vmnic}
        if extra_nic:
            log.info("Host '{host}' has extra nic '{nic}' attached to "
                     "dvSwitch '{vds}'".format(host=hostname,
                                               nic=','.join(extra_nic),
                                               vds=vds.name))

    return 0


def check_esxi(args, inst):
    """Return 0 if esxi is connected to controller."""
    dc = inst.get_dc_object(args.datacenter)
    hosts_in_cluster = inst.get_cluster_hosts(dc, args.cluster)

    # Check up whether esxi is connected to controller
    for host in hosts_in_cluster:
        if not inst.check_netcpad(host, args.user, args.password):
            inst.restart_netcpad(host, args.user, args.password)

            if inst.check_netcpad(host, args.user, args.password, True):
                log.info('Host {host} reconnected to nsxv '
                         'controller'.format(host=host))
            else:
                log.info('Host {host} NOT reconnected to nsxv '
                         'controller'.format(host=host))

    return 0


def check_portgroup(args, inst):
    """Return 0 if portgroup is configured on cluster."""
    if inst.check_portgroup_configured(args.datacenter, args.cluster,
                                       args.portgroup):
        return 0


def check_datastore(args, inst):
    """Return 0 if datastore is configured on cluster."""
    inst.write_test_datastore(args.datacenter, args.datastore, args.host)
    if inst.check_storage_configured(args.datacenter, args.cluster,
                                     args.datastore):
        return 0


def datastore_list(args, inst):
    """Print list of datastores."""
    dc = inst.get_dc_object(args.datacenter)
    hosts = inst.get_cluster_hosts_objects(dc, args.cluster)
    log.info("In cluster '{cl_name}'".format(cl_name=args.cluster))

    for esxi in hosts:
        log.info("  On esxi '{esxi}' datastores:".format(esxi=esxi.name))

        for ds in esxi.datastore:
            log.info("    '{ds}'".format(ds=ds.name))

    return 0


_script_name = sys.argv[0]  # is used for help message

# settings for help message formatting
_ft = {
    't': ' ' * 4,  # tab
    's': '-' * 35  # separator
}

_func_args = {}  # information about parameters of functions
_env_vars = {}  # information about environment variables


def setup_env_var(name):
    """Save env variable info to the _env_vars dictionary."""
    _env_vars[name] = environ.get(name, False)
    return name


def setup_arg(name, short_flag, help, required=True, default=None,
              env_var=None, example=None):
    """Save parameter info to the _func_args dictionary."""
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


setup_arg(name='host',
          short_flag='s',
          help='vSphere service to connect to',
          env_var=v_host,
          required=not _env_vars[v_host],
          default=_env_vars[v_host],
          example='172.16.0.254')

setup_arg(name='user',
          short_flag='u',
          help='User name to use when connecting to host',
          env_var=v_user,
          required=not _env_vars[v_user],
          default=_env_vars[v_user],
          example='administrator@vsphere.local')

setup_arg(name='password',
          short_flag='p',
          help='Password to use when connecting to host',
          env_var=v_passw,
          required=not _env_vars[v_passw],
          default=_env_vars[v_passw],
          example='Qwer!1234')

setup_arg(name='port',
          short_flag='o',
          help='Port to connect on',
          required=False,
          default=443)

setup_arg(name='datacenter',
          short_flag='d',
          help='Datacenter, which cluster exists',
          env_var=v_dcenter,
          required=False,
          default=_env_vars[v_dcenter] or 'Datacenter')

setup_arg(name='cluster',
          short_flag='c',
          help='Cluster name, where check vswitch',
          required=not _env_vars[v_cluster],
          default=_env_vars[v_cluster],
          env_var=v_cluster, example='Cluster1')

setup_arg(name='vdswitch',
          short_flag='v',
          help='Distributed virtual switch name, which must be configured on '
               'all esxi in vcenter cluster',
          required=False,
          default='dvSwitch')

setup_arg(name='vmnic',
          short_flag='n',
          help='Network interface, which must be attached to vds',
          required=True,
          example='vmnic1')

setup_arg(name='portgroup',
          short_flag='g',
          help='Portgroup name, which must be configured on all esxi in '
               'vcenter cluster',
          required=True,
          example='br100')

setup_arg(name='datastore',
          short_flag='ds',
          help='Datastore, which cluster exists',
          required=not _env_vars[v_datastore],
          default=_env_vars[v_datastore],
          env_var=v_datastore,
          example='nfs')

setup_arg(name='suser',
          short_flag='su',
          help='User name fot connect via ssh to esxi host',
          required=False,
          default='root')

setup_arg(name='spassword',
          short_flag='sp',
          help='Password for connect via ssh to esxi host',
          required=False,
          default='swordfish')


_functions = {}  # information about functions


def setup_func(name, params, func):
    """Save function info to the _functions dictionary."""
    _functions[name] = {
        'params': params,
        'func': func
    }

_common_params = ['host', 'port', 'user', 'password', 'datacenter']


setup_func(name='cluster-list',
           params=_common_params,
           func=cluster_list)

setup_func(name='check-dvs-attached',
           params=_common_params + ['cluster', 'vdswitch', 'vmnic'],
           func=check_dvs_attached)

setup_func(name='check-esxi',
           params=_common_params + ['cluster', 'suser', 'spassword'],
           func=check_esxi)

setup_func(name='check-portgroup',
           params=_common_params + ['cluster', 'portgroup'],
           func=check_portgroup)

setup_func(name='check-datastore',
           params=_common_params + ['cluster', 'datastore'],
           func=check_datastore)

setup_func(name='datastore-list',
           params=_common_params + ['cluster'],
           func=datastore_list)


def _form_env_help():
    """Return message about exported and available env variables."""
    exported = '\n\n{t}{s}\n' \
               '{t}You already have environment variables:'.format(**_ft)

    available = ''  # supported variables to get them from env

    # length of the longest available env variable name
    av_var_maxlen = max(map(len, _env_vars)) + 1

    defined = filter(lambda x: _env_vars[x], _env_vars)
    try:
        # length of the longest exported env variable name
        ex_var_mlen = max(map(len, defined)) + 1
    except ValueError:
        ex_var_mlen = 0

    for name, value in sorted(_env_vars.items()):
        if value:
            # adding info about exported variables
            exported += '\n{t}{t}{name:<{ln}} =  {value}'.format(
                name=name, value=value, ln=ex_var_mlen, **_ft
            )

        # corresponding parameter name for env name
        p_name = filter(lambda x: _func_args[x]['env_var'] == name, _func_args)

        # adding info about variables which user can export
        available += '{t}{t}{name:<{ln}}  --{param}\n'.format(
            name=name, param=list(p_name)[0], ln=av_var_maxlen, **_ft
        )

    if not ex_var_mlen:
        exported = ''

    return exported, available

_env_vars_msg, _env_available = _form_env_help()


def _form_func_help(func_name, with_env=True):
    """Return example of usage for function.

    :param with_env: adds examples for env variables export
    """
    # example of function calling
    func_call = '{t}{t}{script} {func}'.format(script=_script_name,
                                               func=func_name, **_ft)
    # template for function arguments example
    arg_example = " {flag} '{example}'"

    msg = '{func_call}'.format(func_call=func_call, **_ft)  # usage message

    func_params = _functions[func_name]['params']

    for arg in sorted(func_params):
        params = _func_args.get(arg, None)
        # adding all arguments examples
        msg += arg_example.format(
            flag='-' + params['short_flag'],
            example=params['example'] or params['default']
        )

    if with_env:
        # example with exported variables
        msg += '\n{t}{t}{t}or\n'.format(**_ft)

        rest_args = ''  # required arguments without env variable

        for arg in sorted(func_params):
            params = _func_args.get(arg, None)

            if params.get('env_var', False):  # if parameter has env variable
                msg += "{t}{t}export {name}='{value}'\n".format(
                    name=params['env_var'],
                    value=params['example'] or params['default'], **_ft
                )
            elif params.get('required', False):
                rest_args += arg_example.format(
                    flag='-' + params['short_flag'],
                    example=params['example'] or params['default']
                )
        msg += func_call + rest_args + _env_vars_msg

    return msg


def _def_parser(func_name):
    """Return subparser with func_name and func_args_names parameters."""
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
    """Return usage message for the program."""
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
    if len(sys.argv) == 1:
        _parser.print_help()
        sys.exit(0)

    try:
        inst = Victl(args.host, args.user, args.password, args.port)
        res = args.func(args, inst)
    except Exception as e:
        log.error('ERROR: {msg}'.format(msg=e))
        res = 1

    sys.exit(res)
