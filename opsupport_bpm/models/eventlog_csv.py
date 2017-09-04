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

from opsupport_bpm.models.bf_trace_enumerator import BF_PathEnumerator

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

    def _get_end_event_opt_path(self):
        """
        :return: the end event in the optimal path
        """
        nodes = self.opt_path.get_node_set()
        end_node = None
        for node in nodes:
            if self.opt_path.get_node_attribute(node, 'sink') == True:
                end_node = node
        return end_node

    def remove_incomplete_cases(self):
        """
        remove cases that do not contain teh end event in the optimal path
        :return:
        """
        logger = logging.getLogger()
        to_remove = []
        end_node = self._get_end_event_opt_path()
        for case_id in self.log_by_case:
            END_FOUND = False
            for event in self.log_by_case[case_id]:
                if event['activity'] == end_node:
                    END_FOUND = True
            if not END_FOUND:
                to_remove.append(case)
        # removing cases
        for case in to_remove:
            logger.debug("Removing case: ".format(case))
            del self.log_by_case[case]

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



    def opt_decisions_ratio(self, trace, opt_decisions):
        """
                Calculates the ratio of optimal decision taken in a trace
                :param trace:
                :param opt_decision:
                :return:
        """
        total_dec, correct_dec, incorrect_dec = 0, 0, 0
        incorrect_antec = set()
        for key in opt_decisions:
            antec, conseq = opt_decisions[key]['antec'][0], opt_decisions[key]['conseq'][0]
            checked = False             # to check only the first occurrence of a decision (otherwise is a loop)
            for event in trace:
                if event['activity'] == antec and checked == False:
                    # found antecedent, check if next evet in consequent and update counters
                    i = trace.index(event)
                    if i != len(trace) - 1:
                        if trace[i+1]['activity'] == conseq:
                            checked = True
                            correct_dec += 1
                        else:
                            checked = True
                            incorrect_dec += 1
                            incorrect_antec.add(antec)

            total_dec += 1
        return correct_dec, total_dec, correct_dec / total_dec, incorrect_dec, incorrect_antec












if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.WARNING)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    logger = logging.getLogger(__name__)


    """ STEP 0: setup file names and paths"""
    logger.warning("Setting up file names...")

    """ PURCHASING EXAMPLE """
    log_name = 'PurchasingExample'
    hgr_file,  opt_file = "PurchasingExample.hgr", "opt_purchasing.hgr"
    csvfile_name = "C://opsupport_bpm_files/event_logs/PurchasingExample.csv"
    fieldnames = ('Case_id', 't_start', 't_end', 'activity', 'resource', 'role')

    """ ROAD FINE PROCESS """
    # log_name = 'RoadFine'
    # hgr_file, opt_file = "road_fine_process.hgr", "opt_road_fine_process.hgr"
    # csvfile_name = "C://opsupport_bpm_files/event_logs/Road_Traffic_Fine_Management_Process.csv"
    # fieldnames = ('Case_id', 'activity', '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16')

    """ BPI CHALLENGE 2012 """
    # log_name = 'BPI2012'
    # hgr_file, opt_file = "bpi_challenge2012.hgr", "opt_bpi2012.hgr"
    # csvfile_name = "C://opsupport_bpm_files/event_logs/BPI_Challenge_2012.csv"
    # fieldnames = ('Case_id', 'activity_status', 'resource', 'timestamp', 'variant', 'variant_inc', 'amount', 'activity', 'transition')

    logger.warning ("...done!")

    """ STEP 1: LOAD EVENT LOG"""

    logger.warning("Creating event log handler...")
    ELH = EventLogHandler(log_name, csvfile_name,fieldnames)
    logger.warning("...done!")

    logger.warning ("Dumping log to json file...")
    ELH.dump_json_to_file(ELH.log_name+".json")
    logger.warning ("...done!")

    logger.warning ("Loading event log in memory...")
    ELH.create_log_by_case()            # create event login memory
    logger.warning ("...done!")
    ELH.set_optimal_path (opt_file)     # set ref to optimal path
    ELH.set_hgr (hgr_file)              # set ref to hypergraph process model

    #ELH.print_log_by_case()
    #print(ELH.get_trace("391"))
    #print(ELH.get_trace("889"))
    #print(ELH.get_trace("692"))





    """ STEP 2: ENUMERATE OPTIMAL TRACES """

    logger.warning ("Creating path enumerator...")
    PE = BF_PathEnumerator(opt_file)
    logger.warning ("...done!")

    logger.warning ("Preparing path enumerator for trace enumeration...")
    PE.get_hyperpath_tree(PE.tree)
    PE.prepare_tree_for_trace_enumeration()
    logger.warning ("...done!")

    logger.warning ("Enumerating traces...")
    PE._get_traces(PE.tree)
    logger.warning ("...done")
    opt_traces = PE.actlist_from_traces(PE.tree.data)


    count_opt_traces = 0

    """ \n\n======= test optimaly of 1 case ==============="""
    #print(ELH.is_trace_optimal("411", opt_traces))

    """ \n\n======= test all cases ==============="""
    for key in ELH.log_by_case:
        if ELH.is_trace_optimal(key, opt_traces) == True:
            # print("Case {0}, is optimal".format(key))
            count_opt_traces += 1
    print("Optimal traces / Total traces: {0} / {1}".format(count_opt_traces, len(ELH.log_by_case)))
    #print("STOP!")

    """ \n\n======= ration and numbers ==============="""
    print("Ratio of optimal traces: {0}".format(ELH.get_ratio_optimal_traces(opt_traces)))

    opt_decisions = PE.get_optimal_decisions_notau(opt_traces)
    #print(opt_decisions)
    decisions_distr = {}
    for key in ELH.log_by_case:
        trace = ELH.log_by_case[key]
        ret = ELH.opt_decisions_ratio(trace, opt_decisions)
        if ret[2] == 1.0:
            found = 'TRUE'
        else:
            found = 'false'
        #print("Case {0} ==============\n---Correct decisions: {1}\n---Total decisions: {2}\n---Ratio: {3}\n---Optimal? {4}\n---Incorrect Decisions: {5}".format(key, ret[0], ret[1], ret[2], found, ret[3]))
        incorrect_dec = ret[4]
        #print (incorrect_dec)
        #print("="*25)
        # update distribution of incorrect decisions


        for dec in incorrect_dec:
            if dec not in decisions_distr:
                decisions_distr[dec] = 1
            else:
                decisions_distr[dec] += 1

    # print distribution of incorrect decisions

    for dec in decisions_distr:
        print("Antecedent, frequency: {0}, {1}".format(dec, decisions_distr[dec]))







