'''
Created on Aug 2, 2016

Methods to handle pheromone in ant-colony optimisation

@author: UNIST
'''
import logging
import operator
import random

from opsupport_bpm.aco.aco_utility import calculate_utility
from opsupport_bpm.util.print_hypergraph import print_hyperedge


def partial_phero_update(hg_phero, path, w_cost, w_time, w_qual, w_avail, SYS_TYPE):
    """
    Wrapper of the partical pheromone update function
    :param hg_phero:
    :param path:
    :param w_cost:
    :param w_time:
    :param w_qual:
    :param w_avail:
    :param SYS_TYPE: ACS (ant colony system), MMAS (Max min ant colony)
    :return:
    """
    logger = logging.getLogger(__name__)
    if SYS_TYPE == "ACS":
        partial_phero_update_ACS(hg_phero, path, w_cost, w_time, w_qual, w_avail)
    elif SYS_TYPE == "MMAS":
        partial_phero_update_MMAS(hg_phero, path, w_cost, w_time, w_qual, w_avail)
    else:
        logger.error("Something went wrong!")

def final_phero_update(hg, tau, SYS_TYPE, w_cost, w_time, w_qual, w_avail,
                       hg_partial = None, p_best = None, n_xor_splits = None, avg_xor_choices = None, pbest = None):

    """
    Wrapper of the global pheromone update function

    :param SYS_TYPE: ACS (ant colony system), MMAS (Max min ant colony)
    :return:
    """
    logger = logging.getLogger(__name__)
    if SYS_TYPE == "ACS":
        final_phero_update_ACS(hg, tau, w_cost, w_time, w_qual, w_avail,
                       hg_partial)
    elif SYS_TYPE == "MMAS":
        pheromax, pheromin = final_phero_update_MMAS(hg, tau, w_cost, w_time, w_qual, w_avail,
                        p_best, n_xor_splits, avg_xor_choices, pbest)
        return pheromax, pheromin
    else:
        logger.error("Something went wrong!")

def partial_phero_update_MMAS(hg_phero, path, w_cost, w_time, w_qual, w_avail):
    logger = logging.getLogger(__name__)
    logger.debug("Partial phero update MMAS... nothing to update, actually")

    logger.debug("...done!")


def partial_phero_update_ACS(hg_phero, path, w_cost, w_time, w_qual, w_avail):
    '''
    updates the pheromone level in the main hypergraph (under optmisation) based on the utility 
    of the current optimal path
    :param hg_phero: jypergraph under optimisation
    :param path: current optimal path
    :param w_cost: weight of cost utility
    :param w_time: weight of time utility
    :param w_qual: weight of quality utility
    :param w_avail: weight of availability utility

    '''
    #update the phero level of all nodes in path
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    p_edge_set = path.get_hyperedge_id_set()
    p_utility = calculate_utility(path, w_cost, w_time, w_qual, w_avail)
    #for now, utility is the cost
    for p_edge in p_edge_set:
        p_edge_id = path.get_hyperedge_attribute(p_edge, 'id')
        curr_phero = hg_phero.get_hyperedge_attribute(p_edge_id, 'phero')
        path.add_hyperedge(path.get_hyperedge_tail(p_edge), path.get_hyperedge_head(p_edge), phero = curr_phero + p_utility, id = p_edge_id)
        logger.debug("Partial phero update - Phero value: {0}".format(str(path.get_hyperedge_attribute(p_edge, 'phero'))))
        logger.debug("Partial phero update - id: {0}".format(str(path.get_hyperedge_attribute(p_edge, 'id'))))




def final_phero_update_MMAS(hg, tau, w_cost, w_time, w_qual, w_avail,
                       p_best, n_xor_splits, avg_xor_choices, pbest):
    """
    updated by only the best solution in the last colony
    """
    logger = logging.getLogger(__name__)
    logger.debug("Final phero update MMAS started...")
    uti_weights = [w_cost, w_time, w_qual, w_avail]
    # calculate max and min pheromone level
    phero_max = calculate_phero_max_MMAS(tau, p_best, uti_weights)
    phero_min = calculate_phero_min_MMAS(phero_max, n_xor_splits, avg_xor_choices, pbest)
    logger.debug("Phero max-min = [{0}, {1}]".format(phero_max,phero_min))
    # update pheromone levels (limited by max and min)
    utility = calculate_utility(p_best, w_cost, w_time, w_qual, w_avail)
    logger.debug("Best path on last colony utility: {0}".format(utility))
    edge_set = p_best.get_hyperedge_id_set()
    for edge in edge_set:
        edge_id = p_best.get_hyperedge_attribute(edge, 'id')
        # evaporate current phero on hg and add partial update from hg_partial
        evap_u = tau * hg.get_hyperedge_attribute(edge_id, 'phero')
        new_phero = limit_phero_value(evap_u + utility, phero_min, phero_max)
        logger.debug("Edge {0}, old phero value {1}".format(edge_id, hg.get_hyperedge_attribute(edge_id, 'phero')))
        hg.add_hyperedge(p_best.get_hyperedge_tail(edge), p_best.get_hyperedge_head(edge), phero=new_phero,
                         id=edge_id)
        logger.debug("Edge {0}, new phero value {1}".format(edge_id, hg.get_hyperedge_attribute(edge_id, 'phero')))
    logger.debug("...done")
    return phero_max, phero_min


