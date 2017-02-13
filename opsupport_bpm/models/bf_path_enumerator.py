

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_nonrec
from opsupport_bpm.models.hypergraph import reset_pheromone

import random
from itertools import permutations, combinations
import sys
import logging
import re

class Node:
    def __init__(self):
        self.data = []
        self.parent = None
        self.children = []
        self.level = 0
        self.is_merge = False
    def set_level(self,l):
        self.level = l
    def set_parent(self, parent):
        self.parent = parent
    def is_leaf(self):
        return self.children == [] or self.is_merge
    def set_children(self):
        for d in self.data:
            if type(d) is not str:
                self.children.append(d)
    def add_activity(self, act_name):
        self.data.append(act_name)
    def print_node(self, level):
        for act in self.data:
            if type(act) is not str:
                act.print_node(level + 1)
            else:
                print("..."*level +act+" "+str(self.level))

    def adjust_trace_tau_split(self):
        if self.data[len(self.data)-1][:8] == "tau join":
            id = self.data[len(self.data)-1][8]
            tau_split = "tau split"+id
            self.data.insert(0,tau_split)
    def adjust_tau_split(self):
        if self.children == []:
            self.adjust_trace_tau_split()
        else:
            for child in self.children:
                child.adjust_tau_split()
            self.adjust_trace_tau_split()


    def make_lists(self):
        if self.children == []:
             l = []
             l.append(self.data)
             self.data = l
        else:
            for child in self.children:
                child.make_lists ()
            l = []
            l.append (self.data)
            self.data = l
            # if self.parent == None:
            #     l = []
            #     l.append(self.data)
            #     self.data = l





