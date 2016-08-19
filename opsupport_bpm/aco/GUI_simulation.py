'''
Created on 2016. 8. 16.

@author: UNIST
'''


from tkinter import *
import sys
import logging

from opsupport_bpm.aco.evaluation import cleanup
from opsupport_bpm.aco.evaluation import convert_and_optimise
from opsupport_bpm.aco.evaluation import optimise
from opsupport_bpm.aco.evaluation import convert_input_pnml_to_hgr


def test_window():
    main_window = Tk()
    main_window.wm_title("Welcome to my first Tk GUI")
    count_label = Label(main_window, text="Count: 0")
    count_label.grid(row=0, column =1)
    count_value = 0
    def increment_count():
        global count_value, count_label
        count_value += 1
        count_label.configure(text = "Count: " + str(count_value))
        
    incr_button = Button(main_window, text = "Increment", command=increment_count)
    incr_button.grid(row = 0, column = 0)
    quit_button = Button(main_window, text = "Quit", command = main_window.destroy)
    quit_button.grid(row = 1, column = 0)
    
    name_label = Label(main_window, text = 'First Name')
    name_label.grid(row = 2, column = 0)
    lastn_label = Label(main_window, text = 'Last Name')
    lastn_label.grid(row = 3, column = 0)
    
    e_name = Entry(main_window)
    e_lastn = Entry(main_window)
    e_name.grid(row = 2, column = 1)
    e_lastn.grid(row = 3, column = 1)
    
    def show_entry_fields():
        print("First Name: {0}".format(e_name.get()))
        print("Last Name: {0}".format(e_lastn.get()))
        
    my_button = Button(text = "Print full name", command = show_entry_fields).grid(row = 4, column = 1)
    
    mainloop()
    
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
    log_file = io_param['log']
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename=log_file,level=logging.WARNING)
    
    # initialise main window
    main_window = Tk()
    main_window.wm_title("OPSUPPORT BPM - ACO Simulation Parameters")
    
    row_num = 0
    
    Label(main_window, text = 'ACO Parameters - Colonies').grid(row = row_num, column = 0)
    
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
    Label(main_window, text = 'ACO Parameters - Ants').grid(row = row_num, column = 0)
    
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
    Label(main_window, text = 'Utility').grid(row = row_num, column = 0)
    
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
    
    def start_simulation():
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
        
        # convert input pnml into hgr files
        convert_input_pnml_to_hgr(io_param)
        # optimise existing hgr files
        optimise(io_param, aco_param)
    
    row_num += 1
    start_button = Button(text = "start sim", command = start_simulation).grid(row = row_num, column = 1)
    
    mainloop()
    


if __name__ == "__main__":
    #test_window()
    simulation_GUI()