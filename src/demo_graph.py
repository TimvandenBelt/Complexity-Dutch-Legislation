import networkx as nx
import matplotlib.pyplot as plt
from draw import draw_graph

graph = nx.DiGraph()

graph.add_node("A", color="red", label="Node A")
graph.add_node("B", color="blue", label="Node B")
graph.add_edge("A", "B", color="green", label="Edge AB")

draw_graph(graph, name="demo", engine="twopi", root_node=None,
           show_node_labels=True, show_edge_labels=True)
