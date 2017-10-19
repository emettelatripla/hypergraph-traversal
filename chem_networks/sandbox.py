import logging
import sys
from time import time
import random
import graphviz as gv

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only, print_node, print_hyperedge
from halp.utilities.directed_statistics import *

from xml.dom.minidom import parse
import xml.dom.minidom

from opsupport_bpm.aco.aco_misc import generate_random_node_attributes
from opsupport_bpm.aco.aco_directed_hypergraph import aco_algorithm_norec
from opsupport_bpm.util.print_hypergraph import write_hg_to_file
from chem_networks.graphviz_sandbox import test_hypergraph


# setup the logger
log = logging.getLogger ('')
log.setLevel (logging.INFO)
format = logging.Formatter ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# LOG ON STDOUT
# ch = logging.StreamHandler (sys.stdout)
# ch.setFormatter (format)
# log.addHandler (ch)

# LOG ON A FILE
logging.basicConfig(filename='log.log',level=logging.INFO)

logger = logging.getLogger (__name__)


file_name = "/home/mcomuzzi/opsupport_bpm_files/chem_networks/Ec_iAF1260_flux1.txt"

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
   dummy_node_label = "REAC_" + str(id) + "_" + str(dummy_counter)
   dummy_node = []
   dummy_node.append(dummy_node_label)
   dummy_counter += 1
   hg.add_hyperedge(reactants_list, dummy_node, {'reac_id' : id, 'rev' : rev, 'phero' : 0})
   dummy_counter += 1
   hg.add_hyperedge(dummy_node, product_list, {'reac_id' : id, 'rev' : rev, 'phero' : 0})

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
    hg.add_node(node,generate_random_node_attributes() )

# generate source and sink nodes
SOURCE_FOUND = False
while not SOURCE_FOUND:
    source_name = random.sample(hg.get_node_set(), 1)[0]
    if not source_name.startswith("REAC"):
        SOURCE_FOUND = True

logger.info("Chosen SOURCE node: {0}".format(source_name))
source_attrs = generate_random_node_attributes()
source_attrs['source'] = True
hg.add_node(source_name, source_attrs)

SINK_FOUND = False
while not SINK_FOUND:
    sink_name = random.sample(hg.get_node_set(), 1)[0]
    if not sink_name.startswith('REAC'):
        SINK_FOUND = True

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

# """
# RENDER HG WITH GRAPHVIZ
# """
# print("rendering with graphviz...")
# test_hypergraph(hg)
# print("...done")

"""
TEST ACO
"""

start_time_aco = time()
print("running aco....")
# aco_result = aco_algorithm_norec(hg, ANT_NUM, COL_NUM, tau, W_UTILITY, SYS_TYPE, SEARCH_TYPE, IGNORE_PHERO = False)
aco_result = aco_algorithm_norec(hg, 10 , 6, 0.75, {'cost' : 0.7, 'avail' : 0.1, 'qual' : 0.1, 'time' : 0.1},
                                 'ACS', 'B+F', IGNORE_PHERO = False)
p_opt = aco_result[0]
utility = aco_result[1]
end_time_aco = time()
aco_alg_time = end_time_aco - start_time_aco
print_hg_std_out_only(p_opt)
write_hg_to_file (p_opt, "opt.hgr")
print("ACO optimisation took: {0}s".format(aco_alg_time))
print("UTILITY: {0}".format(utility))

