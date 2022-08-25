from Legal_node import Legal_node
from multiprocessing import Pool
import multiprocess as multiprocessing
import networkx as nx
from extract import *
import csv
from draw import draw_graph
import gc
from variables import results_path
from scipy.stats import linregress
import numpy as np
from draw import draw_squares, draw_sea_square
import pandas

graph = nx.DiGraph()
root_node = Legal_node('root', 'root', 'root')
graph.add_node(root_node.id, type="root", label="root",
               group='root', color="orange")

folders = get_folders()

pool = Pool(processes=multiprocessing.cpu_count())
results = pool.map(process_legislation, folders[:])
pool.close()
pool.join()

if not get_reopened():
    goodList = []
    for result in list(results):
        if result.is_type_wet() and not result.deleted and result.latest_version_path is not None and not result.is_wijzigingswet():
            goodList.append(result.id)
        else:
            # Remove from results list
            results.remove(result)
    save_folders(goodList)



def write_graph(graph, name):
    nx.write_graphml(graph, results_path + "graph_" + name + ".graphml")
    nx.drawing.nx_agraph.write_dot(
        graph, results_path + "graph_" + name + "_agraph.dot")


edges_going_to_legislation = {}

for result in results:
    citation_edges = result.citation_graph.edges(data=True)
    """ if citation_edges[2]["ref"] == "ext", then increment edge_going_to_legislation by one based on the result.id or set it to 1 if result.id is not in the edges_going_to_legislation dictionary """
    for edge in citation_edges:
        if edge[2]["ref"] == "ext":
            """ Get the string edge[1] and grab the legislation id by splitting the string with "/" and get the first element and put it in var id"""
            try:
                id = edge[2]["targetbwb"]
            except:
                id = "no-target"
            if id in edges_going_to_legislation:
                edges_going_to_legislation[id] += 1
            else:
                edges_going_to_legislation[id] = 1

for result in results:
    if result.id in edges_going_to_legislation:
        result.num_citations_in = edges_going_to_legislation[result.id]

""" Loop through all Legislation objects in the results list and use the stat_to_dict function of Legislation which returns a dict of key/value of the statistics and save the dicts to a csv file """
field_names = ["id",
               "title",
               "legal_areas",
               "revisions",
               "nodes",
               "log_nodes",
               "log_section_nodes",
               "text_nodes",
               "nontext_nodes",
               "above_section_nodes",
               "section_nodes",
               "below_section_nodes",
               "mean_depth",
               "mean_leaf_depth",
               "tokens",
               "tokens_per_section",
               "tokens_per_text_node",
               "entropy_lemma",
               "entropy_word",
               "num_words",
               "num_sentences",
               "avg_sentence_length",
               "avg_syllables_per_word",
               "avg_word_length",
               "citations",
               "citations_internal",
               "citations_out",
               "citations_in",
               "citations_external",
               "net_flow",
               "net_flow_per_section",
               "flesch",
               "bijlage_cits",
               "unkown_doc",
               "empty_doc",
               "bad_doc",
               ]

log10_nodes_list = []
log10_section_nodes_list = []
mean_depth_list = []
mean_leaf_depth_list = []
flesch_list = []
entropy_list = []
entropy_lemma_list = []
word_length_list = []
citations_list = []
cit_inout_list = []
cit_total_list = []
num_words_list = []
tokens_per_section_list = []
non_text_nodes_list = []
text_nodes_list = []
above_section_nodes_list = []
below_section_nodes_list = []
revision_list = []
nodes_list = []
flow_list = []
net_flow_per_section_list = []
result_list = []
tok_per_sect_list = []
net_flow_per_section_list = []
net_flow_log10_list = []
stats_results = []
num_tokens_list = []

