from draw import draw_graph
import networkx as nx
from variables import layout_engines, rootless_engines, results_path

graph = nx.nx_agraph.read_dot(results_path + "graph_hier_agraph_rootless.dot")

""" Draw the graph for each layout engine """
for engine in rootless_engines:
    draw_graph(graph, root_node=None,
               name="graph_hier_rootless_" + engine, engine=engine)
