#!/usr/bin/env python

import sys,subprocess
sys.path.append("/pkg/bin")
from ztp_helper import ZtpHelpers

def run_bash(cmd=None):
    ## In XR the default shell is bash, hence the name
    if cmd is not None:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        out, err = process.communicate()
    else:
        print "No bash command provided"

    status = process.returncode
    return {"status" : status, "output" : out}



def xr_to_linux_ifname(interface):

    interface_dict = {'Hu' : 'Hg', 'Te':'Tg', 'Fo' : 'Fg',
                      'Gi' : 'Gi', 'Tw': 'Tf', 'Mg': 'Mg'}

    linux_name = interface_dict[interface[:2]] + interface[2:]
    return linux_name.replace('/', '_')


ztp_obj = ZtpHelpers()

try:
    result = ztp_obj.xrcmd({"exec_cmd" : "show ipv6 neighbors"})['output'][1:]
except:
    print "Failed to fetch ipv6 neighbors"
    sys.exit(1)


cmd_list = [] 
for neighbor in result:
    if 'Mcast' in neighbor:
        continue

    ipv6_address = neighbor.split()[0]
    lladdr_xr = neighbor.split()[2]
    lladdr_xr = "".join(lladdr_xr.split('.'))
    lladdr = ":".join([lladdr_xr[i:i+2] for i in range(0, len(lladdr_xr), 2)])
    interface = neighbor.split()[4]
    interface = xr_to_linux_ifname(interface)   
    cmd = ["ip -6 neigh replace "+ipv6_address+" lladdr "+lladdr+" dev "+ interface]
    cmd_list.append(cmd)

for cmd in cmd_list:
    result = run_bash(cmd)
    print result["output"]
    print result["status"]
    if (result["status"]):
        print "Failed to execute cmd, exiting"
        sys.exit(1)


