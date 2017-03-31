'''
Created on 2016. 8. 16.

@author: UNIST
'''

import logging
from tkinter import *

from opsupport_bpm.aco.simulation.simulation_hgr_only import sim_run_hgr_only

from opsupport_bpm.aco.simulation.simulation_pnml_only import cleanup
from opsupport_bpm.aco.simulation.simulation_pnml_only import convert_input_pnml_to_hgr
from opsupport_bpm.aco.simulation.simulation_pnml_only import optimise


def simulation_GUI():
    
    # set working directory (not modificable using GUI
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
    #log_file = io_param['log']
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.WARNING)
    
    # initialise main window
    main_window = Tk()
    main_window.wm_title("OPSUPPORT: ACO and Process generation settings")
    
    row_num = 0
    
    Label(main_window, text = '=== ACO Parameters - Colonies (required) ===').grid(row = row_num, column = 0)
    
    row_num += 1
    col_num_label = Label(main_window, text = 'Number of colonies (min):')
    col_num_label.grid(row = row_num, column = 0)
    col_num_entry = Entry(main_window)
    col_num_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    col_num_max_label = Label(main_window, text = 'Number of colonies (max):')
    col_num_max_label.grid(row = row_num, column = 0)
    col_num_max_entry = Entry(main_window)
    col_num_max_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    col_num_step_label = Label(main_window, text = 'Number of colonies (step):')
    col_num_step_label.grid(row = row_num, column = 0)
    col_num_step_entry = Entry(main_window)
    col_num_step_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    Label(main_window, text = '=== ACO Parameters - Ants (required) ===').grid(row = row_num, column = 0)
    
    row_num += 1
    ant_num_label = Label(main_window, text = 'Number of ants (min):')
    ant_num_label.grid(row = row_num, column = 0)
    ant_num_entry = Entry(main_window)
    ant_num_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    ant_num_max_label = Label(main_window, text = 'Number of ants (max):')
    ant_num_max_label.grid(row = row_num, column = 0)
    ant_num_max_entry = Entry(main_window)
    ant_num_max_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    ant_num_step_label = Label(main_window, text = 'Number of ants (step):')
    ant_num_step_label.grid(row = row_num, column = 0)
    ant_num_step_entry = Entry(main_window)
    ant_num_step_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    phero_tau_label = Label(main_window, text = 'Tau (pheromone evaporation):')
    phero_tau_label.grid(row = row_num, column = 0)
    phero_tau_entry = Entry(main_window)
    phero_tau_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    Label(main_window, text = '=== Utility (required) ===').grid(row = row_num, column = 0)
    
    row_num += 1
    cost_label = Label(main_window, text = 'Weight of cost:')
    cost_label.grid(row = row_num, column = 0)
    cost_entry = Entry(main_window)
    cost_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    avail_label = Label(main_window, text = 'Weight of availability:')
    avail_label.grid(row = row_num, column = 0)
    avail_entry = Entry(main_window)
    avail_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    time_label = Label(main_window, text = 'Weight of time:')
    time_label.grid(row = row_num, column = 0)
    time_entry = Entry(main_window)
    time_entry.grid(row = row_num, column = 1)
    
    row_num += 1
    qual_label = Label(main_window, text = 'Weight of quality:')
    qual_label.grid(row = row_num, column = 0)
    qual_entry = Entry(main_window)
    qual_entry.grid(row = row_num, column = 1)

    row_num += 1
    Label(main_window, text='---- Artificial process generation (fill only if using artificially generated processes) ---').grid(row=row_num, column=0)

    row_num += 1
    min_level_label = Label(main_window, text='Min num of levels:')
    min_level_label.grid(row=row_num, column=0)
    min_level_entry = Entry(main_window)
    min_level_entry.grid(row=row_num, column=1)

    row_num += 1
    max_level_label = Label(main_window, text='Max num of levels:')
    max_level_label.grid(row=row_num, column=0)
    max_level_entry = Entry(main_window)
    max_level_entry.grid(row=row_num, column=1)

    row_num += 1
    step_level_label = Label(main_window, text='Levels step:')
    step_level_label.grid(row=row_num, column=0)
    step_level_entry = Entry(main_window)
    step_level_entry.grid(row=row_num, column=1)

    row_num += 1
    block_len_label = Label(main_window, text='Length of rewrite block (min):')
    block_len_label.grid(row=row_num, column=0)
    block_len_entry = Entry(main_window)
    block_len_entry.grid(row=row_num, column=1)

    row_num += 1
    block_len_max_label = Label(main_window, text='Length of rewrite block (max):')
    block_len_max_label.grid(row=row_num, column=0)
    block_len_max_entry = Entry(main_window)
    block_len_max_entry.grid(row=row_num, column=1)

    row_num += 1
    loop_num_label = Label(main_window, text='Number of loops:')
    loop_num_label.grid(row=row_num, column=0)
    loop_num_entry = Entry(main_window)
    loop_num_entry.grid(row=row_num, column=1)

    row_num += 1
    loop_length_label = Label(main_window, text='Length of loops (min):')
    loop_length_label.grid(row=row_num, column=0)
    loop_length_entry = Entry(main_window)
    loop_length_entry.grid(row=row_num, column=1)

    row_num += 1
    loop_length_max_label = Label(main_window, text='Length of loops (max):')
    loop_length_max_label.grid(row=row_num, column=0)
    loop_length_max_entry = Entry(main_window)
    loop_length_max_entry.grid(row=row_num, column=1)

    row_num += 1
    SYS_TYPE_label = Label(main_window, text='Ant system type (ACS or MMAS):')
    SYS_TYPE_label.grid(row=row_num, column=0)
    SYS_TYPE_label_entry = Entry(main_window)
    SYS_TYPE_label_entry.grid(row=row_num, column=1)
    
    def start_simulation_real_logs():
        aco_param = {}
        aco_param['COL_NUM'] = int(col_num_entry.get())
        aco_param['COL_NUM_MAX'] = int(col_num_max_entry.get())
        aco_param['COL_NUM_STEP'] = int(col_num_step_entry.get())
        aco_param['ANT_NUM'] = int(ant_num_entry.get())
        aco_param['ANT_NUM_MAX'] = int(ant_num_max_entry.get())
        aco_param['ANT_NUM_STEP'] = int(ant_num_step_entry.get())
        aco_param['phero_tau'] = float(phero_tau_entry.get())
        W_UTILITY = {'cost' : float(cost_entry.get()), 'avail' : float(avail_entry.get()), 
                     'qual' : float(qual_entry.get()), 'time' : float(time_entry.get())}
        aco_param['W_UTILITY'] = W_UTILITY

        SYS_TYPE = SYS_TYPE_label_entry.get()
        
        # convert input pnml into hgr files
        convert_input_pnml_to_hgr(io_param)
        # optimise existing hgr files
        optimise(io_param, aco_param, SYS_TYPE)

    def start_simulation_proc_gen():
        aco_param = {}
        aco_param['COL_NUM']        = int(col_num_entry.get())
        aco_param['COL_NUM_MAX']    = int(col_num_max_entry.get())
        aco_param['COL_NUM_STEP']   = int(col_num_step_entry.get())
        aco_param['ANT_NUM']        = int(ant_num_entry.get())
        aco_param['ANT_NUM_MAX']    = int(ant_num_max_entry.get())
        aco_param['ANT_NUM_STEP']   = int(ant_num_step_entry.get())
        aco_param['phero_tau']      = float(phero_tau_entry.get())
        W_UTILITY = {'cost': float(cost_entry.get()), 'avail': float(avail_entry.get()),
                     'qual': float(qual_entry.get()), 'time': float(time_entry.get())}
        aco_param['W_UTILITY'] = W_UTILITY

        gen_param = {}
        gen_param['min_level']      = int(min_level_entry.get())
        gen_param['max_level'] = int(max_level_entry.get())
        gen_param['step_level']    = int(step_level_entry.get())
        gen_param['block_len']     = int(block_len_entry.get())
        gen_param['gen_loop_no']    = int(loop_num_entry.get())
        gen_param['gen_loop_len']   = int(loop_length_entry.get())

        # set up hg_gen param
        gen_param['level_size_min'] = int(min_level_entry.get())
        gen_param['level_size_max'] = int(max_level_entry.get())
        gen_param['level_size_step'] = int(step_level_entry.get())

        gen_param['block_size_min'] = int(block_len_entry.get())
        gen_param['block_size_max'] = int(block_len_max_entry.get())
        gen_param['loop_no_max'] = int(loop_num_entry.get())
        gen_param['loop_length_min'] = int(loop_length_entry.get())
        gen_param['loop_length_max'] = int(loop_length_max_entry.get())

        SYS_TYPE = SYS_TYPE_label_entry.get()

        sim_run_hgr_only(io_param, aco_param, gen_param, SYS_TYPE)

    def sel():
        log_level = var.get()
        if log_level == "DEBUG":
            log_level = logging.DEBUG
        elif log_level == "INFO":
            log_level = logging.INFO
        elif log_level == "WARNING":
            log_level = logging.WARNING
        print("Log level set to : {0}".format(log_level))
        # set logger
        log_file = io_param['log']
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file, level=log_level)


    var = StringVar()

    row_num += 1
    Label(main_window, text='=== Select log level (mandatory) ===').grid(row=row_num, column=0)

    row_num += 1
    r1 = Radiobutton(text="DEBUG", variable=var, value="DEBUG", command=sel)
    r1.grid(row=row_num, column=0)
    r2 = Radiobutton(text="INFO", variable=var, value="INFO", command=sel)
    r2.grid(row=row_num, column=1)
    r3 = Radiobutton(text="WARNING", variable=var, value="WARNING", command=sel)
    r3.grid(row=row_num, column=2)

    row_num += 1
    start_button_1 = Button(text="START sim on pnml files in input folder", command=start_simulation_real_logs).grid(
        row=row_num, column=0)

    row_num += 1
    start_button_2 = Button(text="START sim on artificially generated processes",
                            command=start_simulation_proc_gen).grid(
        row=row_num, column=0)



    mainloop()
    


if __name__ == "__main__":


    simulation_GUI()