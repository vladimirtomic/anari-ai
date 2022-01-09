# Anari AI - PyGearsViz

## Introduction

PyGearsViz is a python3 Anari AI PyGears architecture visualization tool. It is based on Graphviz and provides two utility methods:

- `render_hierarchy_tree(gear, name, format)` - plots a Graphviz hierarchy tree representing the PyGears module hierarchy starting from the provided gear; optionally provide the file name (default `hierarchy_tree`) and export format (default `pdf`)

- `render_dag(gear, name, format)` - plots a Graphviz DAG (directed acyclic graph) representing the logical architecture (modules and "wires") of a PyGears module

## Setup

This project was developed using a Mac with [MS Visual Studio Code](https://code.visualstudio.com/download#). [Python 3.10.1](https://www.python.org/downloads/) was installed in a dedicated [pyenv](https://github.com/pyenv/pyenv) environment. [Graphviz 2.50.0](https://graphviz.org/download/) and pyenv were installed using [homebrew](https://brew.sh/).

Install python dependencies:

```
pip install -r requirements.txt
```

## Usage

To use PyGearsViz import it:

```import pygearsviz```

Plot the module hierarchy tree of a gear:

```
...
# Find the Top Gear (pun intended) :)
gear = find('/')
pygearsviz.render_hierarchy_tree(gear, name='grand_tour_hierarchy_tree', format='pdf')
```

Plot the logical module architecture (directed acyclical graph) of a gear:

```
...
# Find the Top Gear (stopped being funny - if it ever was)
gear = find('/')
pygearsviz.render_dag(gear, name='grand_tour_dag', format='pdf')
```

### Examples

Run:

```
$ python dag_graphviz.py
$ python depthwise_graphviz.py
```

## Contact

Please report issues and post questions in this [GitHub repo](https://github.com/vladimirtomic/anari-ai).
