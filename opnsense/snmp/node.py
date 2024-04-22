class node():
  def __init__(self, name):
    self.name = name
    self.label = ""
    self.indent = 1
    self.edges = []

  def connect(self, label):
    #self.edges.append(nd.name)
    self.edges.append(label)

  def print(self, fp, indent):
    idt = ' ' * indent
    fp.write('{0}{1} [\n'.format(idt, self.name))
    fp.write('{0}  label="{1}"\n'.format(idt, self.name))
    fp.write('{0}];\n'.format(idt))
    fp.write('{0}\n'.format(idt))

