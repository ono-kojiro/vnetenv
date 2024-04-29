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
    create_ip_table(conn)
    create_sysname_table(conn)
    create_ifname_table(conn)

def create_ip_table(conn):
    table = 'ip_table'

    c = conn.cursor()
    sql = 'DROP TABLE IF EXISTS {0};'.format(table)
    c.execute(sql)

    sql = 'CREATE TABLE {0} ('.format(table)
    sql += 'id INTEGER PRIMARY KEY, '
    sql += 'mac TEXT, '
    sql += 'ip  TEXT '
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

def insert_ip(conn, mac, ip):
    table = 'ip_table'

    c = conn.cursor()
    sql = 'INSERT INTO {0} VALUES ( NULL, ?, ?);'.format(table)
    item = [
        mac,
        ip,
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

def search_ip(conn, data):
    keyword = 'ipNetToPhysicalPhysAddress'
    expr = parse('$..' + keyword)

    for m in expr.find(data):
        tree = m.value
        for i in tree:
            if 'ipv4' in tree[i]:
                for ip in tree[i]['ipv4']:
                    mac = tree[i]['ipv4'][ip]['val']
                    insert_ip(conn, mac, ip)

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
        search_ip(conn, data)
        sysname = search_sysname(conn, data)
        search_ifname(conn, data, sysname)

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

    conn.commit()
    conn.close()
    
    #if output is not None :
    #    fp.close()
    
if __name__ == "__main__":
    main()
