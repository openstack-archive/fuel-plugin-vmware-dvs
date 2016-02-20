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

parser = argparse.ArgumentParser(epilog='You can use these variables: '
                                        'VCENTER_IP, VCENTER_USERNAME, '
                                        'VCENTER_PASSWORD, VC_DATACENTER,'
                                        'VC_DATASTORE, VC_CLUSTER')
subparser = parser.add_subparsers()

v_host = environ.get('VCENTER_IP', False)
v_user = environ.get('VCENTER_USERNAME', False)
v_passw = environ.get('VCENTER_PASSWORD', False)
v_dcenter = environ.get('VC_DATACENTER', False)
v_datastore = environ.get('VC_DATASTORE', False)
v_cluster = environ.get('VC_CLUSTER', False)
# v_port = environ.get('?', False)
# v_vdswitch = environ.get('?', False)
# v_vmnic = environ.get('?', False)
# v_suser = environ.get('?', False)
# v_spassw = environ.get('?', False)
# v_portgroup = environ.get('?', False)


# *****************************************************************************
# list_clusters.py

def cluster_list(args):
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
            return 1

        atexit.register(connect.Disconnect, service_instance)

        def list_clusters(service_instance, datacenter):
            content = service_instance.RetrieveContent()
            for dc in content.rootFolder.childEntity:
                # if dc.name == datacenter:
                #     hostFolder = dc.hostFolder
                hostFolder = dc.hostFolder
                for cluster in hostFolder.childEntity:
                    print(cluster.name)

        list_clusters(service_instance, args.datacenter)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        return 1

    return 0

cl_parser = subparser.add_parser('cluster-list')

# because -h is reserved for 'help' we use -s for service
cl_parser.add_argument('-s', '--host', required=not v_host, default=v_host,
                       help='vSphere service to connect to')

# because we want -p for password, we use -o for port
cl_parser.add_argument('-o', '--port', type=int, default=443,
                       help='Port to connect on')

cl_parser.add_argument('-u', '--user', required=not v_user, default=v_user,
                       help='User name to use when connecting to host')

cl_parser.add_argument('-p', '--password', required=not v_passw,
                       default=v_passw,
                       help='Password to use when connecting to host')

cl_parser.add_argument('-d', '--datacenter', default=v_dcenter or 'Datacenter',
                       help='Datacenter, which cluster exists')

cl_parser.set_defaults(func=cluster_list)


# *****************************************************************************
# check_dvs_attached_to_hosts.py

def check_dvs_attached(args):
    def get_dc_object(content, datacenter):
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                return dc
        log.error("Can not find dc '%s'" % datacenter)
        sys.exit(1)

    def get_vds_object(dc, vds):
        networkFolder = dc.networkFolder
        for net in networkFolder.childEntity:
            if isinstance(net, vim.DistributedVirtualSwitch):
                if net.name == vds:
                    return net
        log.error("dvSwitch '%s' not found" % vds)
        sys.exit(1)

    def get_hosts_in_vds(vds):
        return [host.config.host.name for host in vds.config.host]

    def get_hosts_in_cluster(dc, in_cluster):
        hostFolder = dc.hostFolder
        for cluster in hostFolder.childEntity:
            if cluster.name == in_cluster:
                return [host.name for host in cluster.host]
        log.error("Cluster '%s' empty" % in_cluster)
        sys.exit(1)

    def check_all_cluster_host_in_vds(vds_hosts, cluster_hosts, cluster,
                                      vdswitch):
        host_not_in_vds = set(cluster_hosts) - set(vds_hosts)
        if host_not_in_vds:
            log.error("In cluster '%s' on dvSwitch '%s' not found hosts:" %
                      (cluster, vdswitch))
            for host in host_not_in_vds:
                log.error("  %s" % host)
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
                    log.error("Host '%s' not have attached nic '%s' to "
                              "dvSwitch '%s'" % (hostname, vmnic, vds.name))
                    sys.exit(1)  # todo ?
                extra_nic = set(nics) - set([vmnic])
                if extra_nic:
                    print("Host '%s' have extra nic '%s' attached to "
                          "dvSwitch '%s'" %
                          (hostname, (',').join(extra_nic), vds.name))

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
            return 1

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
        return 1

    return 0

dac_parser = subparser.add_parser('check-dvs-attached')

# because -h is reserved for 'help' we use -s for service
dac_parser.add_argument('-s', '--host', required=not v_host, default=v_host,
                        help='vSphere service to connect to')

# because we want -p for password, we use -o for port
dac_parser.add_argument('-o', '--port', type=int, default=443,
                        help='Port to connect on')

dac_parser.add_argument('-u', '--user', required=not v_user, default=v_user,
                        help='User name to use when connecting to host')

dac_parser.add_argument('-p', '--password', required=not v_passw,
                        default=v_passw,
                        help='Password to use when connecting to host')

