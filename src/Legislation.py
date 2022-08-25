import datetime
import os
import xml.etree.ElementTree as ET
import re
import numpy as np
import networkx as nx
import pandas as pd
from scipy.stats import entropy
import variables as var
import calculations as calc
from Legal_node import Legal_node

"""Class which represents a piece of legislation"""


class Legislation:
    """ Uses the format... and is the ID used by the government to identify the legislation """
    id: str

    """ Base path of the folder of the legislation. """
    base_folder_path: str

    """ Label-id of the legislation, id of the label (title) of the legislation. The label-id is used for the citations"""
    label_id: int

    """ Full title of the legislation. """
    title: str

    """ Path to the manifest file."""
    manifest_file_path: str

    """ path to the wti (legislation technical information) file. """
    wti_file_path: str

    """ # Path to the latest revision of the legislation. """
    latest_version_path = str

    """ When the legislation was created. """
    created_at: datetime.date

    """ When the legislation was updated last. """
    updated_at: datetime.date

    """ When the legislation was revoked. """
    deleted_at: datetime.date

    """ Whether the legislation is revoked. """
    deleted: bool

    """ List of revision dates of the legislation. """
    revision_dates: list[datetime.date]

    """ First responsible of the legislation. """
    first_responsible: str

    """ Domains of the government government related to the legislation. """
    government_domains: list[str]

    """ The type of the legislation it represents. """
    type: str

    """ Legal areas the legislation is related to. """
    legal_areas: list[str]

    """ The root Legal_node object of the legislation. """
    root_legal_node: Legal_node

    citation_edges: list

    """ A hierarchical graph representation of the legislation. """
    hierarchical_graph: object

    """ A citation graph representation of the legislation. """
    citation_graph: object

    """ Avarage node depth of the hierarchical graph. """
    avarage_depth = 0

    nodes = list

    """ Avarage leaf depth of the hierarchical graph. """
    avarage_leaf_depth = 0

    """ Avarage syllable length of the words of the legislation. """
    avarage_syllables_per_word = 0

    """ Amount of refs with unkown doc"""
    amount_of_unknown_refs = 0

    amount_empty_doc_refs = 0

    num_tokens = 0

    avg_sentence_length = 0
    num_sentences = 0
    num_words = 0

    num_citations_internal = 0
    num_citations_out = 0
    num_citations_in = 0

    bijlage_refs = 0

    def __init__(self, id, base_path="/data"):
        """ Set default values. """
        self.citation_edges = []
        self.nodes = []
        self.id = id
        self.deleted = False

        """ Get all paths to the files of the legislation. """
        self.base_folder_path = os.path.join(base_path, self.id)
        self.manifest_file_path = os.path.join(
            self.base_folder_path, "manifest.xml")
        self.wti_file_path = os.path.join(
            self.base_folder_path, self.id + ".wti")
        self.revision_dates = self.fetch_revision_dates()

        """ Process the wti file, contains information used to determine further processing. """
        self.process_wti_file()

        """ Start the real work """
        if self.is_type_wet():
            self.process_legislation()

    def process_legislation(self):
        self.hierarchical_graph = nx.DiGraph()
        self.citation_graph = nx.DiGraph()

        self.process_manifest_file()

        if self.deleted is True:
            return

        """ Must be after processing the manifest file because it needs the latest date from the file """
        if self.latest_version_path is None:
            # print("No latest version found of legislation with id: " + self.id)
            return

        """ Verify and correct the latest version date to ensure we process the latest version of the legislation """
        self.verify_and_correct_latest_version_date()

        if self.is_wijzigingswet():
            return

        """ Process the latest version of the legislation """
        self.process_latest_version()

    def process_latest_version(self):
        tree = ET.parse(self.fetch_latest_version_file(),
                        ET.XMLParser(encoding="utf-8"))
        root = tree.getroot().find("wetgeving").find("wet-besluit")

        # Check if a wettekst child can be found
        if root.find("wettekst") is None:
            raise Exception("No wettekst found in legislation contents file")

        self.label_id = tree.getroot().find(
            "wetgeving").attrib.get("label-id")

        """ Wettekst is the root xml node containing the contents of the wet legislation """
        wettekst = root.find("wettekst")

        """ Create a root node for the legislation """
        legal_node = Legal_node(self.label_id, self.type, self.title)
        self.root_legal_node = legal_node

        """
        Add the root node to the graph/node list
        """
        self.nodes.append(legal_node)
        self.hierarchical_graph.add_node(
            legal_node.id, group=self.id, color='lime')

        """
        Recursively add the nodes and edges to the graph by looping through the xml tree
        """
        self.recursive_node_edge_creation(wettekst, legal_node)

        """
        Calculate relevant statistics
        """
        self.calculate_statistics()

    """ Loop recessively through the children of xml_node create of each child a node and add it to the list of nodes called nodes and make a connection between the node and the parent node by creating an edge between the parent and the node called edge """

    def recursive_node_edge_creation(self, xml_node, parent_node):

        # Loop through all the children of xml_node
        for child in xml_node:
            node_of_child = None
            tag = child.tag.lower()
            edge_type = "h"

            if tag not in var.structure_list or (tag == "boek" and self.id in var.bw_id_list):
                self.recursive_node_edge_creation(
                    child, node_of_child if node_of_child is not None else parent_node)
                continue

            """ Check if the child has an attribute 'status' and if so, check if it is 'vervallen' """
            if child.attrib.get("status") is not None and (child.attrib.get("status") == "vervallen" or child.attrib.get("status") == "nogniet"):
                continue

            if tag == "intref" or tag == "extref" or tag == "extioref" or tag == "intioref":
                edge_type = "c"

            if tag == "intref" or tag == "intioref":
                try:
                    if child.attrib.get("doc") == "":
                        self.amount_empty_doc_refs += 1
                        self.recursive_node_edge_creation(
                            child, node_of_child if node_of_child is not None else parent_node)
                        continue

                    legislation_id = child.attrib.get("bwb-id")
                    bwb_ng_variabel_deel = child.attrib.get(
                        "bwb-ng-variabel-deel") if child.attrib.get(
                        "bwb-ng-variabel-deel") else ''
                    id = legislation_id + bwb_ng_variabel_deel
                    
                    if "bijlage" in id.lower():
                        self.bijlage_refs += 1
                        self.recursive_node_edge_creation(
                            child, node_of_child if node_of_child is not None else parent_node)
                        continue
                    
                    id = child.attrib.get("label-id")
                    
                    if "," in id:
                        id = id.split(",")
                        for i in id:
                            self.citation_edges.append(
                                (parent_node.id, i, {'color': 'red'}))
                            self.citation_graph.add_edge(
                                parent_node.id, i, type=edge_type, color='red', group=self.id, ref="int")
                    else:
                        self.citation_edges.append(
                            (parent_node.id, id, {'color': 'red'}))
                        self.citation_graph.add_edge(
                            parent_node.id, id, type=edge_type, color='red', group=self.id, ref="int")
                        
                    self.num_citations_internal += 1
                    
                except Exception as e:
                    print("Could not add edge between: " +
                          parent_node.id + " and " + id)
                    
                self.recursive_node_edge_creation(
                    child, node_of_child if node_of_child is not None else parent_node)
                
                continue

            if tag == "extref" or tag == "extioref":
                try:
                    """ Check if the child has an attribute reeks and if so, check if it is 'Celex' which means EU legislation """
                    if child.attrib.get("doc") == "onbekend":
                        self.amount_of_unknown_refs += 1
                        self.recursive_node_edge_creation(
                            child, node_of_child if node_of_child is not None else parent_node)
                        continue

                    if child.attrib.get("bwb-id") is not None:
                        id = self.jci_string_to_node_id(
                            child.attrib.get("doc"))

                    if "bijlage" in child.attrib.get("doc"):
                        self.bijlage_refs += 1
                        self.recursive_node_edge_creation(
                            child, node_of_child if node_of_child is not None else parent_node)
                        continue

                    """ Append a string of all attributes of child to a file called cits.txt """
                    if child.attrib.get("reeks") is not None and child.attrib.get("reeks") == "Celex":
                        id = child.attrib.get("doc")
                        self.citation_graph.add_node(
                            id, color='gray', group="Celex", ref="ext")
                    else:
                        if "Onderdeel" not in id and "Deel" not in id:
                            id = child.attrib.get("label-id")
                    if "," in id:
                        id = id.split(",")
                        for i in id:
                            self.citation_edges.append(
                                (parent_node.id, i, {'color': 'red'}))
                            self.citation_graph.add_edge(
                                parent_node.id, i, type=edge_type, color='red', group='cout', ref="ext", targetbwb=child.attrib.get("bwb-id") if child.attrib.get("bwb-id") is not None else "no-bwb-id")
                    else:
                        self.citation_edges.append(
                            (parent_node.id, id, {'color': 'red'}))
                        self.citation_graph.add_edge(
                            parent_node.id, id, type=edge_type, color='red', group='cout', ref="ext", targetbwb=child.attrib.get("bwb-id") if child.attrib.get("bwb-id") is not None else "no-bwb-id")
                    self.num_citations_out += 1
                    
                except Exception as e:
                    print("Could not add edge between: " +
                          parent_node.id + " and " + id)
                self.recursive_node_edge_creation(
                    child, node_of_child if node_of_child is not None else parent_node)
                continue

            text = None

            id = self.id + child.attrib.get("bwb-ng-variabel-deel")

            label = child.attrib.get("label") if child.attrib.get(
                "label") is not None else child.attrib.get("bwb-ng-variabel-deel").split("/")[-1]

            """ Fetch the texts of the item types that contain text """
            if tag == "artikel" or tag == "lid" or tag == "li":
                """ Check if the tag has al elements """
                if child.find("al") is not None:
                    """ Get all the <al> tags and get the text of all the <al> tags and add it to a text variable """
                    text = list()
                    for aL in child.findall("al"):
                        if aL.text is not None:
                            """ Get the text of the aL tag including the text of all the children tags between the aL tag text and get the tail of all the tags if present"""
                            text.append("".join(aL.itertext()))

            if "Onderdeel" not in id:
                id = child.attrib.get(
                    "label-id") if child.attrib.get("label-id") is not None else id

            """ Create a legal node object """
            node_of_child = Legal_node(
                id, tag, label, text if text is not None else None)

            """ Add the node to the list of nodes """
            self.nodes.append(node_of_child)

            """ Add the node to the graph """
            self.hierarchical_graph.add_node(
                node_of_child.id, color='blue', group=self.id)

            """ Add the edge to the graph """
            self.hierarchical_graph.add_edge(
                parent_node, node_of_child, type=edge_type, color='black', group=self.id)

            """ If node_of_child is None use parent_node as the node_of_child """
            self.recursive_node_edge_creation(
                child, node_of_child if node_of_child is not None else parent_node)

        return self

    def calculate_statistics(self):
        """ Calculate the amount of legal_nodes which have a text """
        self.text_nodes = 0
        self.nontext_nodes = 0
        self.above_section_nodes = 0
        self.section_nodes = 0
        self.below_section_nodes = 0
        syl_lengths = []

        """ Calculate statistics by combining the data of all the text nodes """
        self.wordsLemmaWithStopwords = list()
        self.wordsLemmaWithoutStopwords = list()
        self.wordsWithStopwords = list()
        self.wordsWithoutStopwords = list()
        self.avgSentenceLength = list()
        self.avgWordLength = list()
        self.num_tokens = 0

        """ Start loop """
        for node in self.nodes:
            if node.type in var.above_section:
                self.above_section_nodes += 1

            if node.type in var.section:
                self.section_nodes += 1

            if node.type in var.below_section:
                self.below_section_nodes += 1

            if node.is_text_node():
                self.text_nodes += 1
                self.num_sentences += node.num_sentences
                self.wordsLemmaWithStopwords.extend(
                    node.word_list_with_lemma_with_stopwords)
                self.wordsLemmaWithoutStopwords.extend(
                    node.word_list_with_lemma_without_stopwords)
                self.wordsWithStopwords.extend(node.word_list)
                self.wordsWithoutStopwords.extend(
                    node.word_list_without_stopwords)
                self.num_tokens += node.num_tokens
                syl_lengths.append(node.avg_syllable_length)

                if node.avg_sentence_length is not None and node.avg_sentence_length != 0:
                    self.avgSentenceLength.append(node.avg_sentence_length)

                if node.avg_word_length is not None and node.avg_word_length != 0:
                    self.avgWordLength.append(node.avg_word_length)
            else:
                self.nontext_nodes += 1

        """ End loop """

        self.avarage_syllables_per_word = sum(
            syl_lengths) / len(syl_lengths)

        """ Calculate the number of nodes and edges in the graph """
        self.number_of_nodes = calc.calculate_number_of_nodes(
            self.hierarchical_graph)
        self.number_of_edges = calc.calculate_number_of_edges(
            self.hierarchical_graph)

        """ Calculate the number of nodes and edges in the graph of each type from the structure_list """
        # self.number_of_nodes_by_type = calc.calculate_number_of_nodes_per_type(
        #     self.hierarchical_graph)

        """ Calculate the avarage of the shortest paths from the root node to each node"""
        self.avarage_depth = calc.calculate_avg_node_depth(
            self.hierarchical_graph, self.root_legal_node)

        """ Calculate the avarage leaf depth of the graph """
        self.avarage_leaf_depth = calc.calculate_avg_leaf_depth(
            self.hierarchical_graph, self.root_legal_node)

        self.avgWordLength = sum(
            self.avgWordLength) / len(self.avgWordLength) if len(self.avgWordLength) > 0 else 0
        self.avgSentenceLength = sum(self.avgSentenceLength) / len(
            self.avgSentenceLength) if len(self.avgSentenceLength) > 0 else 0
        self.entropyLemmaWithStopwords = entropy(
            pd.Series(self.wordsLemmaWithStopwords).value_counts())
        self.entropyLemmaWithoutStopwords = entropy(
            pd.Series(self.wordsLemmaWithoutStopwords).value_counts())
        self.entropyWithStopwords = entropy(
            pd.Series(self.wordsWithStopwords).value_counts())
        self.entropyWithoutStopwords = entropy(
            pd.Series(self.wordsWithoutStopwords).value_counts())

        nun_citations = 0
        num_int_citations = 0
        num_ext_citations = 0

        for edge in self.citation_graph.edges(data=True):
            """ Keep track of the amount of citations"""
            nun_citations += 1
            ref = edge[2]['ref']
            """ Keep track of the amount of internal citations"""
            if ref == "int":
                num_int_citations += 1
            """ Keep track of the amount of external citations"""
            if ref == "ext":
                num_ext_citations += 1

    def verify_and_correct_latest_version_date(self):
        latest_version_date = datetime.datetime.strptime(
            self.latest_version_path.split("_", 1)[0], "%Y-%m-%d").date()

        """ Loop through all the revisions and fetch the date most in the future """
        if self.revision_dates[-1] > latest_version_date:
            # print("Found new version of legislation: " + self.id)
            # print("Old 'latest' version: " + self.latest_version_path)
            i = 0
            latest_date = datetime.datetime(1500, 1, 1).date()
            """" Scan the names of the folders in the base_folder_path and find the folder with the most recent date in the name and set the latest_version_path to that folder """
            for folder in os.listdir(self.base_folder_path):
                try:
                    folder_date = datetime.datetime.strptime(
                        folder.split("_", 1)[0], "%Y-%m-%d").date()
                    if folder_date > latest_version_date:
                        i += 1
                        if folder_date > latest_date:
                            latest_date = folder_date
                            self.latest_version_path = folder
                except ValueError:
                    pass

            self.latest_version_path = self.latest_version_path + \
                "/xml/" + self.id + "_" + self.latest_version_path + ".xml"
            # print("Amount of new versions: " + str(i))
            # print("Newewst version: " + self.latest_version_path)

    """
    Excludes BES legislation, even though those are also wetten.
    """

    def is_type_wet(self):
        return self.type == "wet" or self.type == "rijkswet" or self.type.startswith("wet-")

    """ Fetch latest version of the legislation based on the latest_version_path """
    def fetch_latest_version_file(self):
        try:
            return os.path.join(self.base_folder_path, self.latest_version_path)
        except:
            # print("No latest version found of legislation with id: " + self.id)
            raise Exception("Has no content")

    """ revision_dates is a list of all the revision dates of the legislation based on all the folders in base_folder_path where the name of the folder is a date """
    def fetch_revision_dates(self):
        folders = os.listdir(self.base_folder_path)
        dates = []
        for folder in folders:
            try:
                dates.append(datetime.datetime.strptime(
                    folder.split("_", 1)[0], "%Y-%m-%d").date())
            except ValueError:
                pass
        return dates

    """
    Open the manifest_file xml file and retrieve the metadata of the legislation.
    Retrieves: latest revision as provided by the dataset (sometimes inaccurate), date of deletion/resigned
    """

    def process_manifest_file(self):
        tree = ET.parse(self.manifest_file_path)
        root = tree.getroot()

        """ From root, check if there is an attribute _latestItem and if so, set the latest_version_path to the value of that attribute """
        if root.attrib.get("_latestItem") is not None:
            self.latest_version_path = root.attrib.get("_latestItem")
        else:
            self.latest_version_path = None

        """ Check if first child of root is called metadata and if not so throw an error """
        if root.find("metadata") is None:
            raise Exception("No metadata found in manifest file")

        metadata = root.find("metadata")

        if metadata.find("datum_intrekking") is not None:
            self.deleted = True
            self.deleted_at = datetime.datetime.strptime(
                metadata.find("datum_intrekking").text, "%Y-%m-%d").date()
        else:
            self.deleted = False
            self.deleted_at = None

        return self

    """
    Process the wti file and retrieve the metadata
    Retrieves: legislation type, first responsible, title and legal areas.
    """

    def process_wti_file(self):
        tree = ET.parse(self.wti_file_path)
        root = tree.getroot()

        """ Check if first child of root is called algemene-informatie and if not so throw an error """
        if root.find("algemene-informatie") is None:
            raise Exception("No metadata found in manifest file")

        info = root.find("algemene-informatie")

        """ Get the type from the first child of info and convert it to an enumerate type (Wet, AMvB, etc) """
        self.type = info.find("soort-regeling").text

        """ Get the first_responsible from the first child of info """
        self.first_responsible = info.find("eerstverantwoordelijke").text

        """ Get the title from the first child of info """
        self.title = info.find("citeertitel").text

        """ Get the legal_areas by getting the first rechtsgebieden child of info and then getting all the children of that child and then getting the text of each child of that child """
        self.legal_areas = [child.find("hoofdgebied").text for child in info.find(
            "rechtsgebieden").findall("rechtsgebied")]

        return self

    def jci_string_to_node_id(self, jci_string):
        """ Use a regex to extract legislation id from the jci string """
        id = re.findall(r"c\:(.*)[\&.*]?", jci_string, flags=re.U)[0]

        """ Remove an '&' from the id if it exists """
        if "&" in id:
            id = id.split("&")[0]

        """ Split the string by &amp; and '&' for each item get the name of the parameter and the value of the parameter """
        bwb_ng_variabel_deel = jci_string.split("&")
        """ Remove the first item from the list because it contains the jci string and bwb id """
        bwb_ng_variabel_deel = bwb_ng_variabel_deel[1:]
        """ Create a dictionary with the name of the parameter as key and the value of the parameter as value """
        bwb_ng_variabel_deel = {item.split("=")[0]: item.split(
            "=")[1] for item in bwb_ng_variabel_deel}
        """ Replace the keys with the values of jci_parameters_to_structures """
        bwb_ng_variabel_deel = {
            var.jci_parameters_to_structures[key]: value for key, value in bwb_ng_variabel_deel.items()}
        """ Concate the keys and values of bwb_ng_variabel_deel to a string with a slash as seperate for each item with a leading slash """
        bwb_ng_variabel_deel = "/" + "/".join(
            [key + "" + value for key, value in bwb_ng_variabel_deel.items()])

        if bwb_ng_variabel_deel == "/":
            bwb_ng_variabel_deel = ""

        return id + bwb_ng_variabel_deel

    def is_wijzigingswet(self):
        """ Check if the title contains the word 'wijzigingswet' """
        if "wijzigingswet" in self.title.lower() \
                or "wijziging" in self.title.lower() \
                or "verzamelwet" in self.title.lower() \
                or "wijzigt" in self.title.lower() \
                or "samenvoeging" in self.title.lower():
            return True
        subtitle = ET.parse(self.fetch_latest_version_file(),
                            ET.XMLParser(encoding="utf-8")).getroot() \
            .find("wetgeving") \
            .find("intitule").text

        if "wijzigingswet" in subtitle.lower() \
                or "wijziging" in subtitle.lower() \
                or "verzamelwet" in subtitle.lower() \
                or "wijzigt" in subtitle.lower() \
                or "samenvoeging" in subtitle.lower():
            return True
        return False

    """ Function which returns all statistical variables in dict format """

    def stat_to_dict(self):

        log10_nodes = np.log10(len(self.nodes))
        log10_section_nodes = np.log10(self.section_nodes)

        return {
            "id": self.id,
            "title": self.title,
            "legal_areas": ";".join(self.legal_areas),
            "revisions": len(self.revision_dates),
            "nodes": len(self.nodes),
            "log_nodes": log10_nodes,
            "log_section_nodes": log10_section_nodes,
            "text_nodes": self.text_nodes,
            "nontext_nodes": self.nontext_nodes,
            "above_section_nodes": self.above_section_nodes,
            "below_section_nodes": self.below_section_nodes,
            "section_nodes": self.section_nodes,
            "mean_depth": self.avarage_depth,
            "mean_leaf_depth": self.avarage_leaf_depth,
            "tokens": self.num_tokens,
            "tokens_per_section": self.num_tokens / self.section_nodes,
            "tokens_per_text_node": self.num_tokens / self.text_nodes,
            "entropy_lemma": self.entropyLemmaWithoutStopwords,
            "entropy_word": self.entropyWithoutStopwords,
            "num_words": len(self.wordsWithStopwords),
            "num_sentences": self.num_sentences,
            "avg_sentence_length": self.avgSentenceLength,
            "avg_syllables_per_word": self.avarage_syllables_per_word,
            "avg_word_length": self.avgWordLength,
            "citations": len(self.citation_edges),
            "citations_internal": self.num_citations_internal,
            "citations_out": self.num_citations_out,
            "citations_in": self.num_citations_in,
            "citations_external": self.num_citations_in + self.num_citations_out,
            "net_flow": self.num_citations_out - self.num_citations_in,
            "net_flow_per_section": (self.num_citations_out - self.num_citations_in) / self.section_nodes,
            "flesch": calc.calculate_readability_score(self.avgSentenceLength, self.avarage_syllables_per_word),
            "unkown_doc": self.amount_of_unknown_refs,
            "empty_doc": self.amount_empty_doc_refs,
            "bijlage_cits": self.bijlage_refs,
            "bad_doc": self.amount_of_unknown_refs + self.amount_empty_doc_refs,
        }