def calculate_phero_max_MMAS(tau, p_best, uti_weights):
    w_cost, w_time, w_qual, w_avail = uti_weights[0], uti_weights[1], uti_weights[2], uti_weights[3]
    utility = calculate_utility(p_best, w_cost, w_time, w_qual, w_avail)
    return utility * (1 / (1 - tau))


def calculate_phero_min_MMAS(phero_max, n_xor_splits, avg_xor_choices, pbest):
    root_pbest = pbest ** (1 / n_xor_splits)
    return phero_max * ((1 - root_pbest) / ((avg_xor_choices -1)*root_pbest))

def limit_phero_value(phero_lev, phero_min, phero_max):
    if phero_lev > phero_max:
        return phero_max
    elif phero_lev < phero_min:
        return phero_min
    else:
        return phero_lev



#tau is the evaporation coefficient
def final_phero_update_ACS(hg, tau, w_cost, w_time, w_qual, w_avail,
                       hg_partial):
    '''
    updates the pheromone level based on the results of one ant colony.
    This also performs the pheromone evaporation (using tau)
    :param hg: hypergraph under optimisation
    :param hg_partial: current optimal path updated with partial pheromone update
    :param tau: evaporation coefficient
    '''
    edge_set = hg_partial.get_hyperedge_id_set()
    for edge in edge_set:
        edge_id = hg_partial.get_hyperedge_attribute(edge, 'id')
        #evaporate current phero on hg and add partial update from hg_partial
        evap_u = tau * hg.get_hyperedge_attribute(edge_id, 'phero')
        new_phero = evap_u + hg_partial.get_hyperedge_attribute(edge, 'phero')
        hg.add_hyperedge(hg_partial.get_hyperedge_tail(edge), hg_partial.get_hyperedge_head(edge), phero = new_phero, id = edge_id)
    
    


# node_set: a set of nodes (normally the head of an edge)
# visited: the list of visisted hypernodes
def is_visited(node_set, visited):
    '''
    checks whether a set of nodes has been visited
    :param node_set: the set of nodes 
    :param visited: the set of visited nodes
    '''
    found = False
    #print(str(visited))
    #print(str(node_set))
    for i in range(len(visited)-1):
        #take each element in visited, convert it into a list/set and check if equal
        nodes = visited[i]
        if set(node_set) == set(nodes):
            found = True
    return found


def phero_choice_single_node(f_edge_set, hg, IGNORE_PHERO = False):
    '''
    WORKS WITH NON RECURSIVE VERSION
    returns one edge among a set of candidate edges. The edge to be returned is randomly chosen 
    using a uniform probability distribution proportional to the pheromone distribution on the edges.
    :param f_edge_set: set of candidate edges
    :param hg: hypergraph under optimisation
    '''
    # use this to switch on some debugging on standard output
    debug = False
    #setup the logger
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Completely random choice for benchmarking:
    if IGNORE_PHERO == True:
        chosen_edge = random.sample(f_edge_set, 1)
        logger.debug("Chosen edge ignoring pheromone (total random): {0}".format(chosen_edge))
        return chosen_edge

    #create an ordered list of tuples (edge_id, phero_value)
    """ remove the edges already visited, so only nodes that have not been visited already can be chosen"""      
    """ while loop begins...."""
    #edge_found = False
    #while not edge_found:
    dic = {}
    for edge in f_edge_set:
        dic[edge] = hg.get_hyperedge_attribute(edge, 'phero')
    sorted_dict = sorted(dic.items(), key=operator.itemgetter(1))
    #build hash_pheroval like [edge_id]>[phero value]
    hash_pheroval = [item[1] for item in sorted_dict]
    hash_edgeid = [item[0] for item in sorted_dict]
