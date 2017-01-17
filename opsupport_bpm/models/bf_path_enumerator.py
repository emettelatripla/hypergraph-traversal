

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_nonrec
from opsupport_bpm.models.hypergraph import reset_pheromone

import random
from itertools import permutations, combinations


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
        return hypertree

    def explore(self, tree, node_start, node_end):
        current_node = node_start

        while current_node != node_end:
            if current_node[:9] == "tau split":
                id = current_node[9]
                tree.data.append(current_node)

                next_nodes = self.opt_hgr.get_hyperedge_head(list(self.opt_hgr.get_forward_star(current_node))[0])
                for node in next_nodes:
                    new_block = Node()
                    new_block.set_parent(tree)
                    new_block.set_level(new_block.parent.level + 1)
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



    def vertical_merge(self, data_up, data_down):
        """
        does teh vertical merge step: tested!
        :param data_up: a list with tau split/join
        :param data_down: a "leaf" list (that is, without tau split/join)
        :return:
        """
        # get all the prmutations of data_down
        perm_down = permutations(data_down)

        # find the sublist between tau split/join in data_up
        for value in data_up:
            if value[0:9] == "tau split":
                sublist_start = data_up.index(value)
            if value[0:8] == "tau join":
                sublist_end = data_up.index(value)

        # do the merge (create list of lists)
        merge = []
        data_up[sublist_start:sublist_end+1] = next(perm_down)
        copy = self.deep_copy(data_up)
        merge.append(copy)

        for perm in perm_down:
            data_up[sublist_start:sublist_start+len(perm)] = perm
            copy = self.deep_copy(data_up)
            merge.append(copy)


        return merge



    def deep_copy(self, lst):
        new = []
        for l in lst:
            new.append(l)
        return new


    def horizontal_merge(self, a, b):
        result = []
        for lst1 in a:
            for lst2 in b:
                result += self.combine(lst1,lst2)
        return result

    def combine(self, xs, ys):
        if xs == []: return [ys]
        if ys == []: return [xs]
        x, *xs_tail = xs
        y, *ys_tail = ys
        return [[x] + l for l in self.combine(xs_tail, ys)] + \
               [[y] + l for l in self.combine(ys_tail, xs)]


    def get_traces(self, hypertree):
        """
        Does the traversal of the tree to get all possible traces (doing vertical/horizontal merge as needed)

        The main skeleton is here.
        However, we need to check for data as list or list of lists (horizontal/vertical integration has to work in all cases)
        :return:
        """
        traces = []
        if hypertree.is_leaf():
            if hypertree.parent == None:
                traces.append(hypertree.data)
            else:
                # merge with parent
                self.vertical_merge(hypertree.parent.data, hypertree.data)
        else:
            # check if all children are leaves
            children = hypertree.children
            ALL_CHILD = True
            for child in children:
                if child.is_leaf() != True:
                    ALL_CHILD = False
            if ALL_CHILD:
                # do horizontal merge of all chidlren
                # substitute parent with merge
                pass
            else:
                # recursive call on all children
                pass


        pass




if __name__ == '__main__':

    PE = BF_PathEnumerator("popt.hgr")

    # X = ["xxx","tau split0", "0123","0124", "tau join0", "pppp","zzzz"]
    # Y = ["a", "b", "k"]
    #

    #
    # v_merge = PE.vertical_merge(X,Y)
    # print("========== Vertical merge =============")
    # print(v_merge)
    #
    # Z = [["d","e"]]
    #
    # input()
    # print("========= Horizontal merge =============")
    #
    # res = PE.horizontal_merge(v_merge, Z)
    # print(res)
    # print(len(res))









    PE = BF_PathEnumerator("popt.hgr")

    tree = Node()
    tree.set_parent(None)
    print(PE.get_hyperpath_tree(tree))

    print(tree.parent)
    tree.set_children()
    print(tree.is_leaf())
    print(tree.children)
    for child in tree.children:
        print(child.data)
        print(child.is_leaf())

    #print("========== PRINT TREE ================")
    #tree.print_node(1)


