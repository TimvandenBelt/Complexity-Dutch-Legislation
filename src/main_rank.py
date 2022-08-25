from variables import results_path
import pandas

unnormalized_variables = ["nodes", "entropy_word", "net_flow"]
normalized_variables = ["flesch", "net_flow_per_section", "tokens_per_section"]

raw_data = pandas.read_csv(results_path + "raw.csv", sep=";",
                           quotechar='"', dtype={"nodes": "int32", "entropy_word": "float", "net_flow": "int32", "flesch": "float", "net_flow_per_section": "float", "tokens_per_section": "float"})

raw_data = raw_data.drop(columns=["revisions",
                                  "log_nodes",
                                  "log_section_nodes",
                                  "text_nodes",
                                  "nontext_nodes",
                                  "above_section_nodes",
                                  "below_section_nodes",
                                  "section_nodes",
                                  "mean_depth",
                                  "mean_leaf_depth",
                                  "tokens",
                                  "tokens_per_text_node",
                                  "entropy_lemma",
                                  "num_words",
                                  "num_sentences",
                                  "avg_sentence_length",
                                  "avg_syllables_per_word",
                                  "avg_word_length",
                                  "citations",
                                  "citations_internal",
                                  "citations_in",
                                  "citations_out",
                                  "citations_external",
                                  "unkown_doc",
                                  "empty_doc",
                                  "bijlage_cits",
                                  "bad_doc",
                                  "title",
                                  "legal_areas"])
    
print(raw_data)    
    
raw_data["nodes_rank"] = raw_data["nodes"].rank(
    ascending=False, method='max')
print(raw_data)
raw_data["entropy_word_rank"] = raw_data["entropy_word"].rank(
    ascending=False, method='max')
raw_data["net_flow_rank"] = raw_data["net_flow"].rank(
    ascending=False, method='max')

raw_data["flesch_rank"] = raw_data["flesch"].rank(
    ascending=False, method='min')
raw_data["net_flow_per_section_rank"] = raw_data["net_flow_per_section"].rank(
    ascending=False, method='max')
raw_data["tokens_per_section_rank"] = raw_data["tokens_per_section"].rank(
    ascending=False, method='max')

raw_data = raw_data.drop(columns=["nodes",
                                  "entropy_word",
                                  "net_flow",
                                  "flesch",
                                  "net_flow_per_section",
                                  "tokens_per_section"])

raw_data["normalised_composite"] = (
    raw_data["flesch_rank"] + raw_data["net_flow_per_section_rank"] + raw_data["tokens_per_section_rank"]) / 3
raw_data["unnormalised_composite"] = (
    raw_data["nodes_rank"] + raw_data["entropy_word_rank"] + raw_data["net_flow_rank"]) / 3
    
raw_data["normalised_rank"] = raw_data['normalised_composite'].rank(
    method='min', ascending=True)
raw_data["unnormalised_rank"] = raw_data['unnormalised_composite'].rank(
    method='min', ascending=True)

raw_data["combined_composite"] = (
    raw_data["normalised_rank"] + raw_data["unnormalised_rank"]) / 2
raw_data["combined_rank"] = raw_data['combined_composite'].rank(
    method='min', ascending=True)

raw_data.astype({
    "nodes_rank": 'int32',
    "entropy_word_rank": 'int32',
    "net_flow_rank": 'int32',
    "flesch_rank": 'int32',
    "net_flow_per_section_rank": 'int32',
    "tokens_per_section_rank": 'int32',
})


""" The row values of column named "id" will be the column names of the new table """
raw_data.sort_values(by="combined_rank", axis=0,
                     ignore_index=True, inplace=True)
raw_data = raw_data.set_index("id")
raw_data = raw_data.transpose()

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
    table.style.format(precision=1, escape="latex").format_index(escape="latex", axis=0).to_latex(
        results_path + "raw_rank" + str(i) + ".tex", hrules=True, clines="all;data")
    i += 1