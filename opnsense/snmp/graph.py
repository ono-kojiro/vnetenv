import sys
from subgraph import subgraph
from node import node

import re
from pprint import pprint

class graph():
  def __init__(self, name):
    self.name = name
    self.label = ""
    self.indent = 0
    self.subgraphs = []
    self.rankdir = "TB" # Top to Bottom

    self.nodes = []

  def add_nodes(self, node):
    self.nodes.append(node)
  
  def add_subgraph(self, sg):
    self.subgraphs.append(sg)

  def get_edges(self, conn):
    table = 'conn_view'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    items = []
    for row in rows:
        item = {
            'sysname': row['sysname'],
            #ifname' : row['ifname'], # not used now
            'agent_ip'     : row['agent_ip'],
            'ip'     : row['ip'],
            'mac'    : row['mac'],
        }
        items.append(item)
    return items
  
  def get_is_agent(self, conn):
    table = 'agent_view'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    items = {}
    for row in rows:
        sysname = row['sysname']
        ip      = row['ip']
        sysname = re.sub(r'\.[^.]+', '', sysname)
        items[ip] = sysname
    return items
    
  def create_connections(self, fp, conn, idt):
    line = ''
    line += '  /* draw edges using database */\n'
    line += '\n'

    edges   = self.get_edges(conn)
    routers = self.get_defaultrouters(conn)
    ip2agent = self.get_is_agent(conn)

    records = {}

    for edge in edges :
        sysname = edge['sysname']
        agent_ip = edge['agent_ip']
        ip      = edge['ip']

        sysname = re.sub(r'\.[^.]*', '', sysname)

        if agent_ip == ip :
            continue
        
        src = agent_ip
        dst = ip

        # change direction
        if dst in routers:
            print("default router {0} found".format(dst), file=sys.stderr)
            tmp = src
            src = dst
            dst = tmp

        # remove duplicates
        if not src in records :
            records[src] = {}
        if not dst in records[src]:
            records[src][dst] = 0
        records[src][dst] += 1
        if records[src][dst] >= 2:
            continue

        # ex. "192.168.10.1" -> opnsense10:"192.168.10.1"
        if src in ip2agent :
            src = '{0}:"{1}"'.format(ip2agent[src], src)
        else :
            src = '"{0}"'.format(src)
        
        if dst in ip2agent :
            dst = '{0}:"{1}"'.format(ip2agent[dst], dst)
        else :
            dst = '"{0}"'.format(dst)
        
        minlen = 2
        if re.search(r'.+\:.+', src) and re.search(r'.+\:.+', dst) :
            minlen = 4
        
        line += '  {0} -> {1} '.format(src, dst)
        line += '[minlen={0}];\n'.format(minlen)

    line += '\n'
   
    indent = 2
    idt = ' ' * indent
    tokens = re.split(r'\n', line)
    for token in tokens :
        fp.write('{0}{1}\n'.format(idt, token))

  def get_defaultrouters(self, conn):
    table = 'defaultrouter_table'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    items = {}
    for row in rows:
        item = row[2]
        items[item] = 1
    return items


  def print(self, fp, conn, includes_dot):
    indent = self.indent
    idt = ' ' * indent
    
    line = ''

    line += 'digraph {0} {{\n'.format(self.name)
    line += '  rankdir="{0}";\n'.format(self.rankdir)
    line += '  outputorder=edgesfirst;\n'
    #line += '  newrank=true;\n'
    
    line += '  splines=curved;\n'
    #line += '  splines=ortho;\n'

    #line += '  layout=sfdp;\n'
    #line += '  layout=fdp;\n'
    #line += '  layout=neato;\n'
    #line += '  layout=twopi;\n'
    line += '  overlap=false;\n'
    
    line += '\n'
    
    idt = ' ' * indent
    tokens = re.split(r'\n', line)
    for token in tokens :
        fp.write('{0}{1}\n'.format(idt, token))
    line = ''

    for nd in self.nodes :
        nd.print(fp, indent + 2)
    fp.write('{0}\n'.format(idt))

    for sg in self.subgraphs:
        sg.print(fp, indent + 2)

    self.create_connections(fp, conn, idt)

    for include_dot in includes_dot :
        fp_in = open(include_dot, mode="r", encoding="utf-8")
        lines = fp_in.read()
        fp.write(lines)
        fp_in.close()

    fp.write('{0}}}\n'.format(idt))

if __name__ == '__main__' :
    main()

