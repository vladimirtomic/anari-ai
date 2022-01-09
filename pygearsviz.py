"""
PyGearsViz module

PyGearsViz is a python3 Anari AI PyGears architecture visualization tool.

For more information see README.md or visit:

https://github.com/vladimirtomic/anari-ai
"""

import graphviz
from pygears.core.intf import Intf
from pygears.core.port import HDLProducer, HDLConsumer


def render_hierarchy_tree(gear, name='top_gear_hierarchy_tree', format='svg'):
    """Render PyGears module hierarchy tree

    Parameters
    ----------
    gear : pygears.core.gear.Gear
        PyGears module to use as the root
    name : str, optional
        Name of the generated output file (default is `top_gear_hierarchy_tree`)
    format : str, optional
        Format of the generated output file (default is `svg`)
    """

    g = graphviz.Graph(name=name, comment='Anari AI - Hierarchy Tree', format=format)
    g.attr(rankdir='LR')

    def name(gear):
        """Workaround for the Top Gear not having a name

        Parameters
        ----------
        gear : pygears.core.gear.Gear
            PyGears gear whose name to fetch
        """
        
        return gear.name if gear.name else 'Top'

    def render_gear(gear, parent=None):
        """Recursively render gear

        Parameters
        ----------
        gear : pygears.core.gear.Gear
            PyGears module to render
        parent : pygears.core.gear.Gear
            Parent PyGears module
        """

        g.node(name(gear), name(gear), shape='record')
        if parent:
            g.edge(name(parent), name(gear))
        for child in gear.child:
            render_gear(child, gear)

    render_gear(gear)

    g.view()


def render_dag(gear, name='top_gear_dag', format='svg'):
    """Render PyGears module DAG (directed acyclic graph)

    Parameters
    ----------
    gear : pygears.core.gear.Gear
        PyGears module to use as the root
    name : str, optional
        Name of the generated output file (default is `top_gear_dag`)
    format : str, optional
        Format of the generated output file (default is `svg`)
    """

    g = graphviz.Digraph(name=name, comment='Anari AI', format=format, node_attr={'shape': 'record', 'style': 'rounded'})
    g.attr(rankdir='LR')
    g.attr(fontcolor='#FFFFFF')

    def short(port):
        """Fetch the terminal name of the port, ex. 'dout'"""

        return port.name.split('.')[-1]

    def dot_string(ports):
        """For 'hardware' (non-hierarchical) gears fetch DOT notation with anchors"""

        body = '|'.join(f'<{short(port)}> {short(port)}' for port in ports)
        return '{' + body + '}'

    def cluster_name(gear):
        """Add prefix 'cluster_' for hierarchicl gears"""

        return f'cluster_{gear.name}' if gear.hierarchical else gear.name

    def find_producer(port):
        """Find terminal producer
        
        Traverse producers until HDLProducer is reached
        """

        if isinstance(port, HDLProducer):
            return None
        
        if isinstance(port.producer, HDLProducer):
            return port

        if isinstance(port.producer, Intf):
            producer = find_producer(port.producer.producer)
            return producer if producer else port

    def find_consumers(ports):
        """Find terminal consumers
        
        Traverse consumers until HDLConsumer is reached
        """

        consumers = set()
        
        for port in ports:
            if isinstance(port, HDLConsumer):
                pass
            elif isinstance(port.consumer, HDLConsumer):
                consumers.add(port)
            elif isinstance(port.consumer, Intf):
                for consumer in port.consumer.consumers:
                    if isinstance(consumer, HDLConsumer):
                        consumers.add(port)
                    else:
                        consumers.union(find_consumers(set([consumer])))
            else:
                consumers.add(port)

        return consumers
       
    def find_wires(intf):
        """Find terminal producer/consumer pairs for a given intf"""
        
        wires = []
        producer = find_producer(intf.producer)
        consumers = find_consumers(intf.consumers)
        for consumer in consumers:
            if producer and consumer:
                wires.append([producer, consumer])

        return wires

    def render_gear(gear, parent_graph):
        """Render module logical architecture
        
        Recursively render each hierarchichal gear as a subgraph until
        'hardware' (non-hierarchical) gear is rendered as a node.
        
        Parameters
        ----------
        gear : pygears.core.gear.Gear
            PyGears module to render
        parent_graph : graphviz.Digraph or graphviz.Subgraph
            Parent (sub)graph in which the current gear is being rendered
        """

        if gear.hierarchical:
            with parent_graph.subgraph(name=cluster_name(gear)) as sg:
                sg.attr(label=gear.basename, style='rounded, filled', fillcolor='#88888877')
                for child in gear.child:
                    render_gear(child, sg)
        else:
            ins = dot_string(gear.in_ports)
            outs = dot_string(gear.out_ports)
            parent_graph.node(name=gear.name, label='{' + f'{ins}|{gear.name}|{outs}' + '}', style='rounded,filled', fillcolor='#22222222', fontcolor='#FFFFFF')

    def render_wires(gear, g):
        """Render all terminal wires

        Recursively traverse the interfaces and ports of
        the provided gear to fetch all terminal wires.

        Parameters
        ----------
        gear : pygears.core.gear.Gear
            PyGears module to traverse and fetch terminal wires
        parent_graph : graphviz.Digraph or graphviz.Subgraph
            Parent (sub)graph in which the current gear is being rendered
        """

        wires = []

        if gear.hierarchical:
            for intf in gear.local_intfs:
                wires.extend(find_wires(intf))
                
            for child in gear.child:
                wires.extend(render_wires(child, g))
        else:
            for port in gear.in_ports:
                wires.extend(find_wires(port.producer))            

            for port in gear.out_ports:
                wires.extend(find_wires(port.consumer))
        
        return wires

    render_gear(gear, g)
    wires = render_wires(gear, g)

    printed_wires = set()

    for wire in wires:
        if str(wire) in printed_wires:
            continue
        else:
            printed_wires.add(str(wire))
        producer = wire[0]
        consumer = wire[1]
        src = f'{producer.gear.name}:{short(producer)}'
        dst = f'{consumer.gear.name}:{short(consumer)}'
        g.edge(src, dst)

    g.view()
