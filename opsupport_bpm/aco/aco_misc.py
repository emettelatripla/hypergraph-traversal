'''
Created on Aug 2, 2016

Various useful functions for aco

- random initialisation of utility values for all nodes in a hypergraph

@author: UNIST
'''

from random import uniform





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
