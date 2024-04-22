#!/usr/bin/python

import sys
import os

import getopt
import json

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


def main():
    ret = 0

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hvo:",
            [
                "help",
                "version",
                "output=",
            ]
        )
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    output = None
    
    for o, a in opts:
        if o == "-v":
            usage()
            sys.exit(0)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-o", "--output"):
            output = a
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

    for filepath in args:
        data = read_yaml(filepath)
        addr = os.path.splitext(os.path.basename(filepath))[0]
        if not addr in switch_addrs:
            print('ERROR: no hostname for {0}'.format(addr), file=sys.stderr)
            sys.exit(1)

        hostname = switch_addrs[addr]

        print(addr, file=sys.stderr)
        ifids = data['ifName']
        for ifid in ifids:
            ifname = ifids[ifid]['val']
            if ifname in ignores :
                continue
            
            mac = data['ifPhysAddress'][ifid]['val']
            
            hosts = {}
            ipv4s = data['ipNetToPhysicalPhysAddress'][ifid]['ipv4']
            for ipv4 in ipv4s:
                if ipv4 == addr :
                    continue

                if ipv4 in switch_addrs and switch_addrs[ipv4] == hostname :
                    continue

                mac = ipv4s[ipv4]['val']
                hosts[ipv4] = mac
            

            if not hostname in switches:
                switches[hostname] = {}
            switches[hostname][ifname] = hosts

    
    pprint(switches, stream=sys.stderr)

    mygraph = graph('mygraph')

    aliases = { }

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

    mygraph.print(fp)

    if output is not None :
        fp.close()
    
if __name__ == "__main__":
    main()
