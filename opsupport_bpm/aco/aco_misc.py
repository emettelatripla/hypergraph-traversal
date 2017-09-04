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
import copy

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
    """
    Rewrite a node with a xor_block of a certain size
    :param hg: the hypergraph
    :param node: the node to be rewritten
    :param size: the size of the block that rewrits node
    :return: hg, one of the newly generate nodes randomly chosen
    """
    # create xor block and add edges to to hypergraph
    node_list = generate_random_node_list(hg, size)
    # generate xor split and join
    attrs_xor_split = generate_random_node_attributes()
    attrs_xor_split['type'] = 'xor-split'
    attrs_xor_join = generate_random_node_attributes()
    attrs_xor_join['type'] = 'xor-join'
    num = str(counter())
    xor_split = 'xor-s ' + num
    xor_join = 'xor-j ' + num
    hg.add_node(xor_split, attrs_xor_split)
    hg.add_node(xor_join, attrs_xor_join)
    split_list = []
    join_list = []
    split_list.append(xor_split)
    join_list.append(xor_join)
    # create edges for xor block
    edge_attrs = {'phero' : 100}
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
    """
    Rewrite a node with a and block of a certain size
    :param hg: the hypergraph
    :param node: the node to be rewritten
    :param size: the size of the block that rewrits node
    :return: hg, one of the newly generate nodes randomly chosen
    """
    # create and block and add edges to to hypergraph
    node_list = generate_random_node_list(hg, size)
    # generate tau split and join
    attrs_tau_split = generate_random_node_attributes()
    attrs_tau_join = generate_random_node_attributes()
    num = counter()
    tau_split = 'tauspli ' + str(num)
    tau_join = 'taujoin ' + str(num)
    hg.add_node(tau_split, attrs_tau_split)
    hg.add_node(tau_join, attrs_tau_join)
    split_list = []
    join_list = []
    split_list.append(tau_split)
    join_list.append(tau_join)
    # create one big hyperedge for parallel of all nodes
    edge_attrs = {'phero' : 100}
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
    

