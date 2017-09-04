
'''
Created on Aug 2, 2016

@author: UNIST
'''

from opsupport_bpm.util.print_hypergraph import print_node


#must be parameterised with weoghts    
def calculate_utility(path, w_cost, w_time, w_qual, w_avail):
    """
    calculate the utility of a path
    :param path (must be a halp hypergraph)
    :param w_cost weight of cost utility
    :param w_time weight of time utility
    :param w_qual weight of quality utility
    :param w_avail weight of availability utility
    """
    utility = 0.0
    utility = (w_cost * calc_utility_cost(path)) + (w_time * calc_utility_time(path)) + (w_qual * calc_utility_qual(path)) + (w_avail * calc_utility_avail(path))
    return utility

#this simply calculates utility as sum of cost
def calculate_utility_test(hg):
    utility = 0.0
    node_set = hg.get_node_set()
    for node in node_set:
        print_node(node, hg)
        utility = utility + hg.get_node_attribute(node,'cost')
    return utility

#this works for any anti-additive utility measure (just change the get_node_attribute)
def calc_utility_cost(path):
    '''
    calculate the total utility of path
    :param path: path (must be halp hypergraph)
    '''
    node_set = path.get_node_set()
    #calculate number of nodes in node_set
    node_num = len(node_set)
    #calculate sum of costs of all nodes
    total_cost = 0
    for node in node_set:
        total_cost = total_cost + path.get_node_attribute(node, 'cost')
    #calculate utility
    utility = 1 - (total_cost / node_num)
    return utility

def calc_utility_time(path):
    '''
    caclculate the time utility of a path
    :param path: path (must be halp hypergraph)
    '''
    return 0

def calc_utility_qual(path):
    '''
    caclculate the quality utility of a path
    :param path: path (must be halp hypergraph)
    '''
    node_set = path.get_node_set()
    #create list to have ordered elements
    node_list = list(node_set)
    #calculate number of nodes in node_set
    node_num = len(node_list) 
    #initialise utility value
    utility = path.get_node_attribute(node_list[0], 'qual')
    #calculate minimum of quality of nodes in path
    i = 0
    while i < node_num:
        curr_utility = path.get_node_attribute(node_list[i], 'qual')
        if curr_utility < utility:
            utility = curr_utility
        i = i + 1
    #calculate utility
    return utility

def calc_utility_avail(path):
    '''
    caclculate the availability utility of a path
    :param path: path (must be halp hypergraph)
    '''
    node_set = path.get_node_set()
    #calculate number of nodes in node_set
    node_num = len(node_set)
    #calculate product of avail for all nodes
    total_cost = 1.0
    for node in node_set:
        total_cost = total_cost * path.get_node_attribute(node, 'avail')
    #calculate utility
    utility = total_cost
    return utility
