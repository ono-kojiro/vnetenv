import re
from node import node

class switch(node):
  def __init__(self, name):
    super().__init__(self)
    self.name = name
    self.ports = [ "port0", "port1", "port2", "port3" ]
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
    line = ''
    line += '"{0}" [\n'.format(self.name)
    line += '  shape=record\n'
    line += '  label="{{{0}|{{\n'.format(self.name)

    b_first = 1
    i = 0
    for port in self.ports :
        if b_first == 1:
            b_first = 0
        else :
            line += '|'

        line += '<{0}>{1}\n'.format(port, port)
        i += 1
    line += '\n'

    line += '  }}}}"\n'
    line += '];\n'
    line += '\n'

    idt = ' ' * indent
    tokens = re.split(r'\n', line)
    for token in tokens :
        fp.write('{0}{1}\n'.format(idt, token))

