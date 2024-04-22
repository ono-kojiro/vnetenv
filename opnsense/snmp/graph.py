from subgraph import subgraph
from node import node

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
    fp.write('{0}graph {1} {{\n'.format(idt, self.name))
    fp.write('{0}  rankdir="{1}";\n'.format(idt, self.rankdir))
    fp.write('{0}  splines=curved;\n'.format(idt))
    fp.write('{0}\n'.format(idt))

    for sg in self.subgraphs:
        sg.print(fp, indent + 2)

    for sg in self.subgraphs:
        nodes = sg.get_node_all()
        for nd in nodes :
            names = nd.edges
            for name in names :
                #fp.write('{0}  "{1}" -- {2};\n'.format(idt, nd.name, name))                
                fp.write('{0}  {1} -- "{2}";\n'.format(idt, name, nd.name))                

    fp.write('{0}}}\n'.format(idt))

  def add_subgraph(self, sg):
    self.subgraphs.append(sg)

if __name__ == '__main__' :
    main()

