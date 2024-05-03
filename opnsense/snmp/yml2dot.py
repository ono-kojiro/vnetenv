#!/usr/bin/python

import sys
import os

import getopt
import json
import re

import yaml
from yaml.loader import SafeLoader

from pprint import pprint
from jsonpath_ng import jsonpath, parse

from graph import graph
from subgraph import subgraph
from switch import switch
from pc import pc

def usage():
  print("Usage : {0}".format(sys.argv[0]))
        
def read_json(filepath):
  fp_in = open(filepath, mode='r', encoding='utf-8')
  data = json.load(fp_in)
  fp_in.close()
  return data


def read_yaml(filepath):
  fp = open(filepath, mode="r", encoding="utf-8")
  data = yaml.load(fp, Loader=SafeLoader)
  fp.close()
  return data

def get_interfaces(ifids, ignores):
    ifaces = []
    for ifid in ifids:
        ifname = ifids[ifid]['val']
        if ifname in ignores :
            continue
        ifaces.append(ifid)

    return ifaces

def get_ip_address(ip2macs, ifaces, macs):
    items = {}
    for id in ifaces:
        target = macs[id]
        for ipv4 in ip2macs[id]['ipv4']:
            mac = ip2macs[id]['ipv4'][ipv4]['val']
            #print("debug: {0}, {1}".format(mac, target))
            if mac == target :
                items[id] = ipv4
    return items

def main():
    ret = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:i:",
            [
                "help",
                "version",
                "output=",
                "include=",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
    includes_dot = []
    
    for o, a in opts:
        if o == "-v":
            usage()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-i", "--include"):
            includes_dot.append(a)
        else:
            assert False, "unknown option"
    
    if output is not None :
        fp = open(output, mode='w', encoding='utf-8')
    else:
        fp = sys.stdout
    
    if ret != 0:
        sys.exit(1)
    
    records = {}

    switch_addrs = {
      '192.168.0.254'  : 'opnsense40',
      '192.168.40.1'   : 'opnsense40',

      '192.168.40.254' : 'opnsense50',
      '192.168.50.1'   : 'opnsense50',

      '192.168.50.254' : 'opnsense60',
      '192.168.60.1'   : 'opnsense60',
    }

    ignores = {
        'pfsync0' : 0,
        'pflog0' : 0,
        'enc0' : 0,
        'lo0' : 0,
    }

    switches = {}

    aliases = {}

    for filepath in args:
        data = read_yaml(filepath)
        sysname = data["['sysName.0']"]['val']
        sysname = re.sub(r'\..+', '', sysname)

        ifids = data['ifName']
        ip2macs = data['ipNetToPhysicalPhysAddress']

        # [ '1', '2', ... ]
        ifaces = get_interfaces(ifids, ignores)

        # id => mac
        macs = {}
        for i in ifaces:
            macs[i] = data['ifPhysAddress'][i]['val']

        # id => ipv4
        ipv4s  = get_ip_address(ip2macs, ifaces, macs)
        #pprint(ipv4s)


        hostname = sysname
        
        for i in ipv4s :
            ifname = ifids[i]['val']
            ipv4   = ipv4s[i]
            alias = "{0}:{1}".format(hostname, ifname)
            aliases[ipv4] = alias

        for ifid in ifaces:
            # ex. vtnet0
            ifname = ifids[ifid]['val']
            mac    = macs[ifid]
            ipv4   = ipv4s[ifid]

            hosts = {}
            items = data['ipNetToPhysicalPhysAddress'][ifid]['ipv4']
            for addr in items:
                if addr == ipv4 :
                    continue

                if addr in aliases:
                    alias = aliases[addr]
                else :
                    alias = addr
                hosts[alias] = items[addr]['val']

            if not hostname in switches:
                switches[hostname] = {}
            switches[hostname][ifname] = hosts

    mygraph = graph('mygraph')

    for hostname in switches :
        mysubgraph = subgraph(hostname)
        
        mygraph.add_subgraph(mysubgraph)
    
        ifnames = []
        for ifname in switches[hostname]:
            ifnames.append(ifname)

        myswitch = switch(hostname)
        myswitch.set_ports(ifnames)
        mysubgraph.add_node(myswitch)

        for ifname in switches[hostname]:
            hosts = switches[hostname][ifname]
            for ipv4 in hosts:
                mac = hosts[ipv4]
                mypc = pc(ipv4)
                mysubgraph.add_node(mypc)
                mypc.connect("{0}:{1}".format(hostname,ifname))

    mygraph.print(fp, None, includes_dot)

    if output is not None :
        fp.close()
    
if __name__ == "__main__":
    main()
