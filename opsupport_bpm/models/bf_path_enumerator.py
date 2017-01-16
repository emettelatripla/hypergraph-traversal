

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_nonrec
from opsupport_bpm.models.hypergraph import reset_pheromone

import random

class Node:
    def __init__(self):
        self.data = []
    def add_activity(self, act_name):
        self.data.append(act_name)
    def print_node(self, level):
        for act in self.data:
            if type(act) is not str:
                act.print_node(level + 1)
            else:
                print("..."*level +act)



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
        self.explore(hypertree, start_node, end_node)
        return hypertree.data

    def explore(self, tree, node_start, node_end):
        current_node = node_start

        while current_node != node_end:
            if current_node[:9] == "tau split":
                id = current_node[9]
                tree.data.append(current_node)

                next_nodes = self.opt_hgr.get_hyperedge_head(list(self.opt_hgr.get_forward_star(current_node))[0])
                for node in next_nodes:
                    new_block = Node()
                    tree.data.append(new_block)
                    end_node = "tau join"+id
                    self.explore(new_block, node, end_node)
                current_node = end_node
            else:
                tree.data.append(current_node)
                next_edge = list(self.opt_hgr.get_forward_star(current_node))[0]
                next_node = list(self.opt_hgr.get_hyperedge_head(next_edge))[0]
                current_node = next_node

        tree.data.append(current_node)
        # take care of last node

    def enumerate_paths(self, tree, num_ants, index):
        paths = {}
        start_node = tree.data[0]
        end_node = tree.data[len(tree.data)-1]
        for i in range(num_ants):
            paths[i] = []
            index, data_index = 0, 0
            self.ant_walk(tree.data, paths[i], index, 0, start_node, end_node)
        return paths


    def ant_walk(self, data, path, index, data_index, start_node, end_node):
        current_node = start_node
        while current_node != end_node:
            if current_node[:9] == "tau split":
                id = current_node[9]
                this_node = current_node
                path_temp = []
                while (type(this_node) is not str) or (this_node[:9] != "tau join"):
                    path_temp.append(this_node)
                    data_index += 1
                    this_node = data[data_index]
                path_temp.pop(0)
                path_temp.pop(len(path_temp)-1)
                next = random.choice[path_temp]
                self.ant_walk(next.data, path, index, data_index, current_node, "tau join"+id)
            elif type(current_node) is not str:
                data_index += 1
                current_node = data[data_index]
                pass
            else:
                path.insert(index,current_node)
                index += 1
                data_index += 1
                current_node = data[data_index]


if __name__ == '__main__':
    tree = Node()
    print(type(tree))
    PE = BF_PathEnumerator("popt.hgr")
    print(PE.get_hyperpath_tree(tree))
    #tree.print_node(1)
    paths = PE.enumerate_paths(tree,20, 0)