def random_generate_hg_BF(level_size, block_size_min, block_size_max):
    '''
    Generate a random hypergraph with only BF-paths
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
    edge_attrs = {'phero' : 100}
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


""" FUNCTIONS FOR non-BF random hypergraph generator """

def rewrite_and_block_nonBF(hg, node, size):
    """
    Rewrite a node with a and block of a certain size
    :param hg: the hypergraph
    :param node: the node to be rewritten
    :param size: the size of the block that rewrits node
    :return: hg, one of the newly generate nodes randomly chosen
    """
    # create and block and add edges to to hypergraph
    node_list = generate_random_node_list(hg, size)
    # generate tau split and join
    attrs_tau_split = generate_random_node_attributes()
    attrs_tau_join = generate_random_node_attributes()
    num = counter()
    tau_split = 'tauspli ' + str(num)
    tau_join = 'taujoin ' + str(num)
    hg.add_node(tau_split, attrs_tau_split)
    hg.add_node(tau_join, attrs_tau_join)
    split_list = []
    join_list = []
    split_list.append(tau_split)
    join_list.append(tau_join)
    # create one big hyperedge for parallel of all nodes
    edge_attrs = {'phero': 100}
    node_as_list = []
    for _node in node_list:
        node_as_list.append(_node)
    # REMOVE ONE ELEMENT FROM LIST as HEAD and TAIL
    random_pick = sample(node_as_list, 2)
    remove_tail, remove_head = random_pick[0], random_pick[1]

    node_as_list_tail = copy.deepcopy(node_as_list)
    node_as_list_tail.remove(remove_tail)

    node_as_list_head = copy.deepcopy(node_as_list)
    node_as_list_head.remove(remove_head)

    hg.add_hyperedge(split_list, node_as_list_head, edge_attrs)
    hg.add_hyperedge(node_as_list_tail, join_list, edge_attrs)
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
    # return one random node in the intersection of head and tail
    return hg, choice(list(set(node_as_list_head) & set(node_as_list_tail)))


def random_generate_hg_nonBF(level_size, block_size_min, block_size_max):
    """
    Generate a random graph for searching B-, F-, B+F paths. 
    :param level_size: 
    :param block_size: 
    :param block_size_max: 
    :return: 
    """
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
    edge_attrs = {'phero': 100}
    source_list = []
    sink_list = []
    source_list.append(source)
    sink_list.append(sink)
    hg.add_hyperedge(source_list, sink_list, edge_attrs)

    node_start_list = source_list
    node_end_list = sink_list

    # add 1 node in the middle between source and sink
    node_middle = generate_random_node_list(hg, 1)
    hg.add_hyperedge(source_list, node_middle, edge_attrs)
    hg.add_hyperedge(node_middle, sink_list, edge_attrs)
    hg.remove_hyperedge(hg.get_hyperedge_id(source_list, sink_list))

    current_node = node_middle[0]

    # generate (rewriting) all the other nodes
    SIZE = level_size
    for i in range(0, SIZE, 1):
        size = randint(block_size_min, block_size_max)  # pick size randomly
        if uniform(0, 1) > 0.5:  # make an and block
            out = rewrite_and_block_nonBF(hg, current_node, size)
            hg, current_node = out[0], out[1]

        else:  # make a xor block
            out = rewrite_xor_block(hg, current_node, size)
            hg, current_node = out[0], out[1]

    # print_hg_std_out_only(hg)

    return hg


# note: this allows for two or more loops to start and end from same nodes (that is, this function can return the same set of nodes if called twice)
def find_start_end_of_loop(hg):
    nodes = hg.get_node_set()
    tau_indices = []
    xor_indices = []
    for node in nodes:
        if node[0:4] == 'taus':
            split = node.split()
            tau_indices.append(split[1].strip())
        if node[0:5] == 'xor-s':
            split = node.split()
            xor_indices.append(split[1].strip())
    #print("Tau: "+str(tau_indices))
    #print("Xor: "+str(xor_indices))
    # pick two random tau split/join or xor split/join
    if uniform(0,1) > 0.5:
        if tau_indices != []:
            # pick tau nodes (join is start of loop, split is end of loop
            index = choice(tau_indices)
            node_start = 'taujoin ' + index
            node_end = 'tauspli ' + index
        else:
            # pick xor nodes
            index = choice(xor_indices)
            node_start = 'xor-j ' + index
            node_end = 'xor-s ' + index
    else:
        if xor_indices != []:
            # pick tau nodes (join is start of loop, split is end of loop
            # pick xor nodes
            index = choice(xor_indices)
            node_start = 'xor-j ' + index
            node_end = 'xor-s ' + index
        else:
            # pick xor nodes
            index = choice(tau_indices)
            node_start = 'taujoin ' + index
            node_end = 'tauspli ' + index
    # check if they have not been used yet
    
    # assign to start and end and return
    start_loop, end_loop = node_start, node_end
    return start_loop, end_loop

def get_random_node():
    node_name = randomword(7)
    node = []
    node.append(node_name)
    return node

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
        # pick two random nodes to be start and end of loop
        out = find_start_end_of_loop(hg)
        start = out[0]
        end = out[1]
        start_loop_node = []
        start_loop_node.append(start)
        end_loop_node = []
        end_loop_node.append(end)
        # TBC TBC should check also that node is not in and hyperedge???
        print("Found nodes for loop: {0}, {1}".format(node1, node2))
        # insert loop
        current_node = start_loop_node
        #print("Found nodes for loop: {0}, {1}".format(start_loop_node, end_loop_node))
        line = str(current_node)
        edge_attrs = {'phero' : 100}
        j = 0
        while j <= loop_length:
            if j != loop_length:                                     # add new node
                new_node = get_random_node()
                new_node_attrs = generate_random_node_attributes()
                hg.add_node(new_node[0], new_node_attrs)
                hg.add_hyperedge(current_node, new_node, edge_attrs)
                #line += " ||| " + str(current_node) + " > " + str(new_node)
                current_node = new_node
                #print("current_node: {0}".format(current_node))
            else:                                                    # connect with end loop node
                hg.add_hyperedge(current_node, end_loop_node, edge_attrs)
                #line += " ||| " + str(current_node) + " > " + str(end_loop_node)
            j += 1
        #print(line)
    return hg
            
        
    

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    hg = random_generate_hg_nonBF(2, 3, 4)

    # hg = add_random_loops(hg, 1, 5)
    print_hg_std_out_only(hg)
    
