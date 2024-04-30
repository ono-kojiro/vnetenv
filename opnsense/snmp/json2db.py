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
    create_mac_table(conn)
    create_ifname_table(conn)
    create_netmask_table(conn)

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


def create_mac_table(conn):
    table = 'mac_table'

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
    sql += 'ifid INTEGER, '
    sql += 'ifname TEXT '
    sql += ');'

    c.execute(sql)

def create_netmask_table(conn):
    table = 'netmask_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'sysname TEXT, '
    sql += 'addr TEXT, '
    sql += 'netmask TEXT '
    sql += ');'

    c.execute(sql)

def create_view(conn):
    create_agent_view(conn)
    create_host_view(conn)
    create_conn_view(conn)
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
    sql += '  ifmac_table.mac AS mac, '
    sql += '  mac_table.ip  AS ip '
    sql += 'FROM ifname_table '
    sql += 'LEFT JOIN ifmac_table ON ifname_table.sysname = ifmac_table.sysname AND ifname_table.ifid = ifmac_table.ifid '
    sql += 'LEFT JOIN mac_table ON ifname_table.sysname = mac_table.sysname AND ifname_table.ifid = mac_table.ifid AND ifmac_table.mac = mac_table.mac '
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
    sql += '  mac_table.sysname AS sysname, '
    sql += '  mac_table.ifid AS ifid, '
    sql += '  mac_table.ip  AS ip, '
    sql += '  mac_table.mac AS mac, '
    sql += '  ifmac_table.mac AS mac2 '
    sql += 'FROM mac_table '
    sql += 'LEFT OUTER JOIN ifmac_table ON '
    sql += '  mac_table.mac     = ifmac_table.mac '
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
    sql += '  mac_table.ip AS ip, '
    sql += '  ifmac_table.mac AS mac '
    sql += 'FROM ifmac_table '
    sql += '  LEFT JOIN ifname_table ON ifmac_table.sysname = ifname_table.sysname AND ifmac_table.ifid = ifname_table.ifid '
    sql += '  LEFT JOIN mac_table ON ifmac_table.sysname = mac_table.sysname AND ifmac_table.ifid = mac_table.ifid AND ifmac_table.mac = mac_table.mac '
    sql += ';'

    c.execute(sql)

def create_conn_view(conn):
    view = 'conn_view'

    c = conn.cursor()
    sql = 'DROP VIEW IF EXISTS {0};'.format(view)
    c.execute(sql)

    sql = 'CREATE VIEW {0} AS '.format(view)
    sql += 'SELECT '
    sql += '  mac_table.sysname AS sysname, '
    sql += '  ifname_table.ifname AS ifname, '
    sql += '  mac_table.ip  AS ip, '
    sql += '  mac_table.mac AS mac '
    sql += 'FROM mac_table '
    sql += '  LEFT OUTER JOIN ifmac_table ON mac_table.mac = ifmac_table.mac '
    sql += '  LEFT JOIN ifname_table ON mac_table.sysname = ifname_table.sysname AND mac_table.ifid = ifname_table.ifid '
    #sql += 'WHERE ifmac_table.mac IS NULL '
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

def insert_ifname(conn, sysname, ifid, ifname):
    table = 'ifname_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ?);'.format(table)
    item = [
        sysname,
        ifid,
        ifname,
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

def insert_mac(conn, sysname, ifid, ip, mac):
    table = 'mac_table'

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

def search_netmask(conn, data, sysname):
    keyword = 'ipCidrRouteInfo'
    expr = parse('$..' + keyword)

    items = {}

    for m in expr.find(data):
        tree = m.value
        for addr in tree:
            for mask in tree[addr]:
                if mask != '0.0.0.0' :
                    insert_netmask(conn, sysname, addr, mask)

def insert_netmask(conn, sysname, addr, netmask):
    table = 'netmask_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?, ? );'.format(table)
    item = [
        sysname,
        addr,
        netmask
    ]

    c.execute(sql, item)

def search_ifmac(conn, data, sysname):
    keyword = 'ifPhysAddress'
    expr = parse('$..' + keyword)

    items = {}

    for m in expr.find(data):
        tree = m.value
        for ifid in tree:
            mac = tree[ifid]['val']
            if mac != '' :
                insert_ifmac(conn, sysname, ifid, mac)
                items[mac] = 1

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

                insert_mac(conn, sysname, ifid, ip, mac)

def search_sysname(conn, data):
    keyword = "['sysName.0']"
    expr = parse('$..' + keyword)

    sysname = None

    for m in expr.find(data):
        tree = m.value

        sysname = tree['val']
        insert_sysname(conn, sysname)

    return sysname

def search_ifname(conn, data, sysname):
    keyword = 'ifName'
    expr = parse('$..' + keyword)

    for m in expr.find(data):
        tree = m.value
        for ifid in tree:
            ifname = tree[ifid]['val']
            insert_ifname(conn, sysname, ifid, ifname)

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
 
    records = {}

    keywords = [
#        "['sysName.0']",
#        "['ifNumber.0']",
#        'ifName',
#        'ifPhysAddress',
        'ipNetToPhysicalPhysAddress',
    ]

    for filepath in args:
        data = read_json(filepath)
        sysname = search_sysname(conn, data)
        ifmacs = search_ifmac(conn, data, sysname)
        search_mac(conn, data, sysname, ifmacs)
        search_ifname(conn, data, sysname)
        search_netmask(conn, data, sysname)

    #yaml.dump(records,
    #    fp,
    #    allow_unicode=True,
    #    default_flow_style=False,
    #    sort_keys=True
    #)

    #fp.write(
    #    json.dumps(
    #        records,
    #        indent=4,
    #        ensure_ascii=False,
    #        sort_keys=True,
    #    )
    #)
    #fp.write('\n')

    create_view(conn)
    conn.commit()
    conn.close()
    
    #if output is not None :
    #    fp.close()
    
if __name__ == "__main__":
    main()
