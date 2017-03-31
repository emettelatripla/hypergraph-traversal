'''
Created on 2016. 8. 4.

Facility to evaluate the aco algorithm extensively, keeping track of execution times

@author: UNIST
'''

import os
import xml.etree.ElementTree as ET
import logging

from halp.directed_hypergraph import DirectedHypergraph
from time import time

from opsupport_bpm.aco.aco_directed_hypergraph import aco_algorithm_norec
from opsupport_bpm.aco.aco_misc import random_init_attributes
from opsupport_bpm.models.hypergraph import tau_post_processing, reset_pheromone
from opsupport_bpm.models.hypergraph_to_pnml import reduce_opt_path_pnet
from opsupport_bpm.models.hypergraph_to_pnml import show_opt_path_pnet
from opsupport_bpm.models.pnml_to_hypergraph import convert_pnet_to_hypergraph
from opsupport_bpm.models.pnml_to_hypergraph import convert_to_hg_and_rw_pnml
from opsupport_bpm.models.hypergraph import get_statistics
from opsupport_bpm.util.print_hypergraph import read_hg_from_file,\
    write_hg_to_file, print_hg_std_out_only


def get_pnml_tree(input_eval_dir, file_root):
    pnml_file = input_eval_dir+"/"+file_root+".pnml" 
    tree = ET.parse(pnml_file)
    return tree

def setup_conversion_pnet_to_hg(file_root, input_eval_dir, output_eval_dir):
    '''

    :param file_root:
    :param input_eval_dir
    :param output_eval_dir:
    '''
    
    # extract root of pnml file: onet
    #pnet = get_pnml_tree(input_eval_dir, file_root).getroot()
    file_name = input_eval_dir + "/" + file_root + ".pnml"
    
    # setup logger
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.DEBUG)
    
    
    hg = DirectedHypergraph()
    
    # STEP 1: convert pnet into hypergraph + tau post processing
    start_time_conv = time()

    hg = convert_to_hg_and_rw_pnml(file_name)

    end_time_conv = time()
    conv_pnet_to_hg_time = end_time_conv - start_time_conv
    print("{1}: Conversion Petri net to hypergraph took: {0}s".format(conv_pnet_to_hg_time, file_root))
    
    start_time_post = time()
    hg = tau_post_processing(hg)
    end_time_post = time()
    tau_post_time = end_time_post - start_time_post
    print("{1}: Tau post processing on hypergraph took: {0}".format(tau_post_time, file_root))
    #STEP 2: randomly initialise hypergraph's nodes utility values
    hg = random_init_attributes(hg)
    # TBC TBC TBC: PERSIST hg ON FILE
    print("{0}: Hypergraph utility randomly initialised".format("file_root"))
    
    return (hg, conv_pnet_to_hg_time, tau_post_time)
    
    
    
def sim_run_pnml_files(hg, COL_NUM, ANT_NUM, phero_tau, W_UTILITY, file_root, input_eval_dir, output_eval_dir, SYS_TYPE):
    '''
    
    :param hg:
    :param COL_NUM:
    :param ANT_NUM:
    :param phero_tau:
    :param W_UTILITY
    :param file_root:
    :param input_eval_dir:
    :param output_eval_dir:
    '''
    
    tree = get_pnml_tree(input_eval_dir, file_root)
    
    # set up logger
    #TO-DO: change logger if possible
    
    
    start_time_aco = time()
    aco_result = aco_algorithm_norec(hg, ANT_NUM, COL_NUM, phero_tau, W_UTILITY, SYS_TYPE)
    p_opt = aco_result[0]
    utility = aco_result[1]
    end_time_aco = time()
    aco_alg_time = end_time_aco - start_time_aco
    print("{1}: ACO optimisation took: {0}s".format(aco_alg_time, file_root))
    
    output_dir_pnml = output_eval_dir+"/pnml"
    
    file_root_ext = file_root+"_"+str(COL_NUM)+"_"+str(ANT_NUM)+"_"+str(phero_tau)
    
    # =================  highlight optimal path on pnet
    start_time_opt = time()
    show_opt_path_pnet(p_opt, tree, file_root_ext, output_dir_pnml)
    
    # ================= reduce pnet to show only the optimal path
    reduce_opt_path_pnet(tree, file_root_ext, output_dir_pnml)
    end_time_opt = time()
    pnet_post_time = end_time_opt - start_time_opt
    print("{1}: Post processing pnet (show optimal path on pnet) took: {0}".format(pnet_post_time, file_root))
    
    return (aco_alg_time, pnet_post_time, utility)

