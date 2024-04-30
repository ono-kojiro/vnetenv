#!/usr/bin/python

import sys
import os

import getopt
import json
import re

import sqlite3

import yaml
from yaml.loader import SafeLoader

from pprint import pprint
from jsonpath_ng import jsonpath, parse

from graph import graph
from subgraph import subgraph
from switch import switch
from pc import pc
from agent import agent

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

def get_agents(conn):
    table = 'agent_view'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    agents = {}

    for row in rows:
        sysname = row[0]
        ifid    = row[1]
        ifname  = row[2]
        mac     = row[3]
        ip      = row[4]

        sysname = re.sub(r'\.[^.]*', '', sysname)
        if not sysname in agents:
            agents[sysname] = {}
        
        if not ifname in agents[sysname]:
            agents[sysname][ifname] = {}

        agents[sysname][ifname]['ip'] = ip
        agents[sysname][ifname]['mac'] = mac

    return agents

def get_sysnames(conn):
    table = 'sysname_table'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    sysnames = []
    for row in rows:
        sysname = row[1]
        sysnames.append(sysname)
    return sysnames

def get_segments(conn):
    table = 'segment_view'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    items = []
    for row in rows:
        item = row[0]
        items.append(item)

    return items

def get_hosts(conn, segment):
    table = 'host_view'

    segment = re.sub(r'\.[^.]*$', '.%', segment)

    c = conn.cursor()
    sql =  'SELECT '
    sql += '  sysname, '
    sql += '  ip, '
    sql += '  mac '
    sql += 'FROM {0} '.format(table)
    sql += 'WHERE ip LIKE "{0}"'.format(segment)
    sql += ';'

    #print(sql)
    rows = c.execute(sql)

    items = []
    for row in rows:
        item = {
            'ip'  : row[1],
            'mac' : row[2],
        }
        items.append(item)

    return items

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

    aliases = {}
    
    mygraph = graph('mygraph')

    for database in args:
        conn = sqlite3.connect(database)
        
        sysnames = get_sysnames(conn)
        segments = get_segments(conn)
        #pprint(sysnames)
        #pprint(segments)

        for segment in segments:
            mysubgraph = subgraph(segment)
            mygraph.add_subgraph(mysubgraph)
            
            hosts = get_hosts(conn, segment)

            for host in hosts:
                ip  = host['ip']
                mac = host['mac']
                mypc = pc(ip, ip, mac)
                mysubgraph.add_node(mypc)

        agents = get_agents(conn)
        print(agents, file=sys.stderr)
        for name in agents :
            myagent = agent(name)
            ports = []
            for ifname in agents[name]:
                ports.append(ifname)
            myagent.set_ports(ports)
            mygraph.add_nodes(myagent)

    mygraph.print(fp, conn)

    if output is not None :
        fp.close()
    
if __name__ == "__main__":
    main()
