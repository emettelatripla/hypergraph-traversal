'''
Created on Aug 7, 2016

@author: UNIST
'''

import logging
from time import time

from opsupport_bpm.aco.aco_directed_hypergraph import aco_algorithm_norec
from opsupport_bpm.aco.aco_misc import random_generate_hg_BF, add_random_loops
from opsupport_bpm.aco.simulation.simulation_pnml_only import cleanup
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    print_hg_std_out_only, read_hg_from_file


def do_one_run(io_param, aco_param, hg_gen_param):
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
    
    
    # setup hg generation params
    L_SIZE = hg_gen_param['level_size']
    B_SIZE_MIN = hg_gen_param['block_size_min']
    B_SIZE_MAX = hg_gen_param['block_size_max']
    
    # generate hg
    hg = random_generate_hg_BF(L_SIZE, B_SIZE_MIN, B_SIZE_MAX)
    hg = add_random_loops(hg, 5, 5)
    
    # write hg on file
    print("writing file FIRST time....")
    hg_gen_file_name = input_eval_dir + '/test_rewrite.hgr'
    print_hg_std_out_only(hg)
    write_hg_to_file(hg, hg_gen_file_name)
    
    #print("read from file FIRST time....")
    #hg = read_hg_from_file(hg_gen_file_name)
    #print("writing file SECOND time....")
    #write_hg_to_file(hg, hg_gen_file_name)
    
    # run optimisation
    #optimise(io_param, aco_param)
    
    start_time_aco = time()
    print("running aco....")
    aco_result = aco_algorithm_norec(hg, ANT_NUM, COL_NUM, phero_tau, W_UTILITY)
    p_opt = aco_result[0]
    utility = aco_result[1]
    end_time_aco = time()
    aco_alg_time = end_time_aco - start_time_aco
    print_hg_std_out_only(p_opt)
    print("ACO optimisation took: {0}s".format(aco_alg_time))
    print("UTILITY: {0}".format(utility))
    
def do_one_run_single_file(io_param, aco_param, file_name):
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

    # setup hg generation params
    L_SIZE = hg_gen_param['level_size']
    B_SIZE_MIN = hg_gen_param['block_size_min']
    B_SIZE_MAX = hg_gen_param['block_size_max']

    # generate hg
    hg = read_hg_from_file(file_name)

    # write hg on file
    #print("writing file FIRST time....")
    #hg_gen_file_name = input_eval_dir + '/test_rewrite.hgr'
    print_hg_std_out_only(hg)
    #write_hg_to_file(hg, hg_gen_file_name)

    # print("read from file FIRST time....")
    # hg = read_hg_from_file(hg_gen_file_name)
    # print("writing file SECOND time....")
    # write_hg_to_file(hg, hg_gen_file_name)

    # run optimisation
    # optimise(io_param, aco_param)

    start_time_aco = time()
    print("running aco....")
    aco_result = aco_algorithm_norec(hg, ANT_NUM, COL_NUM, phero_tau, W_UTILITY)
    p_opt = aco_result[0]
    utility = aco_result[1]
    end_time_aco = time()
    aco_alg_time = end_time_aco - start_time_aco
    print_hg_std_out_only(p_opt)
    write_hg_to_file (hg, "opt.hgr")
    print("ACO optimisation took: {0}s".format(aco_alg_time))
    print("UTILITY: {0}".format(utility))

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
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.DEBUG)
    
    
    # set aco parameters
    aco_param = {}
    aco_param['COL_NUM'] = 2
    aco_param['COL_NUM_MAX'] = 3
    aco_param['COL_NUM_STEP'] = 5
    aco_param['ANT_NUM'] = 2
    aco_param['ANT_NUM_MAX'] = 3
    aco_param['ANT_NUM_STEP'] = 9
    aco_param['phero_tau'] = 0.5
    W_UTILITY = {'cost' : 1.0, 'avail' : 0.0, 'qual' : 0.0, 'time' : 0.0}
    aco_param['W_UTILITY'] = W_UTILITY
    
    # set up hg gen params
    hg_gen_param = {}
    hg_gen_param['level_size'] = 2
    hg_gen_param['block_size_min'] = 2
    hg_gen_param['block_size_max'] = 2
    
    #do_one_run(io_param, aco_param, hg_gen_param)

    # Test smart_NODE
    #file_name = "C://opsupport_bpm_files/eval/input_files/ex1_inductive_smart_node.hgr"

    # Test smart ATTRIBUTE
    #file_name = "C://opsupport_bpm_files/eval/input_files/ex1_inductive_smart_attribute.hgr"

    # Test smart SERVICE
    #file_name = "C://opsupport_bpm_files/eval/input_files/ex1_inductive_smart_service.hgr"

    # file_name = "C://opsupport_bpm_files/eval/input_files/PurchasingExample.hgr"
    # file_name = "C://opsupport_bpm_files/eval/input_files/road_fine_process.hgr"
    file_name = "C://opsupport_bpm_files/eval/input_files/bpi_challenge2012.hgr"

    do_one_run_single_file(io_param, aco_param, file_name)