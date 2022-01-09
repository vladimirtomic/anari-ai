"""
PyGearsViz module

PyGearsViz is a python3 Anari AI PyGears architecture visualization tool.

For more information see README.md or visit:

https://github.com/vladimirtomic/anari-ai
"""

import graphviz
from pygears import find


def render_hierarchy_tree(gear, name='grand_tour_hierarchy_tree', format='pdf'):
    """Render PyGears module hierarchy tree

    Parameters
    ----------
    gear : pygears.core.gear.Gear
        PyGears module to use as the root
    name : str, optional
        Name of the generated output file (default is `grand_tour_hierarchy_tree`)
    format : str, optional
        Format of the generated output file (default is `pdf`)
    """

    g = graphviz.Graph(name=name, comment='Anari AI - Hierarchy Tree', format=format)
    g.attr(rankdir='TD')

    def name(gear):
        """Workaround for the Top Gear not having a name

        Parameters
        ----------
        gear : pygears.core.gear.Gear
            PyGears gear whose name to fetch
        """
        return gear.name if gear.name else 'Top'

    def render_gear(gear, parent=None):
        g.node(name(gear), name(gear), shape='record')
        if parent:
            g.edge(name(parent), name(gear))
        for child in gear.child:
            render_gear(child, gear)

    render_gear(find('/'))

    g.view()
    # print(g.source)
