import logging
import sys
from time import time
import random

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only, print_node, print_hyperedge
from halp.utilities.directed_statistics import *

from xml.dom.minidom import parse
import xml.dom.minidom

from opsupport_bpm.aco.aco_misc import generate_random_node_attributes
from opsupport_bpm.aco.aco_directed_hypergraph import aco_algorithm_norec
from opsupport_bpm.util.print_hypergraph import write_hg_to_file



class ChemNetAnalyser:

    def __init__(self, chem_net_filename, start_compound, end_compound):
        self._file_name = chem_net_filename
        self._start_compound = start_compound
        self.end_compound = end_compound
        self._net_hg = self._create_net_hg()
        self._opt_hg = None


    """ CREATE NETWORK HG AND FIN OPTIMAL PATH """

    def _create_net_hg(self):
        DOMTree = xml.dom.minidom.parse(file_name)
        sbml = DOMTree.documentElement
        if sbml.hasAttribute("id"):
            print("Root element : {0}".format(sbml.getAttribute("id")))

        def print_list_metabolites(list):
            for node in list:
                species = node.getElementsByTagName('speciesReference')
                for sp in species:
                    print(sp.getAttribute('species'))

        def get_list_metabolites(list):
            met_list = []
            for node in list:
                species = node.getElementsByTagName('speciesReference')
                for sp in species:
                    met_list.append(sp.getAttribute('species'))
            return met_list

        # Get all the movies in the collection
        reactions = sbml.getElementsByTagName("reaction")
        i = 0
        # Print detail of each movie.
        hg = DirectedHypergraph()

        dummy_counter = 0

        for reaction in reactions:
            print("*** REACTION {0} ***".format(i))
            i += 1
            id = reaction.getAttribute('id')
            rev = reaction.getAttribute('reversible')
            reactants = reaction.getElementsByTagName('listOfReactants')
            products = reaction.getElementsByTagName('listOfProducts')
            print("ID: {0}".format(id))
            print("Reversible? {0}".format(rev))
            reactants_list = get_list_metabolites(reactants)
            product_list = get_list_metabolites(products)
            print("\t--- REACTANTS ---")
            # print_list_metabolites(reactants)
            print(reactants_list)
            print("\t--- PRODUCTS ---")
            # print_list_metabolites(products)
            print(product_list)
            print("********************\n")
            dummy_node_label = "dummy" + str(dummy_counter)
            dummy_node = []
            dummy_node.append(dummy_node_label)
            dummy_counter += 1
            hg.add_hyperedge(reactants_list, dummy_node, {'reac_id': id, 'rev': rev, 'phero': 0})
            dummy_counter += 1
            hg.add_hyperedge(dummy_node, product_list, {'reac_id': id, 'rev': rev, 'phero': 0})

        # print_hg_std_out_only(hg)

        print(number_of_hyperedges(hg))
        print(number_of_nodes(hg))
        print(mean_hyperedge_cardinality_ratio(hg))
        print(mean_hyperedge_head_cardinality(hg))
        print(mean_hyperedge_tail_cardinality(hg))
        print(mean_indegree(hg))
        print(mean_outdegree(hg))

        """
        ADD RANDOM UTILITY INFORMATION
        """
        for node in hg.get_node_set():
            hg.add_node(node, generate_random_node_attributes())

        # generate source and sink nodes
        source_name = random.sample(hg.get_node_set(), 1)[0]
        logger.info("Chosen SOURCE node: {0}".format(source_name))
        source_attrs = generate_random_node_attributes()
        source_attrs['source'] = True
        hg.add_node(source_name, source_attrs)

        sink_name = random.sample(hg.get_node_set(), 1)[0]
        logger.info("Chosen SINK node: {0}".format(sink_name))
        sink_attrs = generate_random_node_attributes()
        sink_attrs['sink'] = True
        hg.add_node(sink_name, sink_attrs)

        print("\n\n RANDOM UTILITY INFO GENERATED\n")

        for node in hg.get_node_set():
            print_node(node, hg)
        for edge in hg.get_hyperedge_id_set():
            print_hyperedge(edge, hg)

        """
        DETERMINE XOR SPLITS
        """

        """
        WRITE HG TO FILE
        """
        write_hg_to_file(hg, "chem_net_hg.hgr")


    def create_random_utility_info(self):
        pass

    def find_optimal_path(self):
        pass

    """ **** METHODS TO PRINT NETWORK AND OPTIMAL PATH """

    def print_net_hg(self):
        if self._net_hg == None:
            print("Nothing to print here :(")
        else:
            pass

    def print_opt_hg(self):
        if self._net_hg == None:
            print("Nothing to print here :(")
        else:
            pass

    """ OTHER ANCILLARY METHODS """

    def list_compounds(self):
        pass

    def list_reactions(self):
        pass

    def show_reaction_details(self):
        pass




if __name__ == "__main__":
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # LOG ON STDOUT
    ch = logging.StreamHandler (sys.stdout)
    ch.setFormatter (format)
    log.addHandler (ch)

    # LOG ON A FILE
    # logging.basicConfig(filename='log.log', level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("Logger initialised")

    # Initialise Chem network analyser

