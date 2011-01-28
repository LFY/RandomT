from RandomT import *

X = Flip()
Y = Flip()
Z = Flip()

W = X * Y + Y * Z + Z * X

name = 'debug'

f = open(name + '.dot', 'w')
print debug_output(W, locals())
f.write(debug_output(W, locals()))
f.close()

import os

os.system('dot %s.dot -Tpng > %s.png' % (name, name))

