# Implort pygears types
from pygears import find, reg

# Import pygears types
from pygears.typing import Uint

# Import pygears built-in modules
from pygears.lib import drv, priority_mux, shred, when

# Packages used for verification and visualization
import pygearsviz

reg['gear/memoize'] = False

##############################################
#                                            #
#                   Design                   #
#                                            #
##############################################


inp1 = drv(t=Uint[8], seq=[])
inp2 = drv(t=Uint[8], seq=[])
maybe_inp1 = inp1 | when(inp1 - inp2 > 3)
maybe_inp2 = inp2 | when(inp1 * inp2 < 100)
priority_mux(maybe_inp1, maybe_inp2) | shred

##############################################
#                                            #
#          Graphviz DAG visualization        #
#                                            #
##############################################

top = find('/')

# Traverse hierarchy starting from the 'top' and generate graphviz graph
pygearsviz.render_hierarchy_tree(gear=top, name='dag_graphviz_hierarchy_tree', format='svg')
pygearsviz.render_dag(gear=top, name='dag_graphviz_dag', format='svg')