dac_parser.add_argument('-d', '--datacenter',
                        default=v_dcenter or 'Datacenter',
                        help='Datacenter, which cluster exists')

dac_parser.add_argument('-c', '--cluster', required=not v_cluster,
                        default=v_cluster,
                        help='Cluster name, where check vswitch')

dac_parser.add_argument('-v', '--vdswitch', default='dvSwitch',
                        help='Distributed virtual switch name, which must be '
                        'configured on all esxi in vcenter cluster')

dac_parser.add_argument('-n', '--vmnic', required=True,
                        help='Network interface, which must be '
                             'attached to vds')

dac_parser.add_argument('-l', '--list', required=False,
                        help='List all host attached to dvs with uplink vmnic')

dac_parser.set_defaults(func=check_dvs_attached)


# *****************************************************************************
# check_esxi.py

def check_esxi(args):
    def get_dc_object(content, datacenter):
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                return dc
        log.error("Can not find dc '%s'" % datacenter)
        sys.exit(1)

    def get_hosts_in_cluster(dc, in_cluster):
        hostFolder = dc.hostFolder
        for cluster in hostFolder.childEntity:
            if cluster.name == in_cluster:
                return [host.name for host in cluster.host]
        log.error("Cluster '%s' empty" % in_cluster)
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
                    log.error("Host '%s' not connected to nsxv controller"
                              % host)
                return False
            return True

        def restart_netcpad(host, user, password):
            cmd = r"/etc/init.d/netcpad restart || /etc/init.d/netcpad start"
            log.error("Host '%s',try restart netcpad" % host)
            exec_command(host, user, password, cmd)

        for host in hosts:
            if not check_netcpad(host, user, password):
                restart_netcpad(host, user, password)
                if check_netcpad(host, user, password, True):
                    print('Host %s reconnected to nsxv controller' % host)
                else:
                    print('Host %s NOT reconnected to nsxv controller'
                          % host)

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
            return 1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        dc = get_dc_object(content, args.datacenter)
        hosts_in_cluster = get_hosts_in_cluster(dc, args.cluster)
        check_esxi_connect_to_controller(hosts_in_cluster, args.suser,
                                         args.spassword)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        return 1

ce_parser = subparser.add_parser('check-esxi')

# because -h is reserved for 'help' we use -s for service
ce_parser.add_argument('-s', '--host', required=not v_host, default=v_host,
                       help='vSphere service to connect to')

# because we want -p for password, we use -o for port
ce_parser.add_argument('-o', '--port', type=int, default=443,
                       help='Port to connect on')

ce_parser.add_argument('-u', '--user', required=not v_user, default=v_user,
                       help='User name to use when connecting to host')

ce_parser.add_argument('-p', '--password', required=not v_passw,
                       default=v_passw,
                       help='Password to use when connecting to host')

ce_parser.add_argument('-d', '--datacenter', default=v_dcenter or 'Datacenter',
                       help='Datacenter, which cluster exists')

ce_parser.add_argument('-c', '--cluster', required=not v_cluster,
                       default=v_cluster,
                       help='Cluster name, where create vswitch')

ce_parser.add_argument('-su', '--suser', default='root',
                       help='User name fot connect via ssh to esxi host')

ce_parser.add_argument('-sp', '--spassword', default='swordfish',
                       help='Password for connect via ssh to esxi host')

ce_parser.set_defaults(func=check_esxi)


# *****************************************************************************
# check_portgroup_on_cluster.py

def check_portgroup(args):
    def check_portgroup_configured(service_instance, datacenter, in_cluster,
                                   portgroup):
        bad_exit = False
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                hostFolder = dc.hostFolder
            for cluster in hostFolder.childEntity:
                if cluster.name == in_cluster:
                    for esxi in cluster.host:
                        if not portgroup in [pg.name for pg in esxi.network]:
                            bad_exit = True
                            log.error("On esxi '%s' portgroup '%s' not found" %
                                      (esxi.name, portgroup))
                    if bad_exit:
                        return 1
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
            return 1

        atexit.register(connect.Disconnect, service_instance)

        return check_portgroup_configured(service_instance, args.datacenter,
                                          args.cluster, args.portgroup)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        return 1


cp_parser = subparser.add_parser('check-portgroup')

# because -h is reserved for 'help' we use -s for service
cp_parser.add_argument('-s', '--host', required=not v_host, default=v_host,
                       help='vSphere service to connect to')

# because we want -p for password, we use -o for port
cp_parser.add_argument('-o', '--port', type=int, default=443,
                       help='Port to connect on')

cp_parser.add_argument('-u', '--user', required=not v_user, default=v_user,
                       help='User name to use when connecting to host')

cp_parser.add_argument('-p', '--password', required=not v_passw,
                       default=v_passw,
                       help='Password to use when connecting to host')

