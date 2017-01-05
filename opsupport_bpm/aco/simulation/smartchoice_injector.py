"""
Functions to inject smartchoice options in a hypergraph
"""

from halp.directed_hypergraph import DirectedHypergraph

import random

from opsupport_bpm.util.print_hypergraph import read_hg_from_file, write_hg_to_file
from opsupport_bpm.models.hypergraph import smartchoice_service, smartchoice_node, smartchoice_attribute

class SmartChoiceInjector():

    def __init__(self):
        self.hg = None

    def __init__(self, hg:DirectedHypergraph):
        """
        Initialise with hyeprgraph object
        :param hg:
        """
        self.hg = hg

    def __init__(self, file_name):
        """
        initialise with hgr file
        :param file_name:
        """
        self.file_name = file_name
        self.hg = self.get_hypergraph_from_hgr_file(self.file_name)

    def get_hypergraph_from_hgr_file(self, file_name):
        """
        returns a hypergraph by reading it in a .hgr file
        :param file_name:
        :return:
        """
        self.renumber_edges()                        # renumber sequentially edges in hgr file
        return read_hg_from_file(self.file_name)


    def renumber_edges(self):
        """
        This functions changes the edges numbering in the a hgr file to make it sequential
        :param file_name:
        :return:
        """
        file = open (self.file_name, 'r')
        content = file.readlines()
        edge_count = 0                                          # initialise edge counter
        new_content = ""
        # build new file content by numbering edges progressively
        for line in content:
            values = line.split('\t')
            line_copy = ""
            if values[0] == "edge":
                edge_count += 1
                edge_id = "e" + str(edge_count)
                values[1] = edge_id
                line_copy = values[0] + "\t" + values[1] + "\t" + values[2]
                new_content += line_copy
            else:
                new_content += line
        file.close()
        # write the new content on file
        file = open(self.file_name, "w")
        file.write(new_content)
        file.close()


    def write_hypergraph_to_file(self, out_file_name):
        write_hg_to_file(self.hg, out_file_name)

    def switch_on_smartchoice(self):
        """
        Set the smartchoice option to TRUE for all nodes in a hypergraph
        :param hg:
        :return:
        """
        for node in self.hg.get_node_set():
            attrs = self.hg.get_node_attributes(node)
            attrs['smartchoice'] = True
            self.hg.add_node(node, attrs)

    def switch_off_smartchoice(self):
        """
        Set the smartchoice option to FALSE for all nodes in a hypergraph
        :param hg:
        :return:
        """
        for node in self.hg.get_node_set():
            attrs = self.hg.get_node_attributes(node)
            attrs['smartchoice'] = False
            self.hg.add_node(node, attrs)

    def inject_attribute_sc_random(self, node):
        """

        :param hg:
        :param node:
        :return:
        """
        pass

    def inject_node_sc_random(self, node):
        """

        :param hg:
        :param node:
        :return:
        """
        fstar = self.hg.get_forward_star(node)                          # get the node forward star
        prob_values, sum = [], 0
        for edge in fstar:
            prob_value = random.random()
            sum += prob_value
            prob_values.append(prob_value)
        new_prob_values = [value / sum for value in prob_values]

        edge_probabilities = dict(zip(fstar,new_prob_values))
        self.hg = smartchoice_node(self.hg, node, edge_probabilities)

    def inject_service_smartchoice(self, node):
        """

        :param hg:
        :param node:
        :return:
        """
        pass

    def get_xorsplits(self):
        """
        return the list of xorsplits in a hypergraph
        :param hg:
        :return:
        """
        node_list = []
        for node in self.hg.get_node_set():
            if self.hg.get_node_attribute(node,'type') == 'xor-split':
                node_list.append(node)
        return node_list

    """ TODO: some initialiser of smartchoice (e.g., picked random, all nodes in the same way)"""


""" MAIN """
if __name__ == "__main__":

    file_name = "C://opsupport_bpm_files/eval/input_files/test.hgr"

    SCI = SmartChoiceInjector(file_name)

    xorsplits = SCI.get_xorsplits()
    print(xorsplits)

    for node in xorsplits:
        SCI.inject_node_sc_random(node)

    file_out = "C://opsupport_bpm_files/eval/input_files/output.hgr"
    SCI.write_hypergraph_to_file(file_out)