class BF_PathEnumerator():

    def __init__(self):
        self.path = None
        self.path_file = None
        self.opt_hgr = None
        self.tree = Node()

    def __init__(self, file_name):
        self.path = None
        self.path_file = file_name
        self.opt_hgr = self.read_hgr(file_name)
        self.tree = Node ()

    def read_hgr(self, file_name):
        hg = read_hg_from_file(file_name)
        return hg


    def get_hyperpath_tree(self, hypertree):
        node_set = self.opt_hgr.get_node_set()
        # start from source node
        start_node, end_node = None, None
        for node in node_set:
            if self.opt_hgr.get_node_attribute(node, 'source') == True:
                start_node = node
            if self.opt_hgr.get_node_attribute(node, 'sink') == True:
                end_node = node
        #hypertree = Node()
        self._explore(hypertree, start_node, end_node)
        return hypertree

    def _explore(self, tree, node_start, node_end):
        current_node = node_start

        while current_node != node_end:
            if current_node[:9] == "tau split":
                id = current_node[9]
                tree.data.append(current_node)

                next_nodes = self.opt_hgr.get_hyperedge_head(list(self.opt_hgr.get_forward_star(current_node))[0])
                #next_nodes.insert(0,current_node)
                for node in next_nodes:
                    new_block = Node()
                    new_block.set_parent(tree)
                    new_block.set_level(new_block.parent.level + 1)
                    tree.data.append(new_block)
                    #start_node = "tau split"+id
                    end_node = "tau join"+id
                    #self.explore (new_block, start_node, end_node)
                    self._explore(new_block, node, end_node)
                current_node = end_node
            else:
                tree.data.append(current_node)
                next_edge = list(self.opt_hgr.get_forward_star(current_node))[0]
                next_node = list(self.opt_hgr.get_hyperedge_head(next_edge))[0]
                current_node = next_node

        tree.data.append(current_node)
        # take care of last node

    def prepare_tree_for_trace_enumeration(self):
        """
        some makeup before trace enumeration:
        :return:
        """
        self.tree.set_children ()       # set links to children
        self.tree.adjust_tau_split ()   # add tau split activity in front of all children
        self.tree.make_lists ()         # make all traces as "lists of lists"


    """" METHODS FOR EXTRACTING traces from optimal path (START)"""


    def _vertical_merge(self, data_parent, data_down_list):
        """
        does teh vertical merge step: tested!
        :param data_up: a list with tau split/join
        :param data_down: a "leaf" list (that is, without tau split/join)
        :return:
        """
        merge = []
        data_up = data_parent[0]
        # get all the prmutations of data_down
        for data_down in data_down_list:
            perm_down = permutations(data_down)

            # find the sublist between tau split/join in data_up
            for value in data_up:
                if type(value) is str:
                    if value[0:9] == "tau split":
                        sublist_start = data_up.index(value)+1
                    if value[0:8] == "tau join":
                        sublist_end = data_up.index(value)-1

                # do the merge (create list of lists)

            data_up[sublist_start:sublist_end+1] = next(perm_down)
            copy = self._deep_copy(data_up)
            merge.append(copy)

            for perm in perm_down:
                data_up[sublist_start:sublist_start+len(perm)] = perm
                copy = self._deep_copy(data_up)
                merge.append(copy)

        return merge

    def _vertical_substitution(self, hypertree, data_down_list):
        """
        does teh vertical merge step: tested!
        :param data_up: a list with tau split/join
        :param data_down: a "leaf" list (that is, without tau split/join)
        :return:
        """
        data_parent = hypertree.data
        merge = []
        data_up = data_parent[0]
        # get all the prmutations of data_down
        for data_down in data_down_list:
            #perm_down = permutations(data_down)

            #xxx = next(perm_down)

            # find the sublist between tau split/join in data_up
            for value in data_up:
                if type(value) is str:
                    if value[0:9] == "tau split":
                        sublist_start = data_up.index(value)+1
                    if value[0:8] == "tau join":
                        sublist_end = data_up.index(value)-1

                # do the merge (create list of lists)

            data_up[sublist_start:sublist_end+1] = data_down[1:-1]
            copy = self._deep_copy(data_up)
            merge.append(copy)

            # for perm in perm_down:
            #     data_up[sublist_start:sublist_start+len(perm)] = perm
            #     copy = self.deep_copy(data_up)
            #     merge.append(copy)
        # remove the children of hypertree
        hypertree.children = []
        hypertree.data = merge

        return merge



    def _deep_copy(self, lst):
        new = []
        for l in lst:
            new.append(l)
        return new


    def _horizontal_merge(self, a, b):
        #b = b[1:-1]
        logger = logging.getLogger(__name__)
        logger.debug("H-merge: {0} === {1}".format(a,b))

        result = []
        for lst1 in a:
            copy_lst1 = self._deep_copy(lst1)
            del copy_lst1 [0]
            del copy_lst1 [-1]
            for lst2 in b:
                copy_lst2 = self._deep_copy(lst2)
                del copy_lst2 [0]
                del copy_lst2 [-1]
                result += self._combine(copy_lst1, copy_lst2)

        return result

    def _combine(self, xs, ys):
        logger = logging.getLogger(__name__)
        logger.debug ("Combine: {0} === {1}".format (xs, ys))
        if xs == []: return [ys]
        if ys == []: return [xs]
        x, *xs_tail = xs
        y, *ys_tail = ys
        return [[x] + l for l in self._combine(xs_tail, ys)] + \
               [[y] + l for l in self._combine(ys_tail, xs)]


    def _get_traces(self, hypertree):
        """
        Does the traversal of the tree to get all possible traces (doing vertical/horizontal merge as needed)

        The main skeleton is here.
        However, we need to check for data as list or list of lists (horizontal/vertical integration has to work in all cases)
        :return:
        """
        traces = []
        children = hypertree.children
        ALL_LEAVES = True
        for child in children:
            if child.is_leaf() == False:
                ALL_LEAVES = False
        if ALL_LEAVES:
            # horizontal merge pair by pair

            child_num = len(children)
            i = 0
            res = children[i].data
            while i < len(children) - 1:
                # make a copy
                copy_res = []
                for r in res:
                    copy_res.append(r)
                res = self._horizontal_merge(copy_res, children[i + 1].data)
                j = 0
                while j < len(res):
                    res[j].insert (0, "tau split0")
                    res[j].append("tau join0")
                    j += 1
                i += 1
                # vertical substitution

            self._vertical_substitution(hypertree, res)
            if hypertree.parent != None:
                PE._get_traces(hypertree.parent)

        #return traces


    def actlist_from_traces(self, traces):
        traces_copy = []
        for trace in traces:
            trace_copy = []
            for event in trace:
                is_n = re.search('n([0-9]+)', event)
                is_tau = re.search('tau ', event)
                if is_n is None and is_tau is None:
                    trace_copy.append(event)

            traces_copy.append(trace_copy)
        return traces_copy

    """" METHODS FOR EXTRACTING traces from optimal path (END)"""

    """" METHODS FOR EXTRACTING DECISIONS from optimal path (START)"""

    def _get_optimal_decisions(self):
        """
        Returns the list of decisions in the optimal path in a dictionary of the type (includes tau transitions)
        {1: {'antec' : 'Activity_A', 'conseq' : 'ActivityB'} }
        :return:
        """
        node_set = self.opt_hgr.get_node_set()
        dec_count = 0
        decisions = {}
        for node in node_set:
            if self.opt_hgr.get_node_attribute(node, 'type') == 'xor-split':
                antec = list(self.opt_hgr.get_hyperedge_tail(list(self.opt_hgr.get_backward_star(node))[0]))[0]
                conseq =  list(self.opt_hgr.get_hyperedge_head(list(self.opt_hgr.get_forward_star(node))[0]))[0]
                decisions[dec_count] = {'antec' : antec, 'conseq' : conseq}
                dec_count += 1
        return decisions

    def get_optimal_decisions_notau(self, opt_traces):
        """
        picks the list of decisions (with tau transitions) and checks in the list of optimal traces how this decisions may look like
        :return: the list of decisions in the optimal path involving only activities (no tau transitions)
        """
        opt_tau_decisions = self._get_optimal_decisions()
        opt_decisions = {}
        for key in opt_tau_decisions:
            antec = opt_tau_decisions[key]['antec']
            conseq = opt_tau_decisions[key]['conseq']
            is_antec_tau = re.search('tau from tree', antec)
            is_conseq_tau = re.search('tau from tree', conseq)
            if is_antec_tau is not None:
                for opt_trace in opt_traces:
                    possible_antecs = []
                    for i in range(len(opt_trace)-1):
                        if opt_trace[i+1] == conseq:
                            possible_antecs.append(opt_trace[i])
                # create entry in dictionary
                opt_decisions[key] = {'antec': possible_antecs , 'conseq' : [conseq]}
            elif is_conseq_tau is not None:
                for opt_trace in opt_traces:
                    possible_conseqs = []
                    for i in range(1,len(opt_trace)):
                        if opt_trace[i-1] == antec:
                            possible_conseqs.append(opt_trace[i])
                # create entry in dictionary
                opt_decisions[key] = {'antec': [antec] , 'conseq' : possible_conseqs}
            else:
                opt_decisions[key] = {'antec': [antec], 'conseq': [conseq]}

        self._reduce_duplicate_opt_dec(opt_decisions)
        return opt_decisions

    def _reduce_duplicate_opt_dec(self, opt_decisions):
        """
        Deletes duplicate optimal decisions (because collapsed when removing taus)
        :param opt_decisions:
        :return:
        """
        keys_to_del, checked_keys = [], []
        for key in opt_decisions:
            for key2 in opt_decisions:
                if opt_decisions[key] == opt_decisions[key2] and key2 not in keys_to_del and key2 not in checked_keys and key != key2:
                    keys_to_del.append(key2)
            checked_keys.append(key)
        # delete duplicate keys
        for key in keys_to_del:
            del opt_decisions[key]
        return opt_decisions

    """" METHODS FOR EXTRACTING DECISIONS from optimal path (END)"""





