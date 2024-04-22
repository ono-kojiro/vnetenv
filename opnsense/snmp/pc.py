from node import node

import re

class pc(node):
  def __init__(self, name):
    super().__init__(self)
    self.name = name

  def print(self, fp, indent):
    line = ''

    #line += '"{0}" [\n'.format(self.name)
    #line += '  label="{0}"\n'.format(self.name)
    #line += '  penwidth=0\n'
    #line += '  image="icons/doc_jpg/pc.png"\n'
    #line += ']\n'
    #line += '\n'

    line += '"{0}" [\n'.format(self.name)
    line += '  label=<\n'
    line += '    <table cellspacing="0" border="0" cellborder="1">\n'
    line += '      <tr><td><img src="icons/doc_jpg/pc.png" /></td></tr>\n'
    line += '      <tr><td>{0}</td></tr>\n'.format(self.name)
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

