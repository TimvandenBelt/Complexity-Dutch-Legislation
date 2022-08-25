
structure_list = ("hoofdstuk", "artikel", "paragraaf", "lid",
                  "li", "boek", "afdeling", "titeldeel", "intref", "intioref", "extref", "extioref", "subparagraaf", "subsubparagraaf")

bw_id_list = ("BWBR0002656", "BWBR0003045", "BWBR0005291", "BWBR0002761", "BWBR0005288",
              "BWBR0005289", "BWBR0005290", "BWBR0006000", "BWBR0005034", "BWBR0030068")

above_section = ("hoofdstuk", "paragraaf",
                 "boek", "afdeling", "titeldeel", "subparagraaf", "subsubparagraaf")

section = ("artikel")

below_section = ("lid", "li")

debug = False

jci_parameters_to_structures = {
    "hoofdstuk": "Hoofdstuk",
    "artikel": "Artikel",
    "paragraaf": "Paragraaf",
    "lid": "Lid",
    "o": "Onderdeel",
    "boek": "Boek",
    "afdeling": "Afdeling",
    "titeldeel": "TitelDeel",
    "bijlage": "Bijlage",
    "sub-paragraaf": "SubParagraaf",
    "sub-sub-paragraaf": "SubSubParagraaf",
    "bijlage": "Bijlage",
    "deel": "Deel",
}

layout_engines = ["twopi", "circo", "multipartite_layout", "dot", "sfdp"]
rootless_engines = ["multipartite_layout", "neato", "sfdp"]

results_path = "../results/"

data_path = "../data/"
