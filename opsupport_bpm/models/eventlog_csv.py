import csv
import json

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

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

    def get_optimal_node_list(self):
        """
        Returns the list of transitions in the optimal path (excluding: (i) tau silent transitions and (ii) xor splits/join
        TODO: ACTIVITIES MUST BE ORDERED
        :return:
        """
        # get start
        node_start = None
        node_set = self.opt_path.get_node_set()
        act_list = []
        index = 0
        for node in node_set:
            if self.opt_path.get_node_attribute(node,'source'):
                node_start = node
        current_node = node_start
        while self.opt_path.get_node_attribute(current_node, 'sink') == False:
            act_list.insert(index, current_node)
            index += 1
            next_edge = list(self.opt_path.get_forward_star(current_node))[0]
            current_node = list(self.opt_path.get_hyperedge_head(next_edge))[0]
        act_list.insert(index,current_node)


        return act_list

    def get_optimal_activity_list(self):
        act_list = self.get_optimal_node_list()
        node_set = self.opt_path.get_node_set()
        for node in node_set:
             if node[:4] == "tau ":
                act_list.remove(str(node))
             if self.opt_path.get_node_attribute(node, 'type') == 'xor-join':
                act_list.remove(str(node))
             if self.opt_path.get_node_attribute(node, 'type') == 'xor-split':
                act_list.remove(str(node))
        return act_list


    def get_optimal_decisions(self):
        """
        Returns the list of decisions in the optimal path in a dictionary of the type
        {1: {'antec' : 'Activity_A', 'conseq' : 'ActivityB'} }
        :return:
        """
        node_set = self.opt_path.get_node_set()
        dec_count = 0
        decisions = {}
        for node in node_set:
            if self.opt_path.get_node_attribute(node, 'type') == 'xor-split':
                antec = list(self.opt_path.get_hyperedge_tail(list(self.opt_path.get_backward_star(node))[0]))[0]
                conseq =  list(self.opt_path.get_hyperedge_head(list(self.opt_path.get_forward_star(node))[0]))[0]
                decisions[node] = {'antec' : antec, 'conseq' : conseq}
                dec_count += 1
        return decisions


    def get_case_act_matching(self, case_id):
        """
        Returns the activity matching with the optimal case. It is adjusted for LOOPS!
        :param case_id:
        :return:
        """
        trace = self.get_trace(case_id)
        opt_act = self.get_optimal_activity_list()
        # adjust for loops: count duplicates
        trace_count = dict(Counter(trace))
        den = 0
        for key in trace_count:
            if key in opt_act:
                den += 1 / trace_count[key]
        return den / len(opt_act)

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





if __name__ == '__main__':

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

    print("OPTIMAL PATH NODE LIST    : {0}".format(ELH.get_optimal_node_list()))
    print("OPTIMAL PATH ACTIVITY LIST: {0}".format(ELH.get_optimal_activity_list()))

    #for key in ELH.log_by_case:
    #    print("Case {0}, optimal path activity matching: {1}".format(key,ELH.get_case_act_matching(key)))

    print(ELH.get_case_act_matching("122"))
    print(ELH.get_case_act_matching("720"))
    #print(ELH.get_case_act_matching("40"))
    #print(ELH.get_case_act_matching("49"))
    #print(ELH.get_case_act_matching("294"))

    print(ELH.get_optimal_decisions())
    print(ELH.get_all_decisions())

    print(ELH.get_trace("122"))
    print(ELH.get_case_dec_matching("122"))

    print(ELH.get_trace("720"))
    print(ELH.get_case_dec_matching("720"))

    #print(ELH.get_case_dec_matching("40"))
    #print(ELH.get_case_dec_matching("49"))
    #print(ELH.get_case_dec_matching("294"))
