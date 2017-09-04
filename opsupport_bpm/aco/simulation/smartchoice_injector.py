"""
Functions to inject smartchoice options in a hypergraph
"""

from halp.directed_hypergraph import DirectedHypergraph

import random
import logging
import sys

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


    def write_hypergraph_to_file(self, out_file_name):\
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

    def inject_attribute_sc_random(self, node, choice_attr, values):
        """
        :param values: the values that choice_attr can assume
        :return:
        """
        fstar = self.hg.get_forward_star(node)
        list_fstar = list(fstar)
        edge_no = len(fstar)
        values_no = len(values)
        random.shuffle(values)
        options = {}
        if values_no > edge_no:
            # more values of attribute than edges available
            counter = 0
            for i in range(len(values)):
                if counter < edge_no:
                    options[i] = list_fstar[counter]
                    counter += 1
                else:
                    counter = 0
                    options[i] = list_fstar[counter]
        else:
            # more edges than values
            chosen_edges = []
            for i in range(len(values)):
                edge = random.choice(list(fstar))
                while (edge in chosen_edges):
                    edge = random.choice(list(fstar))
                options[i] = edge
                chosen_edges.append(edge)
        # create smacrtchoice at node
        self.hg = smartchoice_attribute(self.hg, node, choice_attr, options)

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

    def print_xorsplits_info(self):
        logger.debug("===!!!=== XOR SPLIT NODES INFO ===!!!=== ")
        xorsplits = self.get_xorsplits()
        for node in xorsplits:
            logger.debug("--- Node: {0}".format(node))
            for edge in self.hg.get_backward_star(node):
                logger.debug("* Backward edge {0} >>> {1}".format(edge, self.hg.get_hyperedge_tail(edge)))
            for edge in self.hg.get_forward_star(node):
                logger.debug("* Forward edge {0} >>> {1}".format(edge, self.hg.get_hyperedge_head(edge)))
        logger.debug("===!!!=== ==================== ===!!!=== ")

    """ Some initialiser of smartchoice (e.g., picked random, all nodes in the same way)"""

    """ 1) nodes chosen with probability prob initialised using node_sc_random"""
    def init_hg_node_sc_random(self, prob):
        logger.debug("Initilalising hg with random node_smartchoice...")
        xorsplits = self.get_xorsplits()
        for node in xorsplits:
            logger.debug("Analysing node: {0}".format(node))
            if random.random() <= prob:
                logger.debug("Injecting node_smartchoice at node: {0}".format(node))
                self.inject_node_sc_random(node)

    """ 2) nodes chosen with probability prob initialised using attribute_sc_random"""
    def init_hg_attribute_sc_random(self, prob, choice_attr, values):
        logger.debug("Initilalising hg with random attribute_smartchoice...")
        xorsplits = self.get_xorsplits()
        for node in xorsplits:
            logger.debug("Analysing node: {0}".format(node))
            if random.random() <= prob:
                logger.debug("Injecting attribute_smartchoice at node: {0}".format(node))
                self.inject_attribute_sc_random(node, choice_attr, values)

    """ 3) nodes chosen with probability prob initialised using either node_ or attribute_sc_random """
    def init_hg_random(self, prob, choice_attr, values):
        logger.debug("Initilalising hg with random node/attribute_smartchoice...")
        xorsplits = self.get_xorsplits()
        for node in xorsplits:
            logger.debug("Analysing node: {0}".format(node))
            if random.random() <= prob:
                if random.random() <= 0.5:
                    logger.debug("Injecting node_smartchoice at node: {0}".format(node))
                    self.inject_node_sc_random(node)
                else:
                    logger.debug("Injecting attribute_smartchoice at node: {0}".format(node))
                    self.inject_attribute_sc_random(node, choice_attr, values)

""" MAIN """
if __name__ == "__main__":
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    logger = logging.getLogger(__name__)



    file_name = "C://opsupport_bpm_files/eval/input_files/road_fine_process.hgr"

    SCI = SmartChoiceInjector(file_name)

    logger.debug("Number of XOR nodes: {0}".format(len(SCI.get_xorsplits())))

    #SCI.init_hg_node_sc_random(0.9)
    SCI.init_hg_attribute_sc_random(0.9,'patient_type',[0,1,2,3,4,5])


    #xorsplits = SCI.get_xorsplits()
    #print(xorsplits)

    #for node in xorsplits:
        #SCI.inject_node_sc_random(node)
        #SCI.inject_attribute_sc_random(node,'attribute', [0,1])

    file_out = "C://opsupport_bpm_files/eval/input_files/output_injected.hgr"
    SCI.print_xorsplits_info()
    SCI.write_hypergraph_to_file(file_out)