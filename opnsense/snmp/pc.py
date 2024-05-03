from node import node

import re

class pc(node):
  def __init__(self, name, *args):
    super().__init__(self)
    self.name = name

    if len(args) >= 1:
      self.ip   = args[0]
    else :
      self.ip = ''

    if len(args) >= 2:
      self.mac  = args[1]
    else :
      self.mac = ''

  def print(self, fp, indent):
    line = ''

    #line += '"{0}" [\n'.format(self.name)
    #line += '  label="{0}"\n'.format(self.name)
    #line += '  penwidth=0\n'
    #line += '  image="icons/doc_jpg/pc.png"\n'
    #line += ']\n'
    #line += '\n'

    if not re.search(r':', self.name) :
        line += '"{0}" [\n'.format(self.name)
        line += '  shape=box,\n'
        line += '  label=<\n'
        line += '    <table cellspacing="0" border="0" cellborder="0">\n'
        line += '      <tr><td fixedsize="true" width="20" height="20"><img src="icons/doc_jpg/pc.png" /></td></tr>\n'
        line += '      <tr><td>ip:  {0}</td></tr>\n'.format(self.name)
        line += '      <tr><td>mac: {0}</td></tr>\n'.format(self.mac)
        line += '    </table>\n'
        line += '  >\n'
        line += ']\n'
        line += '\n'
    
    idt = ' ' * indent
    tokens = re.split(r'\n', line)
    for token in tokens :
        fp.write('{0}{1}\n'.format(idt, token))

    #fp.write('{0}"{1}" [\n'.format(idt, self.name))
    #fp.write('{0}  label="{1}"\n'.format(idt, self.name))
    #fp.write('{0}  penwidth=0\n'.format(idt))
    #fp.write('{0}  image="icons/doc_jpg/pc.png"\n'.format(idt))
    #fp.write('{0}];\n'.format(idt))
    #fp.write('{0}\n'.format(idt))

