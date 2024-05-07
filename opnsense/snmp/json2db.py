#!/usr/bin/python

import sys

import getopt
import json

import yaml
from yaml.loader import SafeLoader

import sqlite3

from pprint import pprint
from jsonpath_ng import jsonpath, parse

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

def create_table(conn):
    create_sysname_table(conn)
    create_ifmac_table(conn)
    create_ip_table(conn)
    create_ifname_table(conn)
    create_netmask_table(conn)
    create_defaultrouter_table(conn)

def create_ifmac_table(conn):
    table = 'ifmac_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifid INTEGER, '
    sql += 'mac  TEXT '
    sql += ');'

    c.execute(sql)


def create_ip_table(conn):
    table = 'ip_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifid INTEGER, '
    sql += 'ip TEXT, '
    sql += 'mac  TEXT '
    sql += ');'

    c.execute(sql)

def create_sysname_table(conn):
    table = 'sysname_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'name TEXT '
    sql += ');'

    c.execute(sql)

def create_ifname_table(conn):
    table = 'ifname_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'ifname TEXT, '
    sql += 'ifid INTEGER '
    sql += ');'

    c.execute(sql)

def create_netmask_table(conn):
    table = 'netmask_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'addr TEXT, '
    sql += 'netmask TEXT '
    sql += ');'

    c.execute(sql)

def create_defaultrouter_table(conn):
    table = 'defaultrouter_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'addr TEXT '
    sql += ');'

    c.execute(sql)


def create_view(conn):
    create_agent_view(conn)
    create_host_view(conn)
    create_conn_view(conn)
    create_trunk_view(conn)
    create_segment_view(conn)
    create_ifip_view(conn)

def create_agent_view(conn):
    view = 'agent_view'

    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  ifname_table.sysname AS sysname, '
    sql += '  ifname_table.ifid AS ifid, '
    sql += '  ifname_table.ifname AS ifname, '
    sql += '  ip_table.ip  AS ip, '
    sql += '  ifmac_table.mac AS mac '
    sql += 'FROM ifname_table '
    sql += 'LEFT JOIN ifmac_table ON ifname_table.sysname = ifmac_table.sysname AND ifname_table.ifid = ifmac_table.ifid '
    sql += 'LEFT JOIN ip_table ON ifname_table.sysname = ip_table.sysname AND ifname_table.ifid = ip_table.ifid AND ifmac_table.mac = ip_table.mac '
    sql += 'WHERE ifmac_table.mac != "" '
    sql += ';'

    c.execute(sql)

def create_host_view(conn):
    view = 'host_view'

    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  ip_table.sysname AS sysname, '
    sql += '  ip_table.ifid AS ifid, '
    sql += '  ip_table.ip  AS ip, '
    sql += '  ip_table.mac AS mac, '
    sql += '  ifmac_table.mac AS mac2 '
    sql += 'FROM ip_table '
    sql += 'LEFT OUTER JOIN ifmac_table ON '
    sql += '  ip_table.mac     = ifmac_table.mac '
    sql += 'WHERE ifmac_table.mac IS NULL '
    sql += ';'

    c.execute(sql)

def create_ifip_view(conn):
    view = 'ifip_view'

    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  ifmac_table.sysname AS sysname, '
    sql += '  ifmac_table.ifid AS ifid, '
    sql += '  ifname_table.ifname AS ifname, '
    sql += '  ip_table.ip AS ip, '
    sql += '  ifmac_table.mac AS mac '
    sql += 'FROM ifmac_table '
    sql += '  LEFT JOIN ifname_table ON ifmac_table.sysname = ifname_table.sysname AND ifmac_table.ifid = ifname_table.ifid '
    sql += '  LEFT JOIN ip_table ON ifmac_table.sysname = ip_table.sysname AND ifmac_table.ifid = ip_table.ifid AND ifmac_table.mac = ip_table.mac '
    sql += ';'

    c.execute(sql)

def create_conn_view(conn):
    view = 'conn_view'

    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  ip_table.sysname AS sysname, '
    sql += '  ifname_table.ifname AS ifname, '
    sql += '  agent_view.ip AS agent_ip, '
    sql += '  ip_table.ip  AS ip, '
    sql += '  ip_table.mac AS mac '
    sql += 'FROM ip_table '
    sql += '  LEFT OUTER JOIN ifmac_table ON ip_table.mac = ifmac_table.mac '
    sql += '  LEFT JOIN ifname_table ON ip_table.sysname = ifname_table.sysname AND ip_table.ifid = ifname_table.ifid '
    sql += '  LEFT JOIN agent_view ON ip_table.sysname = agent_view.sysname AND ip_table.ifid = agent_view.ifid '
    sql += ';'

    c.execute(sql)