with open(results_path + 'raw_data.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=field_names, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for result in results:
        if result.is_type_wet() and not result.deleted and result.latest_version_path is not None and not result.is_wijzigingswet():
            result_list.append(result)
            stats_results.append(result.stat_to_dict())
            legislation_stats = result.stat_to_dict()
            writer.writerow(legislation_stats)
            log10_nodes_list.append(legislation_stats["log_nodes"])
            log10_section_nodes_list.append(
                legislation_stats["log_section_nodes"])
            mean_depth_list.append(legislation_stats["mean_depth"])
            mean_leaf_depth_list.append(legislation_stats["mean_leaf_depth"])
            flesch_list.append(legislation_stats["flesch"])
            entropy_list.append(legislation_stats["entropy_word"])
            word_length_list.append(legislation_stats["avg_word_length"])
            num_words_list.append(np.log10(legislation_stats["num_words"]))
            num_tokens_list.append(np.log10(legislation_stats["tokens"]))
            citations_list.append(
                np.log10(legislation_stats["citations_internal"]) if legislation_stats["citations_internal"] > 0 else 0)
            cit_inout_list.append(np.log10(
                legislation_stats["citations_in"] + legislation_stats["citations_out"]) if legislation_stats["citations_in"] + legislation_stats["citations_out"] > 0 else 0)
            cit_total_list.append(np.log10(
                legislation_stats["citations"] + legislation_stats["citations_in"]) if legislation_stats["citations_in"] + legislation_stats["citations"] > 0 else 0)
            tokens_per_section_list.append(
                np.log10(legislation_stats["tokens_per_section"]))
            entropy_lemma_list.append(legislation_stats["entropy_lemma"])
            non_text_nodes_list.append(
                np.log10(legislation_stats["nontext_nodes"]) if legislation_stats["nontext_nodes"] > 0 else 0)
            text_nodes_list.append(np.log10(
                legislation_stats["text_nodes"]) if legislation_stats["text_nodes"] > 0 else 0)
            above_section_nodes_list.append(
                np.log10(legislation_stats["above_section_nodes"]) if legislation_stats["above_section_nodes"] > 0 else 0)
            below_section_nodes_list.append(
                np.log10(legislation_stats["below_section_nodes"]) if legislation_stats["below_section_nodes"] > 0 else 0)
            revision_list.append(np.log10(
                legislation_stats["revisions"]) if legislation_stats["revisions"] > 0 else 0)
            flow_list.append(
                legislation_stats["citations_in"] + legislation_stats["citations_out"])
            nodes_list.append(legislation_stats["nodes"])
            net_flow_per_section_list.append(
                legislation_stats["net_flow_per_section"])
            net_flow_log10_list.append(
                np.log10(legislation_stats["net_flow"]) if legislation_stats["net_flow"] > 0 else 0)
            tok_per_sect_list.append(legislation_stats["tokens_per_section"])

raw_data = pandas.DataFrame(stats_results)
raw_data.to_csv(results_path + "raw.csv", sep=";", index=False,
                quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
raw_data.to_latex(results_path + "raw.tex", index=False,
                  float_format="% .3f", longtable=True)

relation_nodes_and_section_nodes = linregress(
    log10_nodes_list, log10_section_nodes_list)
relation_size_and_mean_depth = linregress(log10_nodes_list, mean_depth_list)
relation_size_and_mean_leaf_depth = linregress(
    log10_nodes_list, mean_leaf_depth_list)
relation_size_and_flesch = linregress(log10_nodes_list, flesch_list)
relation_size_and_entropy = linregress(log10_nodes_list, entropy_list)
relation_size_and_entropy_lemma = linregress(
    log10_nodes_list, entropy_lemma_list)
relation_size_and_word_length = linregress(
    log10_nodes_list, word_length_list)
relation_size_and_citations = linregress(log10_nodes_list, citations_list)
relation_size_and_cit_inout = linregress(log10_nodes_list, cit_inout_list)
relation_size_and_cit_total = linregress(log10_nodes_list, cit_total_list)
relation_size_and_num_words = linregress(log10_nodes_list, num_words_list)
relation_num_words_and_flesch = linregress(num_words_list, flesch_list)
relation_size_and_tokens_per_section = linregress(
    log10_nodes_list, tokens_per_section_list)
relation_tokens_per_section_and_flesch = linregress(
    tokens_per_section_list, flesch_list)
relation_flesch_and_word_length = linregress(flesch_list, word_length_list)
relation_size_and_revisions = linregress(log10_nodes_list, revision_list)
relation_flesch_and_revisions = linregress(flesch_list, revision_list)
relation_mean_depth_and_revisions = linregress(mean_depth_list, revision_list)
relation_size_and_text_nodes = linregress(log10_nodes_list, text_nodes_list)
relation_size_and_non_text_nodes = linregress(
    log10_nodes_list, non_text_nodes_list)
relation_size_and_below_section_nodes = linregress(
    log10_nodes_list, below_section_nodes_list)
relation_size_and_above_section_nodes = linregress(
    log10_nodes_list, above_section_nodes_list)
relation_sections_and_above_sections = linregress(
    log10_section_nodes_list, above_section_nodes_list)
relation_sections_and_below_sections = linregress(
    log10_section_nodes_list, below_section_nodes_list)
relation_above_and_below_sections = linregress(
    above_section_nodes_list, below_section_nodes_list)
relation_size_and_flow_per_section = linregress(
    log10_nodes_list, net_flow_per_section_list)
relation_size_and_net_flow = linregress(
    log10_nodes_list, net_flow_log10_list)
relation_size_and_tokens = linregress(
    log10_nodes_list, num_tokens_list)


with open(results_path + 'correlation.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
                            "Correlation", "P value", "R value", "Slope", "Intercept", "R squared percentage"])
    writer.writeheader()

    writer.writerow({"Correlation": "Size & section nodes", "P value": relation_nodes_and_section_nodes.pvalue, "R value": relation_nodes_and_section_nodes.rvalue,
                    "Slope": relation_nodes_and_section_nodes.slope, "Intercept": relation_nodes_and_section_nodes.intercept, "R squared percentage": np.square(relation_nodes_and_section_nodes.rvalue) * 100})

    writer.writerow({"Correlation": "Size & above section nodes", "P value": relation_size_and_above_section_nodes.pvalue, "R value": relation_size_and_above_section_nodes.rvalue,
                     "Slope": relation_size_and_above_section_nodes.slope, "Intercept": relation_size_and_above_section_nodes.intercept, "R squared percentage": np.square(relation_size_and_above_section_nodes.rvalue) * 100})

    writer.writerow({"Correlation": "Size & below section nodes", "P value": relation_size_and_below_section_nodes.pvalue, "R value": relation_size_and_below_section_nodes.rvalue,
                     "Slope": relation_size_and_below_section_nodes.slope, "Intercept": relation_size_and_below_section_nodes.intercept, "R squared percentage": np.square(relation_size_and_below_section_nodes.rvalue) * 100})

    writer.writerow({"Correlation": "Size & text nodes", "P value": relation_size_and_text_nodes.pvalue, "R value": relation_size_and_text_nodes.rvalue,
                    "Slope": relation_size_and_text_nodes.slope, "Intercept": relation_size_and_text_nodes.intercept, "R squared percentage": np.square(relation_size_and_text_nodes.rvalue) * 100})

    writer.writerow({"Correlation": "Size & non-text nodes", "P value": relation_size_and_non_text_nodes.pvalue, "R value": relation_size_and_non_text_nodes.rvalue,
                    "Slope": relation_size_and_non_text_nodes.slope, "Intercept": relation_size_and_non_text_nodes.intercept, "R squared percentage": np.square(relation_size_and_non_text_nodes.rvalue) * 100})

    writer.writerow({"Correlation": "Sections & above section nodes", "P value": relation_sections_and_above_sections.pvalue, "R value": relation_sections_and_above_sections.rvalue,
                     "Slope": relation_sections_and_above_sections.slope, "Intercept": relation_sections_and_above_sections.intercept, "R squared percentage": np.square(relation_sections_and_above_sections.rvalue) * 100})

    writer.writerow({"Correlation": "Sections & below section nodes", "P value": relation_sections_and_below_sections.pvalue, "R value": relation_sections_and_below_sections.rvalue,
                     "Slope": relation_sections_and_below_sections.slope, "Intercept": relation_sections_and_below_sections.intercept, "R squared percentage": np.square(relation_sections_and_below_sections.rvalue) * 100})

    writer.writerow({"Correlation": "Above section & below section nodes", "P value": relation_above_and_below_sections.pvalue, "R value": relation_above_and_below_sections.rvalue,
                     "Slope": relation_above_and_below_sections.slope, "Intercept": relation_above_and_below_sections.intercept, "R squared percentage": np.square(relation_above_and_below_sections.rvalue) * 100})

    writer.writerow({"Correlation": "Size & mean depth", "P value": relation_size_and_mean_depth.pvalue, "R value": relation_size_and_mean_depth.rvalue,
                    "Slope": relation_size_and_mean_depth.slope, "Intercept": relation_size_and_mean_depth.intercept, "R squared percentage": np.square(relation_size_and_mean_depth.rvalue) * 100})

    writer.writerow({"Correlation": "Size & mean leaf depth", "P value": relation_size_and_mean_leaf_depth.pvalue, "R value": relation_size_and_mean_leaf_depth.rvalue,
                    "Slope": relation_size_and_mean_leaf_depth.slope, "Intercept": relation_size_and_mean_leaf_depth.intercept, "R squared percentage": np.square(relation_size_and_mean_leaf_depth.rvalue) * 100})

    writer.writerow({"Correlation": "Size & Flesch", "P value": relation_size_and_flesch.pvalue, "R value": relation_size_and_flesch.rvalue,
                    "Slope": relation_size_and_flesch.slope, "Intercept": relation_size_and_flesch.intercept, "R squared percentage": np.square(relation_size_and_flesch.rvalue) * 100})

    writer.writerow({"Correlation": "Size & word entropy", "P value": relation_size_and_entropy.pvalue, "R value": relation_size_and_entropy.rvalue,
                    "Slope": relation_size_and_entropy.slope, "Intercept": relation_size_and_entropy.intercept, "R squared percentage": np.square(relation_size_and_entropy.rvalue) * 100})

    writer.writerow({"Correlation": "Size & lemmatised word entropy", "P value": relation_size_and_entropy_lemma.pvalue, "R value": relation_size_and_entropy_lemma.rvalue,
                    "Slope": relation_size_and_entropy_lemma.slope, "Intercept": relation_size_and_entropy_lemma.intercept, "R squared percentage": np.square(relation_size_and_entropy_lemma.rvalue) * 100})

    writer.writerow({"Correlation": "Size & word length", "P value": relation_size_and_word_length.pvalue, "R value": relation_size_and_word_length.rvalue,
                    "Slope": relation_size_and_word_length.slope, "Intercept": relation_size_and_word_length.intercept, "R squared percentage": np.square(relation_size_and_word_length.rvalue) * 100})

    writer.writerow({"Correlation": "Size & net flow per section", "P value": relation_size_and_flow_per_section.pvalue, "R value": relation_size_and_flow_per_section.rvalue,
                    "Slope": relation_size_and_flow_per_section.slope, "Intercept": relation_size_and_flow_per_section.intercept, "R squared percentage": np.square(relation_size_and_flow_per_section.rvalue) * 100})

    writer.writerow({"Correlation": "Size & net flow", "P value": relation_size_and_net_flow.pvalue, "R value": relation_size_and_net_flow.rvalue,
                     "Slope": relation_size_and_net_flow.slope, "Intercept": relation_size_and_net_flow.intercept, "R squared percentage": np.square(relation_size_and_net_flow.rvalue) * 100})

    writer.writerow({"Correlation": "Size & internal citations", "P value": relation_size_and_citations.pvalue, "R value": relation_size_and_citations.rvalue,
                    "Slope": relation_size_and_citations.slope, "Intercept": relation_size_and_citations.intercept, "R squared percentage": np.square(relation_size_and_citations.rvalue) * 100})

    writer.writerow({"Correlation": "Size & external citations", "P value": relation_size_and_cit_inout.pvalue, "R value": relation_size_and_cit_inout.rvalue,
                    "Slope": relation_size_and_cit_inout.slope, "Intercept": relation_size_and_cit_inout.intercept, "R squared percentage": np.square(relation_size_and_cit_inout.rvalue) * 100})

    writer.writerow({"Correlation": "Size & citations total", "P value": relation_size_and_cit_total.pvalue, "R value": relation_size_and_cit_total.rvalue,
                    "Slope": relation_size_and_cit_total.slope, "Intercept": relation_size_and_cit_total.intercept, "R squared percentage": np.square(relation_size_and_cit_total.rvalue) * 100})

    writer.writerow({"Correlation": "Size & tokens per section", "P value": relation_size_and_tokens_per_section.pvalue, "R value": relation_size_and_tokens_per_section.rvalue,
                    "Slope": relation_size_and_tokens_per_section.slope, "Intercept": relation_size_and_tokens_per_section.intercept, "R squared percentage": np.square(relation_size_and_tokens_per_section.rvalue) * 100})

    writer.writerow({"Correlation": "Size & number of words", "P value": relation_size_and_num_words.pvalue, "R value": relation_size_and_num_words.rvalue,
                    "Slope": relation_size_and_num_words.slope, "Intercept": relation_size_and_num_words.intercept, "R squared percentage": np.square(relation_size_and_num_words.rvalue) * 100})

    writer.writerow({"Correlation": "Flesch & word length", "P value": relation_flesch_and_word_length.pvalue, "R value": relation_flesch_and_word_length.rvalue,
                    "Slope": relation_flesch_and_word_length.slope, "Intercept": relation_flesch_and_word_length.intercept, "R squared percentage": np.square(relation_flesch_and_word_length.rvalue) * 100})

    writer.writerow({"Correlation": "Flesch & number of words", "P value": relation_num_words_and_flesch.pvalue, "R value": relation_num_words_and_flesch.rvalue,
                    "Slope": relation_num_words_and_flesch.slope, "Intercept": relation_num_words_and_flesch.intercept, "R squared percentage": np.square(relation_num_words_and_flesch.rvalue) * 100})

    writer.writerow({"Correlation": "Flesch & tokens per section", "P value": relation_tokens_per_section_and_flesch.pvalue, "R value": relation_tokens_per_section_and_flesch.rvalue,
                    "Slope": relation_tokens_per_section_and_flesch.slope, "Intercept": relation_tokens_per_section_and_flesch.intercept, "R squared percentage": np.square(relation_tokens_per_section_and_flesch.rvalue) * 100})

    writer.writerow({"Correlation": "Size & number of tokens", "P value": relation_size_and_tokens.pvalue, "R value": relation_size_and_tokens.rvalue,
                     "Slope": relation_size_and_tokens.slope, "Intercept": relation_size_and_tokens.intercept, "R squared percentage": np.square(relation_size_and_tokens.rvalue) * 100})


draw_sea_square(x=log10_nodes_list, y=log10_section_nodes_list, xlabel="log10(Nodes)", ylabel="log10(Section nodes)",
                relation=relation_nodes_and_section_nodes, name="Nodes and section nodes regression")

draw_sea_square(x=log10_nodes_list, y=mean_depth_list, xlabel="log10(Nodes)", ylabel="Mean depth",
                relation=relation_size_and_mean_depth, name="Size and mean depth regression")

draw_sea_square(x=log10_nodes_list, y=mean_leaf_depth_list, xlabel="log10(Nodes)", ylabel="Mean leaf depth",
                relation=relation_size_and_mean_leaf_depth, name="Size and mean leaf depth regression")

draw_sea_square(x=log10_nodes_list, y=flesch_list, xlabel="log10(Nodes)", ylabel="Flesch score",
                relation=relation_size_and_flesch, name="Size and Flesch score regression")

draw_sea_square(x=log10_nodes_list, y=entropy_list, xlabel="log10(Nodes)", ylabel="Word entropy",
                relation=relation_size_and_entropy, name="Size and word entropy regression")

draw_sea_square(x=log10_nodes_list, y=entropy_lemma_list, xlabel="log10(Nodes)", ylabel="Lemmatised word entropy",
                relation=relation_size_and_entropy_lemma, name="Size and lemmatised word entropy regression")

draw_sea_square(x=log10_nodes_list, y=word_length_list, xlabel="log10(Nodes)", ylabel="Avarage word length",
                relation=relation_size_and_word_length, name="Size and avarage word length regression")

draw_sea_square(x=log10_nodes_list, y=citations_list, xlabel="log10(Nodes)", ylabel="log10(Internal citations)",
                relation=relation_size_and_citations, name="Size and internal citations regression")

draw_sea_square(x=log10_nodes_list, y=cit_inout_list, xlabel="log10(Nodes)", ylabel="log10(External citations)",
                relation=relation_size_and_cit_inout, name="Size and external citations regression")

draw_sea_square(x=log10_nodes_list, y=cit_total_list, xlabel="log10(Nodes)", ylabel="log10(Total citations)",
                relation=relation_size_and_cit_total, name="Size and total citations regression")

draw_sea_square(x=log10_nodes_list, y=num_words_list, xlabel="log10(Nodes)", ylabel="Number of words",
                relation=relation_size_and_num_words, name="Size and number of words regression")

draw_sea_square(x=num_words_list, y=flesch_list, xlabel="log10(Number of words)", ylabel="Flesch score",
                relation=relation_num_words_and_flesch, name="Flesch score and Number of words regression")

draw_sea_square(x=log10_nodes_list, y=tokens_per_section_list, xlabel="log10(nodes)", ylabel="log10(Tokens per section)",
                relation=relation_size_and_tokens_per_section, name="Size and tokens per section regression")

draw_sea_square(x=tokens_per_section_list, y=flesch_list, xlabel="log10(Tokens per section)", ylabel="Flesch score",
                relation=relation_tokens_per_section_and_flesch, name="Flesch score and Tokens per section regression")

draw_sea_square(x=word_length_list, y=flesch_list, xlabel="Avarage word length", ylabel="Flesch score",
                relation=relation_flesch_and_word_length, name="Flesch score and avarage word length regression")

draw_sea_square(x=log10_nodes_list, y=revision_list, xlabel="log10(Nodes)", ylabel="log10(Revisions)",
                relation=relation_size_and_revisions, name="Size and revisions regression")

draw_sea_square(x=flesch_list, y=revision_list, xlabel="Flesch score", ylabel="log10(Revisions)",
                relation=relation_flesch_and_revisions, name="Flesch score and revisions regression")

draw_sea_square(x=mean_depth_list, y=revision_list, xlabel="Mean depth", ylabel="log10(Revisions)",
                relation=relation_mean_depth_and_revisions, name="Mean depth and revisions regression")

draw_sea_square(x=log10_nodes_list, y=text_nodes_list, xlabel="log10(Nodes)", ylabel="log10(Text nodes)",
                relation=relation_size_and_text_nodes, name="Size and text nodes regression")

draw_sea_square(x=log10_nodes_list, y=non_text_nodes_list, xlabel="log10(Nodes)", ylabel="log10(Non text nodes)",
                relation=relation_size_and_non_text_nodes, name="Size and non text nodes regression")

draw_sea_square(x=log10_nodes_list, y=below_section_nodes_list, xlabel="log10(Nodes)", ylabel="log10(Below section nodes)",
                relation=relation_size_and_below_section_nodes, name="Size and below section nodes regression")

draw_sea_square(x=log10_nodes_list, y=above_section_nodes_list, xlabel="log10(Nodes)", ylabel="log10(Above section nodes)",
                relation=relation_size_and_above_section_nodes, name="Size and above section nodes regression")

draw_sea_square(x=log10_section_nodes_list, y=above_section_nodes_list, xlabel="log10(Section nodes)", ylabel="log10(Above section nodes)",
                relation=relation_sections_and_above_sections, name="Section and above section nodes regression")

draw_sea_square(x=log10_section_nodes_list, y=below_section_nodes_list, xlabel="log10(Section nodes)", ylabel="log10(Below section nodes)",
                relation=relation_sections_and_below_sections, name="Section and below section nodes regression")

draw_sea_square(x=above_section_nodes_list, y=below_section_nodes_list, xlabel="log10(Above section nodes)", ylabel="log10(Below section nodes)",
                relation=relation_above_and_below_sections, name="Above and below section nodes regression")

draw_sea_square(x=log10_nodes_list, y=net_flow_per_section_list, xlabel="log10(Nodes)", ylabel="Net flow per section",
                relation=relation_above_and_below_sections, name="Size and net flow per section regression")

draw_sea_square(x=log10_nodes_list, y=net_flow_log10_list, xlabel="log10(Nodes)", ylabel="log10(Net flow)",
                relation=relation_above_and_below_sections, name="Size and net flow regression")

draw_sea_square(x=log10_nodes_list, y=num_tokens_list, xlabel="log10(Nodes)", ylabel="log10(tokens)",
                relation=relation_above_and_below_sections, name="Size and number of tokens")

for result in results:
    combine_graphs(graph, result.hierarchical_graph, root_node=root_node,
                   legislation_id=result.label_id, add_root_edge=True)


write_graph(graph, "hier")

rootless_graph = graph.copy()
rootless_graph.remove_node("root")

write_graph(rootless_graph, "hier_rootless")

del rootless_graph
gc.collect()

cit_graph = nx.DiGraph()
for result in results:
    combine_graphs(graph, result.citation_graph, result.label_id)
    combine_graphs(cit_graph, result.citation_graph)
    

write_graph(graph, "cit")

graph.remove_node("root")
write_graph(graph, "cit_rootless")