if __name__ == '__main__':

    m = re.search('n([0-9]+)', 'n456' )
    n = re.search('n([0-9]+)', 'yuy456 ioio')
    print(m.group(0))
    if n is None:
        print("No match")

    log = logging.getLogger ('')
    log.setLevel (logging.WARNING)
    format = logging.Formatter ("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler (sys.stdout)
    ch.setFormatter (format)
    log.addHandler (ch)

    logger = logging.getLogger (__name__)

    PE = BF_PathEnumerator("popt.hgr")

    #tree = Node()
    PE.get_hyperpath_tree(PE.tree)
    PE.prepare_tree_for_trace_enumeration()
    print(PE.tree.data)
    for child in PE.tree.children:
        print(child.data)



    """ Create sample tree """

    Y = [ "a", "b", "c", "tau join0"]
    Z = [ "x", "y", "z", "tau join0"]
    W = [ "l", "m", "n", "tau join0"]

    child1 = Node()
    child1.data = Y
    child2 = Node ()
    child2.data = Z
    child3 = Node()
    child3.data = W
    X = ["1", "tau split0", child1, child2, child3, "tau join0", "2", "3"]
    parent = Node ()
    parent.data = X

    #parent.set_children()
    child1.parent = parent
    child2.parent = parent
    child3.parent = parent


    # PE.tree = parent
    # PE.prepare_tree_for_trace_enumeration()
    # #parent.make_lists()
    #
    # print(PE.tree.data)
    # print(PE.tree.children[0].data)
    # print(PE.tree.children[1].data)
    # print (PE.tree.children[2].data)
    # result = PE.horizontal_merge(PE.tree.children[0].data,PE.tree.children[1].data)
    # for r in result:
    #     r.insert (0, "tau split0")
    #     r.insert(len(result),"tau join0")
    #     print(r)
    #
    # print("\n\n=====  SECOND MERGE ================================")
    # result2 = PE.horizontal_merge(result,PE.tree.children[2].data)
    # for r in result2:
    #     r.insert (0, "tau split0")
    #     r.insert (len (result), "tau join0")
    #     print (r)

    """ end create sample tree """
    print("\n\n=========== HORIZONTAL MERGE =============================")
    # result = PE.horizontal_merge (parent.children[0].data, parent.children[1].data)
    # for r in result:
    #     print(r)
    print ("\n\n=========== VERTICAL MERGE =============================")
    # result = PE.vertical_substitution(parent.data,parent.children[0].data)
    # for r in result:
    #     print(r)

    """ test vertical/horizontal integration"""


    """ enumerate all possible paths """
    # print("\n\n ================ ALL TRACES ===================================")
    PE._get_traces(PE.tree)
    print("Number of traces: {0}".format(len(PE.tree.data)))
    # for t in PE.tree.data:
    #     print(t)

    print("\n\n ================ ALL TRACES (NO GATEWAYS)=======================")
    traces_act = PE.actlist_from_traces(PE.tree.data)
    print("Number of traces: {0}".format(len(traces_act)))
    for t in traces_act:
        print(t)


    print("\n\n ================ TEST DECISIONS =======================")

    decisions = PE._get_optimal_decisions()
    for key in decisions:
        print("{2} : {0} : {1}".format(decisions[key]['antec'], decisions[key]['conseq'], key))

    print("\n\n OPT DECISIONS NO TAU ================================== (note some decision's will collapse!! =====")

    decisions_notau = PE.get_optimal_decisions_notau(traces_act)
    for key in decisions_notau:
        print("{2} : {0} : {1}".format(decisions_notau[key]['antec'], decisions_notau[key]['conseq'], key))