def create_trunk_view(conn):
    view = 'trunk_view'
    
    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  ip_table.sysname AS sysname, '
    sql += '  ifname_table.ifname AS ifname, '
    sql += '  agent_view.ip AS agent_ip, '
    sql += '  ip_table.ip  AS ip, '
    sql += '  ip_table.mac AS mac '
    sql += 'FROM ip_table '
    sql += '  LEFT OUTER JOIN ifmac_table ON ip_table.mac = ifmac_table.mac '
    sql += '  LEFT JOIN ifname_table ON ip_table.sysname = ifname_table.sysname AND ip_table.ifid = ifname_table.ifid '
    sql += '  LEFT JOIN agent_view ON ip_table.sysname = agent_view.sysname AND ip_table.ifid = agent_view.ifid '
    sql += 'WHERE ifmac_table.mac IS NOT NULL '
    sql += ';'

    c.execute(sql)

def create_segment_view(conn):
    view = 'segment_view'

    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  DISTINCT addr, netmask '
    sql += 'FROM netmask_table '
    sql += ';'

    c.execute(sql)

def insert_ifname(conn, sysname, ifname, ifid):
    table = 'ifname_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    item = [
        sysname,
        ifname,
        ifid,
    ]

    c.execute(sql, item)

def insert_defaultrouter(conn, sysname, addr):
    table = 'defaultrouter_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ? );'.format(table)
    item = [
        sysname,
        addr,
    ]

    c.execute(sql, item)


def insert_ifmac(conn, sysname, ifid, mac):
    table = 'ifmac_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ? );'.format(table)
    item = [
        sysname,
        ifid,
        mac,
    ]

    c.execute(sql, item)

def insert_ip(conn, sysname, ifid, ip, mac):
    table = 'ip_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?, ? );'.format(table)
    item = [
        sysname,
        ifid,
        ip,
        mac,
    ]

    c.execute(sql, item)

def insert_sysname(conn, name):
    table = 'sysname_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?);'.format(table)
    item = [
        name,
    ]

    c.execute(sql, item)

def search_netmask(conn, data):
    keyword = 'ipCidrRouteInfo'
    expr = parse('$..' + keyword)

    items = {}

    for m in expr.find(data):
        tree = m.value
        for addr in tree:
            for mask in tree[addr]:
                if mask != '0.0.0.0' :
                    insert_netmask(conn, addr, mask)

def search_defaultrouter(conn, data, sysname):
    keyword = 'ipDefaultRouterLifetime'
    expr = parse('$..' + keyword)

    items = {}

    for m in expr.find(data):
        tree = m.value
        if not 'ipv4' in tree:
            continue

        for addr in tree['ipv4']:
            insert_defaultrouter(conn, sysname, addr)

def insert_netmask(conn, addr, netmask):
    table = 'netmask_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ? );'.format(table)
    item = [
        addr,
        netmask
    ]

    c.execute(sql, item)

def search_ifmac(data):
    keyword = 'ifPhysAddress'
    expr = parse('$..' + keyword)

    items = {}

    for m in expr.find(data):
        tree = m.value
        for ifid in tree:
            mac = tree[ifid]['val']
            if mac != '' :
                items[ifid] = mac

    return items

def search_mac(conn, data, sysname, ifmacs):
    keyword = 'ipNetToPhysicalPhysAddress'
    expr = parse('$..' + keyword)

    for m in expr.find(data):
        tree = m.value
        for ifid in tree:
            if not 'ipv4' in tree[ifid]:
                continue

            for ip in tree[ifid]['ipv4']:
                mac = tree[ifid]['ipv4'][ip]['val']
                #if mac in ifmacs:
                #    continue

                insert_ip(conn, sysname, ifid, ip, mac)

def search_sysname(data):
    keyword = "['sysName.0']"
    expr = parse('$..' + keyword)

    items = []
    
    for m in expr.find(data):
        tree = m.value
        sysname = tree['val']
        items.append(sysname)

    return items

def search_ifname(data):
    keyword = 'ifName'
    expr = parse('$..' + keyword)

    items = {}

    for m in expr.find(data):
        tree = m.value
        for ifid in tree:
            ifname = tree[ifid]['val']
            items[ifname] = ifid
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
                "output="
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
   
    if output is None:
        print('no output option')
        sys.exit(1)

    conn = sqlite3.connect(output)
    create_table(conn)
 
    for filepath in args:
        data = read_json(filepath)
        sysnames = search_sysname(data)
        if len(sysnames) != 1 :
            print('ERROR: no sysname in {0}'.format(filepath))
            sys.exit(1)

        sysname = sysnames[0]
        insert_sysname(conn, sysname)
        
        # ifnames[ifname] => ifid
        ifnames = search_ifname(data)
        for ifname in ifnames:
            ifid = ifnames[ifname]
            insert_ifname(conn, sysname, ifname, ifid)

        ifmacs = search_ifmac(data)
        for ifid in ifmacs :
            mac = ifmacs[ifid]
            insert_ifmac(conn, sysname, ifid, mac)
            
        search_mac(conn, data, sysname, ifmacs)
        search_netmask(conn, data)
        search_defaultrouter(conn, data, sysname)

    create_view(conn)
    conn.commit()
    conn.close()
    
    #if output is not None :
    #    fp.close()
    
if __name__ == "__main__":
    main()
