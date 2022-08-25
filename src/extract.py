import os
import pickle
from Legislation import Legislation

global reopened
reopened = False


def get_reopened():
    global reopened
    return reopened


def set_reopened(status):
    global reopened
    reopened = status


def save_folders(folders):
    with open('folders.pickle', 'wb') as f:
        pickle.dump(folders, f)


def get_folders(path='/data', caching=True):
    if os.path.isfile('folders.pickle') and caching:
        with open('folders.pickle', 'rb') as f:
            folders = pickle.load(f)
        set_reopened(True)
    else:
        folders = []
        for folder in os.listdir(path):
            if os.path.isdir(os.path.join(path, folder)):
                folders.append(folder)
    return folders


def process_legislation(folder):
    try:
        legislation = Legislation(folder)
    except FileNotFoundError:
        legislation = None
        pass
    return legislation


def combine_graphs(graph, graph2, root_node=Legislation, legislation_id=None, add_root_edge=False):
    nodes = graph2.nodes(data=True)
    graph.add_nodes_from(nodes)
    graph.add_edges_from(graph2.edges(data=True))
    if add_root_edge:
        graph.add_edge(root_node.id, legislation_id,
                       color="black", group=legislation_id, type="h")
