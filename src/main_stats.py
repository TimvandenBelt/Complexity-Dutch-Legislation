from variables import results_path
import pandas
import matplotlib.pyplot as plt
import statistics


def calculate_mean(values):
    return statistics.mean(values)


def calculate_median(values):
    return statistics.median(values)


def calculate_standard_deviation(values):
    return statistics.stdev(values)


def calculate_pstandard_deviation(values):
    return statistics.pstdev(values)


def calc_stats_of_values(values, name):
    mean = calculate_mean(values)
    median = calculate_median(values)
    standard_deviation = calculate_standard_deviation(values)
    pstandard_deviation = calculate_pstandard_deviation(values)
    return {"name": name, "mean": mean, "median": median, "standard_deviation": standard_deviation, "pstandard_deviation": pstandard_deviation}


vars_to_calculate_stats_for = [
    "nodes", "text_nodes", "nontext_nodes", "above_section_nodes", "below_section_nodes", "section_nodes", "tokens", "tokens_per_section", "tokens_per_text_node", "entropy_lemma", "entropy_word",
    "num_words", "num_sentences", "avg_sentence_length", "avg_syllables_per_word", "avg_word_length", "citations", "citations_internal", "citations_in", "citations_out", "citations_external", "net_flow", "net_flow_per_section", "flesch", "mean_depth", "mean_leaf_depth"]


def get_stats_from_dataframe(dataframe):

    stats_for_vars = {}
    for var in vars_to_calculate_stats_for:
        stats_for_vars[var] = []
        for i in range(len(raw_data)):
            stats_for_vars[var].append(raw_data[var][i])

    """ For every vars_to_calculate_stats_for,  calculate the stats and add them to a dictionary. """

    stats_for_vars_dict = []
    for var in vars_to_calculate_stats_for:
        stats_for_vars_dict.append(calc_stats_of_values(
            stats_for_vars[var], var))

    return pandas.DataFrame.from_dict(stats_for_vars_dict)


raw_data = pandas.read_csv(results_path + "raw.csv", sep=";",
                           quotechar='"')

stats_data = get_stats_from_dataframe(raw_data)
stats_data.to_csv(results_path + "stats.csv", sep=";", quotechar='"')


for var in vars_to_calculate_stats_for:
    plt.scatter(raw_data[var], raw_data["nontext_nodes"])

raw_data.astype({
    "revisions": 'int32',
    "nodes": 'int32',
    "log_nodes": 'float',
    "log_section_nodes": 'float',
    "text_nodes": 'int32',
    "nontext_nodes": 'int32',
    "above_section_nodes": 'int32',
    "below_section_nodes": 'int32',
    "section_nodes": 'int32',
    "mean_depth": 'float',
    "mean_leaf_depth": 'float',
    "tokens": 'int32',
    "tokens_per_section": 'float',
    "tokens_per_text_node": 'float',
    "entropy_lemma": 'float',
    "entropy_word": 'float',
    "num_words": 'int32',
    "num_sentences": 'int32',
    "avg_sentence_length": 'float',
    "avg_syllables_per_word": 'float',
    "avg_word_length": 'float',
    "citations": 'int32',
    "citations_internal": 'int32',
    "citations_in": 'int32',
    "citations_out": 'int32',
    "citations_external": 'int32',
    "net_flow": 'int32',
    "net_flow_per_section": 'float',
    "flesch": 'float',
    "unkown_doc": 'int32',
    "empty_doc": 'int32',
    "bijlage_cits": 'int32',
    "bad_doc": 'int32',
})

id_id = raw_data.columns.get_loc("id")
title_id = raw_data.columns.get_loc("title")

ID_and_title_table = raw_data.iloc[:, [id_id, title_id]]
ID_and_title_table.columns = ["id", "title"]

raw_data = raw_data.drop(columns=["title", "legal_areas"])
""" The row values of column named "id" will be the column names of the new table """
raw_data = raw_data.set_index("id")
raw_data = raw_data.transpose()
raw_data.round(0)

tables = []
""" For each 10 columns, create a new table where the first column is always the row header from the raw_data """
for i in range(0, len(raw_data.columns), 10):
    table = raw_data.iloc[:, i:i+10]
    table.columns = raw_data.columns[i:i+10]
    tables.append(table)


i = 0
for table in tables:
    # table.to_latex(results_path + "raw" + str(i) + ".tex", index=True,
    #                float_format="% .3f", bold_rows=True)
    table.style.format(precision=3, escape="latex").format_index(escape="latex", axis=1).format_index(escape="latex", axis=0).to_latex(results_path + "raw" + str(i) +
                                                                                                                                       ".tex", hrules=True, clines="all;data")
    i += 1
ID_and_title_table["title"].str.wrap(30)
ID_and_title_table.style.hide(axis='index').to_latex(
    results_path + "raw_index.tex", hrules=True, clines="all;data", environment="longtable")