def cleanup(output_eval_dir):
    print("Doing some cleanup before starting....")
    # logs
    filelist = [ f for f in os.listdir(output_eval_dir + "/logs")]
    for f in filelist:
        file_name = output_eval_dir + "/logs/" + f
        os.remove(file_name)
    # peformance
    filelist = [ f for f in os.listdir(output_eval_dir + "/performance")]
    for f in filelist:
        file_name = output_eval_dir + "/performance/" + f
        os.remove(file_name)
    # pnml
    filelist = [ f for f in os.listdir(output_eval_dir + "/pnml")]
    for f in filelist:
        file_name = output_eval_dir + "/pnml/" + f
        os.remove(file_name)
        
def convert_input_pnml_to_hgr(io_param):
    """
    converts all input .pnml files into .hgr files
    """
    # set up working directory
    working_dir = io_param['working_dir']
    output_eval_dir = io_param['output_eval_dir']
    # all the pnml files in input_eval_dir will be evaluated
    input_eval_dir = io_param['input_eval_dir']
    
    
    # setup logger
    logger = logging.getLogger(__name__)
    
    file_root = None
    
    for file_name in os.listdir(input_eval_dir):
        if file_name.endswith(".pnml"):
                file_root = os.path.splitext(file_name)[0]
                file_ext = os.path.splitext(file_name)[1]
                print("=============================================================================")
                print("========= Processing {1} file: {0}".format(file_name, file_ext))
                print("=============================================================================")
        
        # randomly initialise utility in hypergraph (and keep it the same for the entire evaluation
        
                conversion = setup_conversion_pnet_to_hg(file_root, input_eval_dir, output_eval_dir)
                hg = conversion[0]
                out_file_name = input_eval_dir + '/' + file_root + '.hgr'
                write_hg_to_file(hg, out_file_name)

        
        
