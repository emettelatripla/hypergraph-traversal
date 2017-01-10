import csv
import json

from halp.directed_hypergraph import DirectedHypergraph

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

    def set_optimal_path(self, hg:DirectedHypergraph):
        self.opt_path = hg

    def get_optimal_activity_list(self):
        node_set = self.opt_path.get_node_set()
        act_list = []
        for node in node_set:
            if self.opt_path.get_node_attribute(node, 'type') is not 'xor-join' or self.opt_path.get_node_attribute(node, 'type') is not 'xor-split':
                act_list.append(str(node))
        return act_list


    def get_case_act_matching(self, case_id):
        trace = self.get_trace(case_id)
        opt_act = self.get_optimal_activity_list()
        counter = 0
        for act in trace:
            if act in opt_act:
                counter += 1
        return counter / len(opt_act)

    def get_case_dec_matching(self, case_id):
        pass




if __name__ == '__main__':

    csvfile_name = "C://opsupport_bpm_files/event_logs/PurchasingExample.csv"
    fieldnames = ('Case_id', 't_start', 't_end', 'activity', 'resource', 'role')
    ELH = EventLogHandler("PurchaseExample", csvfile_name,fieldnames)

    ELH.dump_json_to_file(ELH.log_name+".json")
    ELH.create_log_by_case()
    ELH.print_log_by_case()

    print(ELH.get_trace("391"))
    print(ELH.get_trace("889"))
    print(ELH.get_trace("692"))

