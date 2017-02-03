import csv
import json
import logging
import sys

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_nonrec
from opsupport_bpm.models.hypergraph import reset_pheromone

from opsupport_bpm.models.bf_path_enumerator import BF_PathEnumerator

class EventLogHandler():

    def __init__(self):
        self.file_name = None
        self.type = None

    def __init__(self, log_name, file_name, fieldnames):
        self.file_name = file_name
        self.log_name = log_name
        self.field_names = fieldnames
        self.log_by_case = None
        self.opt_path = None
        self.hgr = None

    def dump_json_to_file(self, json_file_name):
        json_file = open(json_file_name, 'w')
        csv_file = open(self.file_name, 'r')
        reader = csv.DictReader(csv_file, self.field_names)
        for row in reader:
            json.dump(row, json_file)
            json_file.write('\n')
        json_file.close()
        csv_file.close()

    def create_log_by_case(self):
        """
        :return:
        """
        csv_file = open(self.file_name, 'r')
        reader = csv.DictReader(csv_file, self.field_names)
        self.log_by_case = {}
        for row in reader:
            if row['Case_id'] in self.log_by_case:
                self.log_by_case[row['Case_id']].append(row)
            else:
                self.log_by_case[row['Case_id']] = []
                self.log_by_case[row['Case_id']].append(row)
        csv_file.close()

    def print_log_by_case(self):
        for key in self.log_by_case:
            print("{0} - {1}".format(key,self.log_by_case[key]))

    def get_trace(self, case_id):
        event_list = self.log_by_case[case_id]
        trace = []
        for event in event_list:
            trace.append(event['activity'])
        return trace

    def set_optimal_path(self, file_name):
        hg = read_hg_from_file(file_name)
        self.opt_path = hg

    def set_hgr(self,file_name):
        hg = read_hg_from_file(file_name)
        self.hgr = hg






    def get_all_decisions(self):
        """
        Return the list of decisions in a hypergraph in a dictionary:
        {1: {'antec' : ['actA','actB'], 'conseq': ['actC','actD']}}
        :param case_id:
        :return:
        """
        node_set = self.hgr.get_node_set()
        dec_count = 0
        decisions = {}
        for node in node_set:
            if self.hgr.get_node_attribute(node, 'type') == 'xor-split':
                antec = []
                for edge in self.hgr.get_backward_star(node):
                    antec.append(list(self.hgr.get_hyperedge_tail(edge))[0])
                conseq = []
                for edge in self.hgr.get_forward_star(node):
                    conseq.append(list(self.hgr.get_hyperedge_head(edge))[0])
                decisions[node] = {'antec': antec, 'conseq': conseq}
                dec_count += 1
        return decisions


    def get_case_dec_matching(self, case_id):
        dec_opt = self.get_optimal_decisions()
        dec_all = self.get_all_decisions()
        trace = self.get_trace(case_id)
        DEC_OK, DEC_DEV, DEC_BACK = 0, 0, 0
        for dec in dec_all:
            antec_list, antec_opt, conseq_list, conseq_opt = dec_all[dec]['antec'], dec_opt[dec]['antec'], dec_all[dec]['conseq'],   dec_opt[dec]['conseq']
            # look for antecedent in trace
            if antec_opt in trace:
                #  match consequence
                antec_index = trace.index(antec_opt)
                cons_trace = trace[antec_index + 1]             # consequent is the next activity in the trace
                if cons_trace == conseq_opt:
                    # CASE 1: optimal path has been followed
                    DEC_OK += 1
                else:
                    if cons_trace in conseq_list:
                        # CASE 2: deviation from optimal path
                        DEC_DEV += 1
            else:
                if conseq_opt in trace:
                    conseq_index = trace.index(conseq_opt)
                    antec_trace = trace[conseq_index - 1]
                    if antec_trace != antec_opt:
                        DEC_BACK += 1
        # determine metric value
        return DEC_OK, DEC_DEV, DEC_BACK, len(dec_all)

    def is_trace_optimal(self, case_id, opt_traces):
        logger = logging.getLogger(__name__)
        case = self.get_trace(case_id)
        FOUND_OPT_MATCH = False
        for opt_trace in opt_traces:
            logger.info("___trace: {0}".format(case))
            logger.info("OPTtrace: {0}".format(opt_trace))
            IS_OPTIMAL = True
            if len(case) != len(opt_trace):
                return False
            for act, opt_act in zip(case, opt_trace):
                logger.info("...matching: {0} -- {1}".format(act,opt_act))
                if act == opt_act:
                    log.info("true")
                    IS_OPTIMAL = True
                else:
                    log.info("false")
                    IS_OPTIMAL = False
                    break
            if IS_OPTIMAL:
                logger.info("Optimal match found")
                return True
        return False


    def get_number_optimal_traces(self,opt_traces):
        traces = self.log_by_case
        num_optimal = 0
        for key in traces:
            if self.is_trace_optimal(key,opt_traces):
                num_optimal += 1
        return num_optimal


    def get_ratio_optimal_traces(self,opt_traces):
        num_optimal = self.get_number_optimal_traces(opt_traces)
        return num_optimal / len(self.log_by_case)


    def get_optimal_decisions(self, case_id, opt_decisions):
        """
        checks how many optimal decisions in a trace have been made
        :param opt_decisions:
        :return:
        """
        case = self.get_trace(case_id)
        num_dec, num_opt_dec = 0, 0
        # WARNING: we have to handle loops in trace: only the first time a choice is made is considered
        banned_choices = []
        for key in opt_decisions:
            antec, conseq = opt_decisions[key]['antec'], opt_decisions[key]['conseq']
            for i in range(len(case)-1):
                if case[i] == antec and case[i] not in banned_choices:
                    banned_choices.append(antec)
                    num_dec += 1
                    if case[i+1] == conseq:
                        num_opt_dec += 1
        return num_dec, num_opt_dec, num_dec / len(opt_decisions), num_opt_dec / len(opt_decisions)