#     for edge in edge_set:
#         hash_pheroval.append(hg.get_hyperedge_attribute(edge, 'phero'))
#         hash_edgeid.append(edge)
    # build cumulative hash_pheroval to compare randomly extracted variable
    cumul_hash = list(hash_pheroval)
    i=0
    while i < len(hash_pheroval):
        j = 0
        while j < i:
            cumul_hash[i] = cumul_hash[i] + hash_pheroval[j]
            j = j+1
        i = i+1
    if debug: print("This is the list: "+str(hash_pheroval))
    if debug: print("This is the cumul list: "+str(cumul_hash))
    #extract random number and check
    len_ch = len(cumul_hash)-1
    low = cumul_hash[0]
    high = cumul_hash[len_ch]
    choice = random.uniform(0, high)
    #logger.debug("Random number to choose next edge: {0} ==== Cumulative choice list: {1}".format(str(choice),str(cumul_hash)))
    #logger.debug("Sorted dict: {0}".format(str(sorted_dict)))
    logger.debug("^^^ Phero value of possible edges: {0}".format(str(hash_pheroval)))
    logger.debug("^^^ Random value: {0}".format(choice))
    #logger.debug("Hash edge_id: {0}".format(str(hash_edgeid)))
    #caculate the edge_id based on the drawn random number
    notFound = True
    i = 0
    edge_in = 0
    while (notFound):
        #adjust if only 1 edge available (or if chosen is last edge in the list)
        if i == (len(cumul_hash) - 1):
            notFound = False
            edge_in = i
        #general case
        elif choice <= cumul_hash[0]:
            notFound = False
            edge_in = 0
        elif choice > cumul_hash[i] and choice <= cumul_hash[i+1]:
            notFound = False
            edge_in = i+1
        i = i+1
    #calculate chosen edge
    #print("Chosen edge i: "+str(i))
    chosen_edge = hash_edgeid[edge_in] 
    logger.debug("^^^ Chosen edge (phero): {0}".format(str(chosen_edge)))
    print_hyperedge(chosen_edge, hg)
    return chosen_edge


#debugged!
def phero_choice(edge_set, hg, visited):
    '''
    WORKS ONLY WITH RECURSIVE VERSION OF ACO !!!!!!
    returns one edge among a set of canidates edges. The edge to be returned is randomly chosen 
    using a uniform probaility distribution proportional to the pheromone distribution on the edges.
    :param edge_set: the canidate set of edges
    :param hg: hypergraoh under optimisation
    :param visited: set of visited nodes (required!)
    '''
    #setup the logger
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    #create an ordered list of tuples (edge_id, phero_value)
    """ remove the edges already visited, so only nodes that have not been visited already can be chosen"""      
    """ while loop begins...."""
    edge_found = False
    while not edge_found:
        dic = {}
        for edge in edge_set:
            dic[edge] = hg.get_hyperedge_attribute(edge, 'phero')
        sorted_dict = sorted(dic.items(), key=operator.itemgetter(1))
        #build hash_pheroval like [edge_id]>[phero value]
        hash_pheroval = [item[1] for item in sorted_dict]
        hash_edgeid = [item[0] for item in sorted_dict]
    #     for edge in edge_set:
    #         hash_pheroval.append(hg.get_hyperedge_attribute(edge, 'phero'))
    #         hash_edgeid.append(edge)
        # build cumulative hash_pheroval to compare randomly extracted variable
        cumul_hash = list(hash_pheroval)
        i=0
        while i < len(hash_pheroval):
            j = 0
            while j < i:
                cumul_hash[i] = cumul_hash[i] + hash_pheroval[j]
                j = j+1
            i = i+1
        print("This is the list: "+str(hash_pheroval))
        print("This is the cumul list: "+str(cumul_hash))
        #extract random number and check
        len_ch = len(cumul_hash)-1
        low = cumul_hash[0]
        high = cumul_hash[len_ch]
        choice = random.uniform(0, high)
        
        
        #logger.debug("Random number to choose next edge: {0} ==== Cumulative choice list: {1}".format(str(choice),str(cumul_hash)))
        #logger.debug("Sorted dict: {0}".format(str(sorted_dict)))
        logger.debug("^^^ Phero value of possible edges: {0}".format(str(hash_pheroval)))
        logger.debug("^^^ Random value: {0}".format(choice))
        #logger.debug("Hash edge_id: {0}".format(str(hash_edgeid)))
        #caculate the edge_id based on the drawn random number
        notFound = True
        i = 0
        edge_in = 0
        while (notFound):
            #adjust if only 1 edge available (or if chosen is last edge in the list)
            if i == (len(cumul_hash) - 1):
                notFound = False
                edge_in = i
            #general case
            elif choice <= cumul_hash[0]:
                notFound = False
                edge_in = 0
            elif choice > cumul_hash[i] and choice <= cumul_hash[i+1]:
                notFound = False
                edge_in = i+1
            i = i+1
        #calculate chosen edge
        #print("Chosen edge i: "+str(i))
        chosen_edge = hash_edgeid[edge_in] 
        logger.debug("^^^ Candidate edge (phero): {0}".format(str(chosen_edge)))
        print_hyperedge(chosen_edge, hg)
        # check if head of chosen edge has been visited, otherwise retry
        if is_visited(hg.get_hyperedge_head(chosen_edge), visited):
            # head already visited: delete edge from edge_set and retry
            edge_set.remove(edge)
            logger.debug("^^^ Head of candidate edge {0} already visited, try again...".format(str(chosen_edge)))
            if edge_set == set():
                """ No other edges available, phero_choice and has to go back """
                return None
        else:
            edge_found = True
            logger.debug("^^^ Candidate edge chosen: {0}".format(str(chosen_edge)))
            return chosen_edge
    #logger.debug("^^^ end selected hyperedge print ^^^^")
    return chosen_edge