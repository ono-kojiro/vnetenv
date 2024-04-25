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

  def print(self, fp):
    indent = self.indent
    idt = ' ' * indent
    #fp.write('{0}graph {1} {{\n'.format(idt, self.name))
    fp.write('{0}digraph {1} {{\n'.format(idt, self.name))
    #fp.write('{0}  graph [overlap=false,outputorder=edgesfirst];\n'.format(idt))
    #fp.write('{0}  node  [style=filled, fillcolor=white];\n'.format(idt))
    fp.write('{0}  rankdir="{1}";\n'.format(idt, self.rankdir))
    fp.write('{0}  newrank=true;\n'.format(idt))
    
    fp.write('{0}  splines=curved;\n'.format(idt))
    #fp.write('{0}  splines=ortho;\n'.format(idt))
    
    #fp.write('{0}  ranksep=10;\n'.format(idt))
    #fp.write('{0}  nodesep=10;\n'.format(idt))

    #fp.write('{0}  layout=sfdp;\n'.format(idt))
    #fp.write('{0}  layout=fdp;\n'.format(idt))
    #fp.write('{0}  layout=neato;\n'.format(idt))

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
                    fp.write('{0}  {1} -> {2};\n'.format(idt, val,  name)) 
                else :
                    fp.write('{0}  {1} -> {2};\n'.format(idt, name, val)) 

    fp.write('{0}}}\n'.format(idt))

  def add_subgraph(self, sg):
    self.subgraphs.append(sg)

if __name__ == '__main__' :
    main()

