from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout as graphviz_layout
from scour import scour
from variables import results_path
import pandas
import seaborn as sns


graphiz_engines = ["twopi", "circo", "sfdp", "dot", "neato", "osage"]
dpi = 600


def get_pos(graph, root_node=None, engine="twopi"):
    if engine in graphiz_engines:
        return graphviz_layout(graph, prog=engine,
                               root=root_node, args="-Gcenter=true -Gconcentrate=true -Gdpi=" + str(dpi) + " -Gsmoothing=avg_dist -Goverlap=scale")
    if engine == "circular":
        return nx.circular_layout(graph)
    if engine == "kamada_kawai":
        return nx.kamada_kawai_layout(graph)
    if engine == "planar":
        return nx.planar_layout(graph)
    if engine == "shell":
        return nx.shell_layout(graph)
    if engine == "spectral":
        return nx.spectral_layout(graph)
    if engine == "spiral":
        return nx.spiral_layout(graph)
    if engine == "multipartite":
        return nx.multipartite_layout(graph, subset_key="group")
    if engine == "multipartite_layout":
        return nx.multipartite_layout(graph, subset_key="group")

    raise NotImplementedError("Engine not implemented")


def draw_graph(graph, root_node, name="graph", engine="twopi", show_node_labels=False, show_edge_labels=False):
    print("Start drawing a " + engine + " graph at " + str(datetime.now()))
    start = datetime.now()
    fig = plt.figure(figsize=(12, 12), dpi=dpi)
    # plt.figure()

    node_colors = []
    edge_colors = []
    node_labels = []
    edge_labels = []

    for node in graph.nodes(data=True):
        try:
            color = node[1]["color"]
        except KeyError:
            color = "blue"
        node_colors.append(color)
        if show_node_labels:
            try:
                label = node[1]["label"]
            except KeyError:
                label = None
            node_labels.append(label)

    for edge in graph.edges(data=True):
        try:
            color = edge[2]["color"]
        except KeyError:
            color = "black"
        edge_colors.append(color)
        if show_node_labels:
            try:
                label = edge[2]["label"]
            except KeyError:
                label = None
            edge_labels.append(label)

    pos = get_pos(graph, root_node, engine)
    print("Received positions")

    plt.margins(0.05)
    plt.axis("off")
    plt.box(False)

    nx.draw(graph, pos, with_labels=True if show_node_labels or show_edge_labels else False, labels=node_labels,
            node_color=node_colors, edge_color=edge_colors, node_size=0.75, alpha=1, arrowsize=0.075, width=0.05)

    cut = 1.05
    xmax = max(xx for xx, yy in pos.values())
    ymax = max(yy for xx, yy in pos.values())
    xmin = min(xx for xx, yy in pos.values())
    ymin = min(yy for xx, yy in pos.values())

    xincrease = (cut - 1) * xmax
    yincrease = (cut - 1) * ymax

    plt.xlim(xmin - xincrease, cut * xmax)
    plt.ylim(ymin - yincrease, cut * ymax)

    plt.savefig(results_path + name + '_agg.png', dpi=dpi, format='png',
                transparent=True, bbox_inches='tight')
    plt.savefig(results_path + name + ".svg", format="svg", dpi=dpi,
                transparent=True, bbox_inches='tight')
    plt.savefig(results_path + name + ".eps", format="eps",
                dpi=dpi, bbox_inches='tight')
    try:
        fig.clf()
        fig.clf()
        fig.close()
    except Exception:
        pass
    plt.close('all')

    with open(results_path + name + ".svg", 'r') as f:
        svg = f.read()

    print("Cleaning SVG")

    try:
        scour_options = scour.sanitizeOptions()
        scour_options.remove_metadata = True
        scour_options.create_groups = True
        scour_options.remove_descriptive_elements = True
        scour_options.enable_comment_stripping = True
        scour_options.no_line_breaks = True
        scour_options.enable_id_stripping = True
        scour_options.shorten_ids = True
        scour_options.simple_colors = True
        clean_svg = scour.scourString(svg, options=scour_options)
        svg_file = open(results_path + name + "_clean.svg", "w")
        svg_file.write(clean_svg)
        svg_file.close()
    except Exception:
        print("Cleaning SVG went wrong")
    print("Done cleaning SVG")

    end = datetime.now()
    print("Finished drawing a " + engine + " graph")

    print("Total time for drawing: "
          + str((end - start).seconds // 60) + " minutes, "
          + str((end - start).seconds % 60) + " seconds and "
          + str((end - start).microseconds // 1000) + " miliseconds")
    print("Done drawing at " + str(datetime.now()))
    print("-----------------------------------------------------")

    return True


def draw_sea_square(x, y, xlabel, ylabel, name, relation=None):
    data = pandas.DataFrame({xlabel: x, ylabel: y})
    fig, ax = plt.subplots(figsize=(12, 12), dpi=dpi)
    sns.set_theme(color_codes=True)
    ax.set_title(name)
    sns.jointplot(x=xlabel, y=ylabel, data=data, kind="reg", label=name, ax=ax)
    name = name.replace(" ", "_")
    plt.savefig(results_path + name + ".png", dpi=dpi, format='png',
                transparent=True, bbox_inches='tight')
    try:
        fig.clf()
        fig.clf()
        fig.close()
    except Exception:
        pass
    plt.close('all')


def draw_squares(x, y, xlabel, ylabel, relation, name):
    slope = relation.slope
    intercept = relation.intercept
    pvalue = relation.pvalue
    rvalue = relation.rvalue
    print("Start drawing a " + name + " regression at " + str(datetime.now()))
    start = datetime.now()
    fig = plt.figure(figsize=(12, 12), dpi=dpi)
    plt.style.use('seaborn-whitegrid')
    plt.scatter(x, y, s=1.5)
    x0 = min(x)
    y0 = intercept + slope * x0
    x1 = max(x)
    y1 = intercept + slope * x1
    plt.plot([x0, x1], [y0, y1], "k--", linewidth=1)
    plt.xlabel(xlabel, fontsize=13)
    plt.ylabel(ylabel, fontsize=13)
    plt.title(name, fontsize=15)

    name = name.replace(" ", "_")

    plt.savefig(results_path + name + '_agg.png', dpi=dpi, format='png',
                transparent=True, bbox_inches='tight')
    plt.savefig(results_path + name + ".svg", format="svg", dpi=dpi,
                transparent=True, bbox_inches='tight')
    plt.savefig(results_path + name + ".eps", format="eps",
                dpi=dpi, bbox_inches='tight')

    with open(results_path + name + ".svg", 'r') as f:
        svg = f.read()

    print("Cleaning SVG")

    try:
        scour_options = scour.sanitizeOptions()
        scour_options.remove_metadata = True
        scour_options.create_groups = True
        scour_options.remove_descriptive_elements = True
        scour_options.enable_comment_stripping = True
        scour_options.no_line_breaks = True
        scour_options.enable_id_stripping = True
        scour_options.shorten_ids = True
        scour_options.simple_colors = True
        clean_svg = scour.scourString(svg, options=scour_options)
        svg_file = open(results_path + name + "_clean.svg", "w")
        svg_file.write(clean_svg)
        svg_file.close()
    except Exception:
        print("Cleaning SVG went wrong")
    print("Done cleaning SVG")

    plt.cla()
    plt.clf()
    plt.close(fig)
    end = datetime.now()
    print("Finished drawing a " + name + " regression")

    data_frame = pandas.DataFrame({"x": x, "t": y})
    data_frame.to_pickle(results_path + name + ".pkl", protocol=0)

    print("Total time for drawing: "
          + str((end - start).seconds // 60) + " minutes, "
          + str((end - start).seconds % 60) + " seconds and "
          + str((end - start).microseconds // 1000) + " miliseconds")
    print("Done drawing at " + str(datetime.now()))
    print("-----------------------------------------------------")