'''
Created on Aug 2, 2016

Various useful functions for aco

- random initialisation of utility values for all nodes in a hypergraph

@author: UNIST
'''

from random import uniform
from random import choice
from random import random
from random import randint
from random import sample
from string import ascii_uppercase
import logging
import sys

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only

# sort of 'static' counter to number tau split and join
def counter(init=[0]):
    init[0] += 1
    return init[0]



def randomword(length):
    return ''.join(choice(ascii_uppercase) for i in range(length))



def random_init_attributes(hg):
    '''
    Initialise the attributes cost, qual, avail, and time of a hypergraph
    to random values drawn from a uniform distribution [0,1]
    :param hg: hypergraph
    '''
    nodes = hg.get_node_set()
    for node in nodes:
        cost = uniform(0,1)
        qual = uniform(0,1)
        avail = uniform(0,1)
        time = uniform(0,1)
        attrs = hg.get_node_attributes(node)
        #hg.remove_node(node)
        attrs.update({'cost' : cost})
        attrs.update({'qual' : qual})
        attrs.update({'avail' : avail})
        attrs.update({'time' : time})
        hg.add_node(node, attrs)
    return hg


""" ================================================================= 
random geneation of hypergraphs """

def generate_random_node_attributes():
    node_attrs = {}
    node_attrs['cost'] = uniform(0,1)
    node_attrs['qual'] = uniform(0,1)
    node_attrs['avail'] = uniform(0,1)
    node_attrs['time'] = uniform(0,1)
    node_attrs['type'] = 'transition'
    node_attrs['source'] = False
    node_attrs['sink'] = False
    return node_attrs

def generate_random_node_list(hg, size):
    node_list = []
    for i in range(0, size, 1):
        node = str(counter())
        node_attrs = generate_random_node_attributes()
        hg.add_node(node, node_attrs)
        node_list.append(node)
    return node_list


    
def rewrite_xor_block(hg, node, size):
    
    # create xor block and add edges to to hypergraph
    node_list = generate_random_node_list(hg, size)
    # generate xor split and join
    attrs_xor_split = generate_random_node_attributes()
    attrs_xor_split['type'] = 'xor-split'
    attrs_xor_join = generate_random_node_attributes()
    attrs_xor_join['type'] = 'xor-join'
    xor_split = str(counter())
    xor_join = str(counter())
    hg.add_node(xor_split, attrs_xor_split)
    hg.add_node(xor_join, attrs_xor_join)
    split_list = []
    join_list = []
    split_list.append(xor_split)
    join_list.append(xor_join)
    # create edges for xor block
    edge_attrs = {'phero' : 0.5}
    for _node in node_list:
        node_as_list = []
        node_as_list.append(_node)
        hg.add_hyperedge(split_list, node_as_list, edge_attrs)
        hg.add_hyperedge(node_as_list, join_list, edge_attrs)
    # substitute node with xor split in all edges in the backward star of node
    back_star = hg.get_backward_star(node)
    for b_edge in back_star:
        head = hg.get_hyperedge_head(b_edge)
        tail = hg.get_hyperedge_tail(b_edge)
        head.remove(node)
        head.append(xor_split)
        hg.add_hyperedge(tail, head, edge_attrs)
        hg.remove_hyperedge(b_edge)
    # substitute node with xor join in all edges in the forward star of node
    forw_star = hg.get_forward_star(node)
    for f_edge in forw_star:
        head = hg.get_hyperedge_head(f_edge)
        tail = hg.get_hyperedge_tail(f_edge)
        tail.remove(node)
        tail.append(xor_join)
        hg.add_hyperedge(tail, head, edge_attrs)
        hg.remove_hyperedge(f_edge)
        
    # remove node from hg
    hg.remove_node(node)
    return hg, choice(node_list)
    
def rewrite_and_block(hg, node, size):
    # create and block and add edges to to hypergraph
    node_list = generate_random_node_list(hg, size)
    # generate tau split and join
    attrs_tau_split = generate_random_node_attributes()
    attrs_tau_join = generate_random_node_attributes()
    num = counter()
    tau_split = 'tau split' + str(num)
    tau_join = 'tau join' + str(num)
    hg.add_node(tau_split, attrs_tau_split)
    hg.add_node(tau_join, attrs_tau_join)
    split_list = []
    join_list = []
    split_list.append(tau_split)
    join_list.append(tau_join)
    # create one big hyperedge for parallel of all nodes
    edge_attrs = {'phero' : 0.5}
    node_as_list = []
    for _node in node_list:
        node_as_list.append(_node)
    hg.add_hyperedge(split_list, node_as_list, edge_attrs)
    hg.add_hyperedge(node_as_list, join_list, edge_attrs)
    # substitute node with xor split in all edges in the backward star of node
    back_star = hg.get_backward_star(node)
    for b_edge in back_star:
        head = hg.get_hyperedge_head(b_edge)
        tail = hg.get_hyperedge_tail(b_edge)
        head.remove(node)
        head.append(tau_split)
        hg.add_hyperedge(tail, head, edge_attrs)
        hg.remove_hyperedge(b_edge)
    # substitute node with xor join in all edges in the forward star of node
    forw_star = hg.get_forward_star(node)
    for f_edge in forw_star:
        head = hg.get_hyperedge_head(f_edge)
        tail = hg.get_hyperedge_tail(f_edge)
        tail.remove(node)
        tail.append(tau_join)
        hg.add_hyperedge(tail, head, edge_attrs)
        hg.remove_hyperedge(f_edge)
        
    # remove node from hg
    hg.remove_node(node)
    # return one random node of the new nodes created
    return hg, choice(node_list)
    

