'''
Created on Aug 2, 2016

Main test for aco

@author: UNIST
'''

import logging
import sys
from time import time

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.aco.aco_directed_hypergraph import aco_algorithm_norec
from opsupport_bpm.aco.aco_misc import random_init_attributes
from opsupport_bpm.models.hypergraph import tau_post_processing
from opsupport_bpm.models.hypergraph_to_pnml import reduce_opt_path_pnet
from opsupport_bpm.models.hypergraph_to_pnml import show_opt_path_pnet
from opsupport_bpm.models.pnml_to_hypergraph import convert_pnet_to_hypergraph
import xml.etree.ElementTree as ET


def main():
    # setup working directory and root file
    working_dir = "C://opsupport_bpm_files"
    input_dir = working_dir+"/pnml_input"
    
    # files for testing ====================================================
    #file_root = "ex1_inductive"
    #file_root = "bpi_challenge2012"
    #file_root = "road_fine_process"
    file_root = "hospital_inductive"
    #file_root = "repair_start_end_inductive"
    
    #file_type = "inductive"
    io_subdir = "/real_logs"
    
    #MINED WITH ALPHA MINER
    #file_root = "ex6_claim_alpha"
    #file_type = "alpha"
    
    #pnml_file = "C://BPMNexamples/"+file_type+"/"+file_root+".pnml"
    pnml_file = input_dir+io_subdir+"/"+file_root+".pnml"
    
    # output directory
    output_dir = working_dir+"/output_single"
    
    #setup the logger =====================================================
    log_file = working_dir+"/aco.log"
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # increase recursion limit (if needed)
    # print(str(sys.getrecursionlimit()))
    # sys.setrecursionlimit(100000000)
    # print(str(sys.getrecursionlimit()))
    
    
    # ========================= A BUNCH OF FILES FOR TESTING =============================
    #pnml_file = "C://BPMNexamples/inductive/ex1_inductive.pnml"
    #pnml_file = "C://BPMNexamples/inductive/ex4_inductive.pnml"
    #pnml_file = "C://BPMNexamples/real_logs/hospital_inductive.pnml"
    #pnml_file = "C://BPMNexamples/inductive/repair_start_end_inductive.pnml"
    #pnml_file = "C://BPMNexamples/inductive/ex6_claim_inductive.pnml"
    #The following has loop:
    #pnml_file = "C://BPMNexamples/inductive/ex5_review_inductive.pnml"
    #pnml_file = "C://BPMNexamples/alpha/ex1_alpha.pnml"
    
    #===========================================================
    # =========================================================================================
    
    
    
    
    # ===================================================================================================
    #===========================================================
    #===========================================================
    #===========================================================
    
    # START: read the pnml file....
    tree = ET.parse(pnml_file)
    pnet = tree.getroot()
    
    hg = DirectedHypergraph()
    
    # STEP 1: convert pnet into hypergraph + tau post processing
    start_time_conv = time()
    hg = convert_pnet_to_hypergraph(pnet)
    end_time_conv = time()
    print("Conversion Petri net to hypergraph took: {0}".format(end_time_conv - start_time_conv))
    
    start_time_post = time()
    hg = tau_post_processing(hg)
    end_time_post = time()
    print("Tau post processing on hypergraph took: {0}".format(end_time_post - start_time_post))
    #STEP 2: randomly initialise hypergraph's nodes utility values
    hg = random_init_attributes(hg)
    #print_hg(hg,'hyp.txt')
    
    #find start node (MAKE A FUNCTION FOR IT!!!!)
    """ INITIALISATION FOR RECURSIVE VERSION
    nodes = hg.get_node_set()
    start_nodes = []
    for node in nodes:
        if hg.get_node_attribute(node, 'source') == True:
            logger.debug("  ")
            logger.debug("$$$$$ Begin optimisation....$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logger.debug("Found start node: {0}".format(print_node(node, hg)))
            logger.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            start_nodes.append(node)
    END """
    
    #===========================================================
    # ==================== INITIALISATION NON RECURSIVE VERSION ===========================================
    #===========================================================
    logger.debug("*"*50)
    logger.info("*"*50)
    logger.info("*** BEGIN ACO OPTIMISATION.... ***")
    logger.info("*"*50)
    logger.debug("*"*50)

    # Set ACO parameters
    tau = 0.6
    ANT_NUM = 10
    COL_NUM = 3
    W_UTILITY = {'cost' : 1.0, 'avail' : 0.0, 'qual' : 0.0, 'time' : 0.0}
    
    #===========================================================
    # =====================  call ACO algorithm (NON RECURSIVE)
    #===========================================================
    #p_opt = aco_algorithm(start_nodes, hg, ANT_NUM, COL_NUM, tau, W_UTILITY)
    start_time_aco = time()
    p_opt = aco_algorithm_norec(hg, ANT_NUM, COL_NUM, tau, W_UTILITY)
    end_time_aco = time()
    print("AcCO optimisation took: {0}".format(end_time_aco - start_time_aco))
    
    # =================  highlight optimal path on pnet
    start_time_opt = time()
    show_opt_path_pnet(p_opt, tree, file_root, output_dir)
    
    # ================= reduce pnet to show only the optimal path
    reduce_opt_path_pnet(tree, file_root, output_dir)
    end_time_opt = time()
    print("Post processing pnet (show optimal path on pnet) took: {0}".format(end_time_opt - start_time_opt))
    


if __name__ == "__main__":
    main()