if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.WARNING)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    logger = logging.getLogger(__name__)




    csvfile_name = "C://opsupport_bpm_files/event_logs/PurchasingExample.csv"
    fieldnames = ('Case_id', 't_start', 't_end', 'activity', 'resource', 'role')
    ELH = EventLogHandler("PurchaseExample", csvfile_name,fieldnames)

    ELH.dump_json_to_file(ELH.log_name+".json")
    ELH.create_log_by_case()
    #ELH.print_log_by_case()

    #print(ELH.get_trace("391"))
    #print(ELH.get_trace("889"))
    #print(ELH.get_trace("692"))

    ELH.set_optimal_path('popt.hgr')

    hgr_file = "C://opsupport_bpm_files/pnml_input/inductive/PurchasingExample.hgr"

    ELH.set_hgr(hgr_file)



    # print("122", ELH.is_trace_optimal("122"))

    print(ELH.get_trace("411"))
    print(ELH.get_trace("224"))

    # GET OPTIMAL TRACES
    PE = BF_PathEnumerator("popt.hgr")
    PE.get_hyperpath_tree(PE.tree)
    PE.prepare_tree_for_trace_enumeration()
    PE.get_traces(PE.tree)
    opt_traces = PE.actlist_from_traces(PE.tree.data)


    count_opt_traces = 0

    """ \n\n======= test optimaly of 1 case ==============="""
    #print(ELH.is_trace_optimal("411", opt_traces))

    """ \n\n======= test all cases ==============="""
    # for key in ELH.log_by_case:
    #     if ELH.is_trace_optimal(key, opt_traces) == True:
    #         print("Case {0}, is optimal".format(key))
    #         count_opt_traces += 1
    # print("Optimal traces / Total traces: {0} / {1}".format(count_opt_traces, len(ELH.log_by_case)))
    # print("STOP!")

    """ \n\n======= ration and numbers ==============="""
    print(ELH.get_number_optimal_traces(opt_traces))
    print(ELH.get_ratio_optimal_traces(opt_traces))

    opt_decisions = PE.get_optimal_decisions()
    print(opt_decisions)
    for key in ELH.log_by_case:
        ret = ELH.get_optimal_decisions(key, opt_decisions)
        if ret[3] == 1.0:
            found = 'True ================================='
        else:
            found = 'false'
        print("Case {0}: {1}, {2}, {3}, {4}, {5}".format(key, ret[0], ret[1], ret[2], ret[3], found))





