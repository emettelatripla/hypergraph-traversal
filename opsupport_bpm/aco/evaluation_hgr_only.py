'''
Created on Aug 7, 2016

@author: UNIST
'''

import logging
import os
from time import time

from opsupport_bpm.aco.aco_directed_hypergraph import aco_algorithm_norec
from opsupport_bpm.aco.aco_misc import random_generate_hg, add_random_loops
from opsupport_bpm.models.hypergraph import get_statistics
from opsupport_bpm.models.hypergraph import reset_pheromone
from opsupport_bpm.util.print_hypergraph import write_hg_to_file, \
    read_hg_from_file


def cleanup(input_eval_dir, output_eval_dir):
    print("Doing some cleanup before starting....")
#     # logs
#     filelist = [ f for f in os.listdir(output_eval_dir + "/logs")]
#     for f in filelist:
#         file_name = output_eval_dir + "/logs/" + f
#         os.remove(file_name)
    # peformance
    filelist = [ f for f in os.listdir(output_eval_dir)]
    for f in filelist:
        file_name = output_eval_dir + "/" + f
        os.remove(file_name)
    filelist = [ f for f in os.listdir(input_eval_dir)]
    for f in filelist:
        file_name = input_eval_dir + "/" + f
        os.remove(file_name)
    # pnml
#     filelist = [ f for f in os.listdir(output_eval_dir + "/pnml")]
#     for f in filelist:
#         file_name = output_eval_dir + "/pnml/" + f
#         os.remove(file_name)

def sim_run_hgr_only(io_param, aco_param, hg_gen_param):
    # read parameters
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
    # set up hg_gen param
    L_SIZE_MIN = hg_gen_param['level_size_min']
    L_SIZE_MAX = hg_gen_param['level_size_max']
    L_SIZE_STEP = hg_gen_param['level_size_step']
    B_SIZE_MIN = hg_gen_param['block_size_min']
    B_SIZE_MAX = hg_gen_param['block_size_max']
    #LOOP_NO_MIN = hg_gen_param['loop_no_min']
    LOOP_NO_MAX = hg_gen_param['loop_no_max']
    LOOP_L_MIN = hg_gen_param['loop_length_min']
    LOOP_L_MAX = hg_gen_param['loop_length_max']
    
    
    # generate hgr files
    print("+++++++++++ Generating hypergraphs....")
    for i in range(L_SIZE_MIN, L_SIZE_MAX, L_SIZE_STEP):
        for j in range(LOOP_L_MIN, LOOP_L_MAX, 1):
            file_name = input_eval_dir + '/hg_level' + str(i) + '_' + str(j) + '.hgr'
            hg = random_generate_hg(i, B_SIZE_MIN, B_SIZE_MAX)
            hg = add_random_loops(hg, LOOP_NO_MAX, j)
            write_hg_to_file(hg, file_name)
            print("+++ hypergraph level {0}, loop length {1}".format(i,j))
    "+++++++++++ Hypergraph generation completed"
    
    
        
    sep = '\t'
    
    # main loop (calls single_run)
    for file_name in os.listdir(input_eval_dir):
        if file_name.endswith(".hgr"):
            file_root = os.path.splitext(file_name)[0]
            file_ext = os.path.splitext(file_name)[1]
            print("=============================================================================")
            print("========= Processing {1} file: {0}".format(file_name, file_ext))
            print("=============================================================================")
            file_name = input_eval_dir + '/' + file_name
            hg = read_hg_from_file(file_name)
            hg_stats = get_statistics(hg)
            perf_file_name = output_eval_dir + '/performance/' + file_root + '.txt'
            perf_file = open(perf_file_name, 'w')
            line = 'FILE_ROOT' + sep + 'COL_NUM' + sep + 'ANT_NUM' + sep + 'UTILITY' + sep + 'EXEC_TIME' +  sep + 'ACT' + sep + 'TRANS' + sep + 'XOR-JOINS' + sep + 'XOR-SPLITS'
            perf_file.write(line)
            perf_file.write('\n')
            # run aco optimisation for all possible configuration
            for col_num in range(COL_NUM, COL_NUM_MAX, COL_NUM_STEP):
                hg = reset_pheromone(hg)
                for ant_num in range(ANT_NUM, ANT_NUM_MAX, ANT_NUM_STEP):
                    
                    start_time_aco = time()
                    aco_result = aco_algorithm_norec(hg, ant_num, col_num, phero_tau, W_UTILITY)
                    end_time_aco = time()
                    p_opt = aco_result[0]
                    utility = aco_result[1]
                    aco_alg_time = end_time_aco - start_time_aco
                    print("ACO optimisation took: {0}s".format(aco_alg_time))
                    
                    line = file_root + sep + str(col_num) + sep + str(ant_num) + sep + str(utility) + sep + str(aco_alg_time) + sep + str(hg_stats['activities']) + sep + str(hg_stats['transitions']) + sep + str(hg_stats['xor-join']) + sep + str(hg_stats['xor-split'])
                    perf_file.write(line)
                    perf_file.write('\n')
            perf_file.close()
    print("TERMINATED")
                    
    
    
    

if __name__ == "__main__":
    
    # set working directory
    working_dir = "C://opsupport_bpm_files"
    output_eval_dir = working_dir+"/eval/output_files"
    
    io_param = {}
    io_param['working_dir'] = working_dir 
    io_param['output_eval_dir'] = working_dir+"/eval/hgr/output"
    io_param['input_eval_dir'] = working_dir+"/eval/hgr/input"
    io_param['log'] = output_eval_dir+"/logs/run.log"
    
    # cleanup output directory
    cleanup(io_param['input_eval_dir'], io_param['output_eval_dir'])
    
    # set logger
    log_file = io_param['log']
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.WARNING)
    
    
    # set aco parameters
    aco_param = {}
    aco_param['COL_NUM'] = 6
    aco_param['COL_NUM_MAX'] = 12
    aco_param['COL_NUM_STEP'] = 5
    aco_param['ANT_NUM'] = 16
    aco_param['ANT_NUM_MAX'] = 48
    aco_param['ANT_NUM_STEP'] = 9
    aco_param['phero_tau'] = 0.5
    W_UTILITY = {'cost' : 1.0, 'avail' : 0.0, 'qual' : 0.0, 'time' : 0.0}
    aco_param['W_UTILITY'] = W_UTILITY
    
    # set up hg gen params
    hg_gen_param = {}
    hg_gen_param['level_size_min'] = 7
    hg_gen_param['level_size_max'] = 8
    hg_gen_param['level_size_step'] = 1
    hg_gen_param['block_size_min'] = 2
    hg_gen_param['block_size_max'] = 3
    
    #LOOP_NO_MIN = hg_gen_param['loop_no_min']
    hg_gen_param['loop_no_max'] = 3
    hg_gen_param['loop_length_min'] = 3
    hg_gen_param['loop_length_max'] = 5
    
    
    sim_run_hgr_only(io_param, aco_param, hg_gen_param)