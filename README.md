# Anari AI - PyGearsViz

## Introduction

PyGearsViz is a python3 Anari AI PyGears architecture visualization tool. It is based on Graphviz and provides two utility methods:

- `render_hierarchy_tree(gear, name, format)` - plots a Graphviz hierarchy tree representing the PyGears module hierarchy starting from the provided gear; optionally provide the file name (default `top_gear_hierarchy_tree`) and export format (default `svg`)

- `render_dag(gear, name, format)` - plots a Graphviz DAG (directed acyclic graph) representing the logical architecture (modules and "wires") of a PyGears module; optionally provide the file name (default `top_gear_dag`) and export format (default `svg`)

## Design

### Hierarchy tree

Hierarchy tree has been implemented in the basic Graphviz template - no fancy styling.

Trees are usually plotted vertically (top-to-bottom, sometimes bottom-to-top) - this was resulting in unreadably wide graphs, so the default (hard-coded) orientation was set to left-to-right.

### DAG (directed acyclic graph)

Initial plots of module architecture in a DAG format were messy with a large number of edges being plotted, which resulted in graph that wasn't easy to understand.

Again, top-to-bottom orientation was replaced with left-to-right.

First improvement was to plot all hierarchical modules as **subgraphs**. **Terminal** modules (non-hierarchical, also referred to as '**hardware**' modules - I assume that these corresond to literal modules available in FPGA) were plotted as **nodes**. Record style was used so that the **input ports** are vertically stacked on the left, and **output ports** vertically stacked on the right. This resulted in a much nicer graph, but a large number of edges was missing since hierarchical module ports were not present.

Second improvement was to trace all the **logical ports** (ports of hierarchical module) back to a **terminal (HDL) port** and plot only edges (also referred to as **wires**) which connect **terminal ports/modules**.

The basic assumption and rationale behind these two improvements is that the hierarchical modules are a logical aggregation of basic HDL/hardware modules - plotting only terminal modules as nodes and terminal port edges will at the same time provide insight into actual hardware modules and wires used, as well as show logical grouping of those elements into functional blocks.

Third improvement was to use the alpha color channel, set the transparency/opacity on each subgraph, which emphasizes the nesting properties of the architecture.

### Notes

I tried to keep the python code very simple. No classes were introduced - each of the two main utility functions contains sub-functions it relies on. For each function a brief docstring is provided.

Most of the complexity in the code comes from the fact that, compared to usual data structure traversing problems, in PyGears we don't have nodes pointing to each other directly, but through children, ports and interfaces.

Function `render_dag()` might fail in the case where a cyclic hierarchical module is provided. See [Stereo echo](https://www.pygears.org/echo.html#stereo-echo) example!

No tests were written. :/

Please consider renaming `gear.child` to `gear.children`.

## Setup

This project was developed using a Mac with [MS Visual Studio Code](https://code.visualstudio.com/download#). [Python 3.10.1](https://www.python.org/downloads/) was installed in a dedicated [pyenv](https://github.com/pyenv/pyenv) environment. [Graphviz 2.50.0](https://graphviz.org/download/) and pyenv were installed using [homebrew](https://brew.sh/).

Install python dependencies:

```
pip install -r requirements.txt
```

## Usage

To use PyGearsViz import it:

```import pygearsviz```

Plot the module hierarchy tree of a gear (saves the files in the working directory and launches a preview):

```
...
# Find the Top Gear (pun intended) :)
gear = find('/')
pygearsviz.render_hierarchy_tree(gear, name='top_gear_hierarchy_tree', format='svg')
```

Plot the logical module architecture (directed acyclical graph) of a gear (saves the files in the working directory and launches a preview):

```
...
# Find the Top Gear (stopped being funny - if it ever was)
gear = find('/')
pygearsviz.render_dag(gear, name='top_gear_dag', format='svg')
```

### Examples

Run:

```
$ python dag_graphviz.py
$ python depthwise_graphviz.py
```

## Contact

Please report issues and post questions in this [GitHub repo](https://github.com/vladimirtomic/anari-ai).
