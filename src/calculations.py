import variables as var
import networkx as nx

""" This file will contain the functions that will be used to calculate the necessary values for the research """

""" 
--------------------------------------------------------------------------------------------------------------------
Network calculations
--------------------------------------------------------------------------------------------------------------------
"""

""" Get a list of all the nodes in the networkx graph except the root node and calculate the mean of the shortest paths lengths to the root node """


def calculate_avg_node_depth(graph, root_node):
    try:
        return sum([nx.shortest_path_length(graph, source=root_node.id, target=node) for node in graph.nodes()]) / graph.number_of_nodes()
    except:
        print("Could not calculate the average node depth")
        return 0


""" Get all leaf nodes from the networkx graph and calculate the mean depth of the leaf nodes """


def calculate_avg_leaf_depth(graph, root_node):
    try:
        leaf_nodes = [node for node in graph.nodes()
                      if graph.degree(node) == 1]
        leaf_nodes_shortest_paths = [nx.shortest_path_length(
            graph, source=root_node.id, target=node) for node in leaf_nodes]
        return sum(leaf_nodes_shortest_paths) / len(leaf_nodes_shortest_paths)
    except:
        print("Could not calculate the average leaf depth")
        return 0


""" 
--------------------------------------------------------------------------------------------------------------------
Structure calculations
--------------------------------------------------------------------------------------------------------------------
"""

""" Calculate the number of nodes in the networkx graph """


def calculate_number_of_nodes(graph):
    try:
        return graph.number_of_nodes()
    except:
        print("Could not calculate the number of nodes")
        return 0


""" Calculate the number of edges in the networkx graph """


def calculate_number_of_edges(graph):
    try:
        return graph.number_of_edges()
    except:
        print("Could not calculate the number of edges")
        return 0


""" Calculate the amount of nodes per type as defined in the variables.py file's structure_list """


def calculate_number_of_nodes_per_type(graph):
    try:
        #  for type in structure_list:
        #         self.number_of_nodes_by_type[type] = len(
        #             [node for node in self.nodes if node.type == type])
        return {x: len(list(y for y in graph.nodes() if graph.nodes[y]['type'] == x)) for x in var.structure_list}
    except:
        print("Could not calculate the number of nodes per type")
        return 0


def calculate_readability_score(avg_sentence_length, avg_word_length):
    """ Calculate the readability score of the text using the readability metric of Rudolf Flesch """
    try:
        return 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
    except:
        print("Could not calculate the readability score")
        return 0