def optimise(io_param, aco_param, SYS_TYPE):
    '''
    reads all input hypergraphs (in .hgr files) and does the optimisation
    :param aco_param: parameters for aco optimisation (see main)
    '''
    """
    
    """
    # set up working directory
    working_dir = io_param['working_dir']
    output_eval_dir = io_param['output_eval_dir']
    # all the pnml files in input_eval_dir will be evaluated
    input_eval_dir = io_param['input_eval_dir']
    
    
    # set up ACO params
    COL_NUM = aco_param['COL_NUM']
    COL_NUM_MAX = aco_param['COL_NUM_MAX']
    COL_NUM_STEP = aco_param['COL_NUM_STEP']
    ANT_NUM = aco_param['ANT_NUM']
    ANT_NUM_MAX = aco_param['ANT_NUM_MAX']
    ANT_NUM_STEP = aco_param['ANT_NUM_STEP']
    phero_tau = aco_param['phero_tau']
    W_UTILITY = aco_param['W_UTILITY']
    

    # cleanup output directories!
    #cleanup(output_eval_dir)
    
    # setup logger
    log_file = output_eval_dir+"/logs/run.log"
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.WARNING)
    logger = logging.getLogger(__name__)
    
    # non .pnml files in input_eval_dir will be ignored
    for file_name in os.listdir(input_eval_dir):
        if file_name.endswith(".hgr"):
            file_root = os.path.splitext(file_name)[0]
            file_ext = os.path.splitext(file_name)[1]
            print("=============================================================================")
            print("========= Processing {1} file: {0}".format(file_name, file_ext))
            print("=============================================================================")
        
            hg = read_hg_from_file(input_eval_dir + '/' + file_name)
            conv_pnet_to_hg_time = 0.0
            tau_post_time = 0.0
            stats = get_statistics(hg)
            
            performance_file_name = output_eval_dir+"/performance/"+file_root+".txt"
            performance_file = open(performance_file_name, 'w')
            # write header line
            header_line = "FILE ROOT" + '\t' + "COL_NUM" + '\t' + "ANT_NUM" + '\t' + "TAU PHERO" + '\t' "UTILITY" + '\t' + "PNET_TO_HG_T" + '\t' + "TAU_POST_T" + '\t' + "ACO_T" + '\t' + "PNET_POST_T" + '\t' + "ACTIVITIES" + '\t' + "TOTAL TRANSITIONS" + '\t' + "XOR JOINS" + '\t' + "XOR SPLITS"
            performance_file.write(header_line)
            performance_file.write('\n')
            # reset_pheromone
            #hg = reset_pheromone(hg)
            # loop on colonies
            for col_num in range(COL_NUM, COL_NUM_MAX, COL_NUM_STEP):
                # reset_pheromone
                print_hg_std_out_only(hg)
                #hg = reset_pheromone(hg)
                # loop on ants within colonies
                for ant_num in range(ANT_NUM, ANT_NUM_MAX, ANT_NUM_STEP):
                    # possible loop on phero_tau (nest here)
                    aco_result = sim_run_pnml_files(hg, col_num, ant_num, phero_tau, W_UTILITY, file_root, input_eval_dir, output_eval_dir, SYS_TYPE)
                    aco_alg_time = aco_result[0] 
                    pnet_post_time = aco_result[1]
                    utility = aco_result[2]
                    # EVALUATION FINISHED, WRITE PERFORMANCE RESULT
                    new_perf_line = file_root + '\t' + str(col_num) + '\t' + str(ant_num) + '\t' + str(phero_tau) + '\t' + str(utility) + '\t' + str(conv_pnet_to_hg_time) + '\t' + str(tau_post_time) + '\t' + str(aco_alg_time) + '\t' + str(pnet_post_time)+ '\t' + str(stats['activities']) + '\t' + str(stats['transitions']) + '\t' + str(stats['xor-join']) + '\t' + str(stats['xor-split'])
                    performance_file.write(new_perf_line)
                    performance_file.write('\n')
            performance_file.close()
    print("--- TERMINATED ---")
    