def random_generate_hg(level_size, block_size_min, block_size_max):
    '''
    Generate a random hypergraph
    :param level_size: number of rewriting levels (at each level an 'and' or 'xor' block is randomly chosen for rewriting)
    :param block_size: min size of a block (number of branches)
    :param block_size: max size of a block (number of branches)
    '''
    hg = DirectedHypergraph()
    # create source and sink nodes
    source_attrs = generate_random_node_attributes()
    source_attrs['source'] = True
    sink_attrs = generate_random_node_attributes()
    sink_attrs['sink'] = True
    source = 'source'
    hg.add_node(source, source_attrs)
    sink = 'sink'
    hg.add_node(sink, sink_attrs)
    edge_attrs = {'phero' : 0.5}
    source_list = []
    sink_list = []
    source_list.append(source)
    sink_list.append(sink)
    hg.add_hyperedge(source_list, sink_list, edge_attrs)
    
    
    node_start_list = source_list
    node_end_list = sink_list
    
    # add 1 node
    node_middle = generate_random_node_list(hg, 1)
    hg.add_hyperedge(source_list, node_middle, edge_attrs)
    hg.add_hyperedge(node_middle, sink_list, edge_attrs)
    hg.remove_hyperedge(hg.get_hyperedge_id(source_list, sink_list))
    
    #print_hg_std_out_only(hg)
    
    # add one xor block
    #hg = rewrite_xor_block(hg, node_middle[0], 2)[0]
    #hg = rewrite_and_block(hg, node_middle[0], 4)[0]
    
    
    #print_hg_std_out_only(hg)
    
    # generation of test hypergraph
    current_node = node_middle[0]
    
    SIZE = level_size
    for i in range(0, SIZE, 1):
        size = randint(block_size_min, block_size_max)                                # pick size randomly
        if uniform(0,1) > 0.5:                              # make an and block
            out = rewrite_and_block(hg, current_node, size)
            hg, current_node = out[0], out[1]
            
        else:                                               # make a xor block
            out = rewrite_xor_block(hg, current_node, size)
            hg, current_node = out[0], out[1]
    
    #print_hg_std_out_only(hg)
    
    return hg


def is_node_ok_too_loop(hg, node):
    is_ok = True
    # should not start loop in sink, source, or tau split/join
    if 'sink' in node:
        is_ok = False
    if node[0][0:3] == "tau":
        is_ok = False
    if 'source' in node:
        is_ok = False
    return is_ok

def add_random_loops(hg, loops_number, loop_length):
    '''
    Add random loops to hg of varianble length
    :param loops_number: number of loops that will be added
    :param loop_length: average length of loops
    '''
    
    #loop_length = randint(loop_length - 5, loop_length + 5)
    node_set = hg.get_node_set()
    i = 0
    while i < loops_number:
        i += 1
        node1, node2, start_loop_node, end_loop_node = " ", " ", " ", " "
        # pick one random element
        found1, found2 = False, False
        while not found1:
            node1 = sample(node_set, 1)
            found1 = is_node_ok_too_loop(hg, node1)
        while not found2:
            node2 = sample(node_set, 1)
            found2 = is_node_ok_too_loop(hg, node2)
        # TBC TBC should check also that node is not in and hyperedge???
        if node1 != node2:
            if node1 < node2:
                start_loop_node, end_loop_node = node2, node1
            else:
                start_loop_node, end_loop_node = node1, node2
        # insert loop
        current_node = start_loop_node
        edge_attrs = {'phero' : 0.5}
        print("Found nodes for loop: {0}, {1}".format(start_loop_node, end_loop_node))
        for j in range(0, loop_length, 1):
            if j != loop_length -1:                                     # add new node
                new_node = randomword(6)
                new_node_attrs = generate_random_node_attributes()
                hg.add_node(new_node, new_node_attrs)
                hg.add_hyperedge(current_node, new_node, edge_attrs)
                current_node = new_node
                print("current_node: {0}".format(current_node))
            else:                                                       # connect with node1
                hg.add_hyperedge(current_node, end_loop_node, edge_attrs)
    return hg
            
        
    

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    hg = random_generate_hg(2, 2, 3)
    hg = add_random_loops(hg, 2, 2)
    print_hg_std_out_only(hg)
    
