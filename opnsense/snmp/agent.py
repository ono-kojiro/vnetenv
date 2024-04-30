from node import node

class agent(node):
  def __init__(self, name):
    super().__init__(self)
    self.name = name
    #self.ports = [ "port0", "port1", "port2", "port3" ]
    self.ports = []
    self.cons = {}

  def set_port_number(self, num):
    print('DEBUG: set port number, {0}'.format(num))
    self.port_num = num

  def set_ports(self, ports):
    self.ports = ports

  def connect(self, port_id, node_name) :
    if not port_id in self.cons:
        self.cons[port_id] = []
    self.cons[port_id].append(node_name)
    
  def print(self, fp, indent):
    idt = ' ' * indent
    fp.write('{0}"{1}" [\n'.format(idt, self.name))
    fp.write('{0}  shape=record\n'.format(idt))
    fp.write('{0}  label="{{{1}|{{\n'.format(idt, self.name))
    b_first = 1
    #for i in range(self.port_num):
    i = 0
    for port in self.ports :
        fp.write('{0}'.format(idt))
        if b_first == 1:
            b_first = 0
        else :
            fp.write('|')

        #fp.write('<port{1}>port{1}\n'.format(idt, i))
        fp.write('<{0}>{1}\n'.format(port, port))
        i += 1
    fp.write('\n')

    fp.write('{0}  }}}}"\n'.format(idt))
    fp.write('{0}];\n'.format(idt))
    fp.write('{0}\n'.format(idt))



