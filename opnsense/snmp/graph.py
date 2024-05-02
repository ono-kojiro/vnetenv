from subgraph import subgraph
from node import node

import re

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
            'sysname': row[0],
            'ifname' : row[1],
            'ip'     : row[2],
            'mac'    : row[3],
        }
        items.append(item)
    return items
  
  def get_agents(self, conn):
    table = 'agent_view'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    items = {}
    for row in rows:
        sysname = row[0]
        ifid    = row[1]
        ifname  = row[2]
        mac     = row[3]
        ip      = row[4]

        if not sysname in items:
            items[sysname] = {}
        if not ifname in items[sysname]:
            items[sysname][ifname] = {
                'ip' : ip,
                'mac' : mac,
            }
    return items

  def get_agent_aliases(self, conn):
    table = 'agent_view'
    c = conn.cursor()
    sql = 'SELECT * FROM {0};'.format(table)
    rows = c.execute(sql)

    items = {}
    for row in rows:
        sysname = row[0]
        ifid    = row[1]
        ifname  = row[2]
        mac     = row[3]
        ip      = row[4]

        sysname = re.sub(r'\.[^.]+', '', sysname)
        items[ip] = "{0}:\"{1}\"".format(sysname, ip)
    return items

  def print(self, fp, conn):
    indent = self.indent
    idt = ' ' * indent
    #fp.write('{0}graph {1} {{\n'.format(idt, self.name))
    fp.write('{0}digraph {1} {{\n'.format(idt, self.name))
    #fp.write('{0}  graph [overlap=false,outputorder=edgesfirst];\n'.format(idt))
    #fp.write('{0}  node  [style=filled, fillcolor=white];\n'.format(idt))
    fp.write('{0}  rankdir="{1}";\n'.format(idt, self.rankdir))
    #fp.write('{0}  newrank=true;\n'.format(idt))
    
    fp.write('{0}  splines=curved;\n'.format(idt))
    #fp.write('{0}  splines=ortho;\n'.format(idt))
    
    #fp.write('{0}  ranksep=10;\n'.format(idt))
    #fp.write('{0}  nodesep=10;\n'.format(idt))

    #fp.write('{0}  layout=sfdp;\n'.format(idt))
    #fp.write('{0}  layout=fdp;\n'.format(idt))
    #fp.write('{0}  layout=neato;\n'.format(idt))
    fp.write('{0}  overlap=false;\n'.format(idt))

    fp.write('{0}\n'.format(idt))

    for nd in self.nodes :
        nd.print(fp, indent + 2)
    fp.write('{0}\n'.format(idt))

    for sg in self.subgraphs:
        sg.print(fp, indent + 2)

    for sg in self.subgraphs:
        nodes = sg.get_node_all()
        for nd in nodes :
            names = nd.edges
            for name in names :
                if re.search(r'\d+(\.\d+){3}', nd.name) :
                    val = '"' + nd.name + '"'
                else :
                    val = nd.name

                #fp.write('{0}  {1} -- {2};\n'.format(idt, name, val)) 
                if re.search(':vtnet', name) and re.search(':vtnet', val) :
                    fp.write('{0}  {1} -> {2} [minlen=2];\n'.format(idt, val,  name)) 
                else :
                    fp.write('{0}  {1} -> {2} [minlen=2];\n'.format(idt, name, val)) 
        fp.write('{0}\n'.format(idt))

    if conn:
        fp.write('\n')
        edges   = self.get_edges(conn)
        agents  = self.get_agents(conn)
        aliases = self.get_agent_aliases(conn)

        for edge in edges :
            sysname = edge['sysname']
            ifname  = edge['ifname']
            ip      = edge['ip']

            agent_ip = agents[sysname][ifname]['ip']
            sysname = re.sub(r'\.[^.]*', '', sysname)

            if agent_ip == ip :
                continue

            src = "{0}:\"{1}\"".format(sysname, agent_ip)
            if ip in aliases:
                dst = aliases[ip]
            else :
                dst = "\"{0}\"".format(ip) 
            fp.write('{0}{1} -> {2} [minlen=2];\n'.format(idt, src, dst))

            #fp.write('{0}{1}:{2} -> "{3}" [minlen=2];\n'.format(idt, sysname, ifname, ip))
            #if ip in aliases :
            #    fp.write('{0}{1}:"{2}" -> {3} [minlen=2];\n'.format(idt, sysname, agent_ip, aliases[ip]))
            #else :
            #    fp.write('{0}{1}:"{2}" -> "{3}" [minlen=2];\n'.format(idt, sysname, agent_ip, ip))
        fp.write('\n')


    str='''
  { rank = same; dummy1;  "192.168.1.1"; }
  { rank = same; dummy10; opnsense10; }
  { rank = same; dummy20; opnsense20; }
  { rank = same; dummy30; opnsense30; }
  { dummy1 -> dummy10 [minlen=4]; }
  { dummy10 -> dummy20 -> dummy30 [minlen=4]; }
'''
    fp.write(str)

    fp.write('{0}}}\n'.format(idt))

if __name__ == '__main__' :
    main()

