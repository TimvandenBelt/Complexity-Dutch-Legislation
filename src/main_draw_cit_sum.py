from draw import draw_graph
import networkx as nx
from variables import layout_engines, rootless_engines, results_path

graph = nx.nx_agraph.read_dot(results_path + "graph_sum_cit_agraph.dot")

root_node = "root"
for node in graph.nodes(data=True):
    if node[0] == "root":
        root_node = node[0]
        break

""" Draw the graph for each layout engine """
for engine in layout_engines:
    draw_graph(graph, root_node=root_node,
               name="graph_cit_sum_" + engine, engine=engine)
