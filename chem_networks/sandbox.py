import logging
import sys
import xml.etree.ElementTree as ET
from lxml import etree

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only
from halp.utilities.directed_statistics import *

from xml.dom.minidom import parse
import xml.dom.minidom


# setup the logger
log = logging.getLogger ('')
log.setLevel (logging.INFO)
format = logging.Formatter ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler (sys.stdout)
ch.setFormatter (format)
log.addHandler (ch)

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
   hg.add_hyperedge(reactants_list, product_list, {'reac_id' : id, 'rev' : rev})

print_hg_std_out_only(hg)

print(number_of_hyperedges(hg))
print(number_of_nodes(hg))
print(mean_hyperedge_cardinality_ratio(hg))
print(mean_hyperedge_head_cardinality(hg))
print(mean_hyperedge_tail_cardinality(hg))
print(mean_indegree(hg))
print(mean_outdegree(hg))


# CREATE HYPERGRAPH