def convert_and_optimise(io_param, aco_param, SYS_TYPE):
    """
    converts all input pnml file into hypergraphs, initialise them randomly and does the optimisation
    """
    # set up working directory
    working_dir = io_param['working_dir']
    output_eval_dir = io_param['output_eval_dir']
    # all the pnml files in input_eval_dir will be evaluated
    input_eval_dir = io_param['input_eval_dir']
    
    
    # set up ACO params
    COL_NUM = aco_param['COL_NUM']
    COL_NUM_MAX = aco_param['COL_NUM_MAX']
    COL_NUM_STEP = aco_param['COL_NUM_STEP']
    ANT_NUM = aco_param['ANT_NUM']
    ANT_NUM_MAX = aco_param['ANT_NUM_MAX']
    ANT_NUM_STEP = aco_param['ANT_NUM_STEP']
    phero_tau = aco_param['phero_tau']
    W_UTILITY = aco_param['W_UTILITY']


    

    # cleanup output directories!
    #cleanup(output_eval_dir)
    
    # setup logger
    
    logger = logging.getLogger(__name__)
    
    # non .pnml files in input_eval_dir will be ignored
    for file_name in os.listdir(input_eval_dir):
        if file_name.endswith(".pnml"):
            file_root = os.path.splitext(file_name)[0]
            file_ext = os.path.splitext(file_name)[1]
            print("=============================================================================")
            print("========= Processing {1} file: {0}".format(file_name, file_ext))
            print("=============================================================================")
        
        # randomly initialise utility in hypergraph (and keep it the same for the entire evaluation
        # TBC TBC TBC
        # loop on COL_NUM
            conversion = setup_conversion_pnet_to_hg(file_root, input_eval_dir, output_eval_dir)
            hg = conversion[0]
            conv_pnet_to_hg_time = conversion[1] 
            tau_post_time = conversion[2]
            stats = get_statistics(hg)
            
            performance_file_name = output_eval_dir+"/performance/"+file_root+".txt"
            performance_file = open(performance_file_name, 'w')
            # write header line
            header_line = "FILE ROOT" + '\t' + "COL_NUM" + '\t' + "ANT_NUM" + '\t' + "TAU PHERO" + '\t' "UTILITY" + '\t' + "PNET_TO_HG_T" + '\t' + "TAU_POST_T" + '\t' + "ACO_T" + '\t' + "PNET_POST_T" + '\t' + "ACTIVITIES" + '\t' + "TOTAL TRANSITIONS" + '\t' + "XOR JOINS" + '\t' + "XOR SPLITS"
            performance_file.write(header_line)
            performance_file.write('\n')
            # reset_pheromone
            #hg = reset_pheromone(hg)
            # loop on colonies
            for col_num in range(COL_NUM, COL_NUM_MAX, COL_NUM_STEP):
                # reset_pheromone
                hg = reset_pheromone(hg)
                # loop on ants within colonies
                for ant_num in range(ANT_NUM, ANT_NUM_MAX, ANT_NUM_STEP):
                    # possible loop on phero_tau (nest here)
                    aco_result = sim_run_pnml_files(hg, col_num, ant_num, phero_tau, W_UTILITY, file_root, input_eval_dir, output_eval_dir, SYS_TYPE)
                    aco_alg_time = aco_result[0] 
                    pnet_post_time = aco_result[1]
                    utility = aco_result[2]
                    # EVALUATION FINISHED, WRITE PERFORMANCE RESULT
                    new_perf_line = file_root + '\t' + str(col_num) + '\t' + str(ant_num) + '\t' + str(phero_tau) + '\t' + str(utility) + '\t' + str(conv_pnet_to_hg_time) + '\t' + str(tau_post_time) + '\t' + str(aco_alg_time) + '\t' + str(pnet_post_time)+ '\t' + str(stats['activities']) + '\t' + str(stats['transitions']) + '\t' + str(stats['xor-join']) + '\t' + str(stats['xor-split'])
                    performance_file.write(new_perf_line)
                    performance_file.write('\n')
            performance_file.close()
    print("--- TERMINATED ---")
        
    
            
        

if __name__ == "__main__":
    
    
    # set working directory
    working_dir = "C://opsupport_bpm_files"
    output_eval_dir = working_dir+"/eval/output_files"
    
    io_param = {}
    io_param['working_dir'] = working_dir 
    io_param['output_eval_dir'] = working_dir+"/eval/output_files"
    io_param['input_eval_dir'] = working_dir+"/eval/input_files"
    io_param['log'] = output_eval_dir+"/logs/run.log"
    
    # cleanup output directory
    cleanup(output_eval_dir)
    
    # set logger
    log_file = io_param['log']
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.WARNING)
    
    
    # set aco parameters
    aco_param = {}
    aco_param['COL_NUM'] = 2
    aco_param['COL_NUM_MAX'] = 10
    aco_param['COL_NUM_STEP'] = 5
    aco_param['ANT_NUM'] = 6
    aco_param['ANT_NUM_MAX'] = 47
    aco_param['ANT_NUM_STEP'] = 9
    aco_param['phero_tau'] = 0.5
    W_UTILITY = {'cost' : 1.0, 'avail' : 0.0, 'qual' : 0.0, 'time' : 0.0}
    aco_param['W_UTILITY'] = W_UTILITY
    
    # convert pnml files to hgr 
    convert_input_pnml_to_hgr(io_param)
    # optimise existing hgr files
    optimise(io_param, aco_param)
    
    # convert and optimise all pnml files
    #convert_and_optimise(io_param, aco_param)