cp_parser.add_argument('-d', '--datacenter', default=v_dcenter or 'Datacenter',
                       help='Datacenter, which cluster exists')

cp_parser.add_argument('-c', '--cluster', required=not v_cluster,
                       default=v_cluster,
                       help='Cluster name, where check vswitch')

cp_parser.add_argument('-g', '--portgroup', required=True,
                       help='Portgroup name, which must be configured on all '
                            'esxi in vcenter cluster')

cp_parser.set_defaults(func=check_portgroup)


# *****************************************************************************
# check_shared_datastore_on_cluster.py

def check_datastore(args):
    def check_storage_configured(service_instance, datacenter, in_cluster,
                                 datastore):
        bad_exit = False
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                hostFolder = dc.hostFolder
            for cluster in hostFolder.childEntity:
                if cluster.name == in_cluster:
                    for esxi in cluster.host:
                        if not datastore in [ds.name for ds in esxi.datastore]:
                            log.error("On esxi '%s' datastore '%s' not found" %
                                      (esxi.name, datastore))
                            bad_exit = True
                if bad_exit:
                    return 1
        return 0

    def write_test_datastore(service_instance, datacenter, datastore, vcenter):
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            if dc.name == datacenter:
                if not datastore in [ds.name for ds in dc.datastore]:
                    log.error("Datastore '%s' not found on '%s' datacenter" %
                              (datastore, datacenter))
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
            log.error("Can not write test file to datastore '%s'" % datastore)
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
            return 1

        atexit.register(connect.Disconnect, service_instance)

        write_test_datastore(service_instance, args.datacenter,
                             args.datastore, args.host)
        return check_storage_configured(service_instance, args.datacenter,
                                        args.cluster, args.datastore)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        return 1

cd_parser = subparser.add_parser('check-datastore')

# because -h is reserved for 'help' we use -s for service
cd_parser.add_argument('-s', '--host', required=not v_host, default=v_host,
                       help='vSphere service to connect to')

# because we want -p for password, we use -o for port
cd_parser.add_argument('-o', '--port', type=int, default=443,
                       help='Port to connect on')

cd_parser.add_argument('-u', '--user', required=not v_user, default=v_user,
                       help='User name to use when connecting to host')

cd_parser.add_argument('-p', '--password', required=not v_passw,
                       default=v_passw,
                       help='Password to use when connecting to host')

cd_parser.add_argument('-d', '--datacenter', default=v_dcenter or 'Datacenter',
                       help='Datacenter, which cluster exists')

cd_parser.add_argument('-c', '--cluster', required=not v_cluster,
                       default=v_cluster,
                       help='Cluster name, where check vswitch')

cd_parser.add_argument('-ds', '--datastore', required=True,
                       help='Portgroup name, which must be configured on all '
                            'esxi in vcenter cluster')

cd_parser.set_defaults(func=check_datastore)


# *****************************************************************************
# list_datastore_in_cluster.py

def datastore_list(args):
    def list_datastore(service_instance, datacenter, in_cluster):
        content = service_instance.RetrieveContent()
        for dc in content.rootFolder.childEntity:
            # if dc.name == datacenter:
                # hostFolder = dc.hostFolder
            hostFolder = dc.hostFolder
            for cluster in hostFolder.childEntity:
                if cluster.name == in_cluster:
                    print("In cluster '%s'" % in_cluster)
                    for esxi in cluster.host:
                        print("  On esxi '%s' datastores:" % (esxi.name))
                        for ds in esxi.datastore:
                            print("    '%s'" % ds.name)
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
            return 1

        atexit.register(connect.Disconnect, service_instance)

        list_datastore(service_instance, args.datacenter, args.cluster)

    except vmodl.MethodFault as e:
        log.error("Caught vmodl fault : " + e.msg)
        return 1

    return 0

dl_parser = subparser.add_parser('datastore-list')

# because -h is reserved for 'help' we use -s for service
dl_parser.add_argument('-s', '--host', required=not v_host, default=v_host,
                       help='vSphere service to connect to')

# because we want -p for password, we use -o for port
dl_parser.add_argument('-o', '--port', type=int, default=443,
                       help='Port to connect on')

dl_parser.add_argument('-u', '--user', required=not v_user, default=v_user,
                       help='User name to use when connecting to host')

dl_parser.add_argument('-p', '--password', required=not v_passw,
                       default=v_passw,
                       help='Password to use when connecting to host')

dl_parser.add_argument('-d', '--datacenter', default=v_dcenter or 'Datacenter',
                       help='Datacenter, which cluster exists')

dl_parser.add_argument('-c', '--cluster', required=not v_cluster,
                       default=v_cluster,
                       help='Cluster name, where check vswitch')

dl_parser.set_defaults(func=datastore_list)


if __name__ == '__main__':
    args = parser.parse_args()
    exit(args.func(args))
