'''
Created on Aug 2, 2016

Main module for aco optimisation
Note: only the NON RECURSIVE ACO has been tested (on hypergraphs including loops as well)

- aco algorithm
- aco search
- escape from loops

@author: Marco Comuzzi mcomuzzi@unist.ac.kr
'''
import logging
import random

from scipy import sparse

from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities.directed_matrices import get_head_incidence_matrix, get_tail_incidence_matrix, get_hyperedge_id_mapping, get_node_mapping
from opsupport_bpm.aco.aco_pheromone import final_phero_update
from opsupport_bpm.aco.aco_pheromone import partial_phero_update
from opsupport_bpm.aco.aco_pheromone import phero_choice_single_node
from opsupport_bpm.aco.aco_utility import calculate_utility, calc_utility_cost, calc_utility_qual
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only
from opsupport_bpm.models.hypergraph import initialise_pheromone, reset_pheromone, number_of_xor_splits

import requests
import sys


#setup logger
def get_start_end_node(hg):
    """ 
    returns the start and end node(s) of a hypergraph
    Raises an error if there are no start or end nodes
    Raises a warning if more than one start or end nodes found
    :param hg: the hypergraph
    :returns the start and end nodes, None if no start node is found
    """
    logger = logging.getLogger(__name__)
    nodes = hg.get_node_set()
    i = 0
    j = 0
    start_node = []
    end_node = []
    for node in nodes:
        if hg.get_node_attribute(node, 'source') == True:
            start_node.append(node)
            i += 1
        elif hg.get_node_attribute(node, 'sink') == True:
            end_node.append(node)
            j += 1
    if i == 0:
        raise AssertionError("No start node found...STOP!")
    elif j == 0:
        raise AssertionError("No end node found...STOP!")
    elif i > 1 or j > 1:
        logger.warning("Found {0} start nodes and {1} end node(s)...STOP!".format(i,j))
    return (start_node,end_node)

def post_process_loop_escape(p_opt):
    '''
    NON RECURSIVE ACO
    Post processing of optimal path to remove disconnected nodes (if any) remained from loop escape
    :param p_opt: optimal path
    '''
    logger = logging.getLogger(__name__)
    node_set = p_opt.get_node_set()
    # check each node
    for node in node_set:
        used = False
        logger.debug("Post-processing loop escape node: {0}".format(node))
        edge_set = p_opt.get_hyperedge_id_set()
        # for each node, check if they are in the head or tail of a hyperedge
        for edge in edge_set:
            tail = p_opt.get_hyperedge_tail(edge)
            head = p_opt.get_hyperedge_head(edge)
            if (node in tail) or (node in head):
                logger.debug("...node is used, keep it!")
                used = True
        if not used:
            logger.info("Post processing (loop escape) of optimal path, deleting unused node: {0}".format(node))
            p_opt.remove_node(node)
    return p_opt
            
        
        

""" ====================================== """
""" MAIN ACO PROCEDURE FOR ALL PATHS     """
""" =====================================+ """


def aco_algorithm_norec(hg:DirectedHypergraph, ANT_NUM, COL_NUM, tau, W_UTILITY, SYS_TYPE, SEARCH_TYPE, IGNORE_PHERO = False):
    '''
    NON RECURSIVE ACO
    Main procedure for aco optimisation of hypergraph
    :param hg: hypergraph
    :param ANT_NUM: number of ants per colony
    :param COL_NUM: number of colonies
    :param tau: pheromone evaporation coefficient
    :param W_UTILITY: dictionary of utility weights, e.g. (cost : 0.2, avail : 0.2, qual : 0.2, time : 0.4)
    :param SYS_TYPE: ACS (ant colony system) or MMAS (Max-min ant system)
    :param SEARCH_TYPE type of path to be searched ("B" "F" or "BF")
    '''
    # check start and end nodes in hg
    logger = logging.getLogger(__name__)
    logger.info("MOACO optimisation has started with system: {0}".format(SYS_TYPE))
    # steup parameters if SYS_TYPE = MMAS
    pbest = 0.005
    # average number of options for xor splits
    n_xor_splits = number_of_xor_splits(hg)
    nodes = hg.get_node_set()
    tot = 0
    for node in nodes:
        if hg.get_node_attribute(node, 'type') == 'xor-split':
            tot += len(hg.get_forward_star(node))
    avg_xor_choices = tot / n_xor_splits

    # adjust initial pheromone level to a high value for MMAS
    if SYS_TYPE == 'MMAS':
        initialise_pheromone(hg,100)
    elif SYS_TYPE == 'ACS':
        reset_pheromone(hg)
    W_COST = W_UTILITY['cost']
    W_AVAIL = W_UTILITY['avail']
    W_QUAL = W_UTILITY['qual']
    W_TIME = W_UTILITY['time']

    # setup the logger
    #logging.basicConfig(filename='aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)

    # currently optimal path
    # p_opt = DirectedHypergraph()
    # utility_opt = 0.0

    # list of non-dominated solutions found
    non_dom_solutions = set()

    # LOOP ON COLONIES
    col = 0
    while col < COL_NUM:
        #counter for ant number
        ant = 0
        logger.info("--- Processing COLONY {0} of {1} -------------------".format(col, COL_NUM - 1))
        hg_phero = hg.copy()
        # LOOP ON ANTS
        while ant < ANT_NUM:
            logger.info("----- Processing COLONY n. {1}, ANT n. {0} of {2} -----------------".format(ant, col, ANT_NUM -1))
            p = DirectedHypergraph()
            """ call aco_search on p"""
            ant_attrs = {}                          # set attributes of this ant
            p = DirectedHypergraph()                # current path built by this ant
            # Call the appropriate aco search procedure based on type of path searched
            if SEARCH_TYPE == "BF":
                p = aco_search_nonrec(hg, ant_attrs)[0]
            if SEARCH_TYPE == "B" or SEARCH_TYPE == "F":
                p, path_found = aco_search_generic_path(hg, ant_attrs, SEARCH_TYPE=SEARCH_TYPE)
                if path_found:
                    print_hg_std_out_only(p)
                else:
                    p = DirectedHypergraph()
            # calculate utility of p
            if len(p.get_node_set()) == 0:
                utility = 0
            else:
                utility = calculate_utility(p, W_COST, W_TIME, W_QUAL, W_AVAIL)
            #do partial pheromone update
            # TODO change pheromone update:
            partial_phero_update(hg_phero, p, W_COST, W_TIME, W_QUAL, W_AVAIL, SYS_TYPE)
            logger.info("...ant finished!")
            non_dom_solutions.add(p.copy())
            non_dom_solutions = delete_dominated_sol(non_dom_solutions)


            ant = ant + 1
            #pheromone update
            #TBC TBC
        if IGNORE_PHERO == False:
            #actual pheromone update after processing an entire colony
            if SYS_TYPE == 'ACS':
                pass
                # final_phero_update(hg, tau, SYS_TYPE, W_COST, W_TIME, W_QUAL, W_AVAIL,
                #                    hg_partial = hg_phero)
            elif SYS_TYPE == 'MMAS':
                pass
                # pheromax, pheromin = final_phero_update(hg, tau, SYS_TYPE, W_COST, W_TIME, W_QUAL, W_AVAIL,
                #                                                 p_best=col_p_best, n_xor_splits=n_xor_splits,
                #                                                 avg_xor_choices=avg_xor_choices, pbest=pbest)
                if SYS_TYPE == 'MMAS':
                    # special initialisation of pheromone at the first iteration
                    if col == 0 and ant == ANT_NUM:
                        logger.info("Initialising pheromone levels to 100")
                        edges = hg.get_hyperedge_id_set()
                        for edge in edges:
                            if hg.get_hyperedge_attribute(edge, 'phero') == 100:
                                hg.add_hyperedge(hg.get_hyperedge_tail(edge), hg.get_hyperedge_head(edge),
                                                 phero=pheromax,
                                                 id=edge)

                logger.info("Global pheromone update done using max-min [{0}, {1}]".format(pheromin,pheromax))


        col = col + 1
                # special initialisation at first
    #do something else
    # post-process p_opt to remove spurious nodes remained from loop escape
    p_opt = post_process_loop_escape(p_opt)
    logger.info("********** OPTIMAL PATH FOUND ******************")
    print_hg_std_out_only(p_opt)
    UTILITY = calculate_utility(p_opt, W_COST, W_TIME, W_QUAL, W_AVAIL)
    logger.info("****** UTILITY: "+str(UTILITY))
    logger.info("***********************************************")
    logger.warning("Is BF-path: {0}".format(p_opt.is_BF_hypergraph()))
    return (p_opt, UTILITY)


def delete_dominated_sol(solutions):
    """
    Deletes solutions that are dominated
    Uses: cost as utility_01, qual as utility_02
    :param non_dominated_sol: a set of solutions
    :return: 
    """
    to_remove = set()
    for path in solutions:
        uti_01, uti_02 = calc_utility_cost(path), calc_utility_qual(path)
        for other_path in solutions:
            if other_path is not path:
                uti_other_01, uti_other_02 = calc_utility_cost(path), calc_utility_qual(path)
                if (uti_other_01 > uti_01 and uti_other_02 >= uti_02) or (uti_other_02 > uti_02 and uti_other_01 >= uti_01):
                    to_remove.add(path)
    return solutions - to_remove

def add_edge(p,hg,edge):
    """
        add edge to optimal path
        :param p: the current optimal path
        :param hg: the hypergraph to optimise
        :param edge: the edge to be added
        :returns the optimal path p
    """
    phero_next_edge = hg.get_hyperedge_attribute(edge, 'phero')
    head_next_edge = hg.get_hyperedge_head(edge)
    for head_node in head_next_edge:
        attrs = hg.get_node_attributes(head_node)
        p.add_node(head_node,attrs)
    tail_next_edge = hg.get_hyperedge_tail(edge)
    for tail_node in tail_next_edge:
        attrs = hg.get_node_attributes(tail_node)
        p.add_node(tail_node,attrs)
    edge_id_p = p.add_hyperedge(tail_next_edge, head_next_edge, phero = phero_next_edge, id = edge, name = edge)
    return p, edge_id_p

def add_head_to_nodes_to_process(edge, hg, nodes_to_process):
    """ 
        adds the tail of an edge to the set of node to be processed
        :param edge: the current edge
        :param hg: the hypergraph under optimisation
        :param nodes_to_process: the current array of nodes to be processed
        :returns the nodes_to_process updated with the nodes in the tail of edge
    """
    logger = logging.getLogger(__name__)
    node_set = hg.get_hyperedge_head(edge)

    random.shuffle(node_set)

    # add to node to process
    for node in node_set:
        if node not in nodes_to_process:
            nodes_to_process.append(node)
    logger.debug("Node to process: {0}".format(nodes_to_process))      
    return nodes_to_process


def escape_from_loop(current_node,next_edge,p,hg,used_edges):
    '''
    when an ant encounters a node that they have already visited, this procedure allows them to escape from the loop
    by retracing to a previously visited node from which they can proceed "outside the loop"
    Returns: 
    next_edge = escape[0]                next_edge to continue building optimal path
    p = escape[1]                        current optimal path
    curent_node = escape[2]              new current_node after loop escape  
    delete_nodes_visited = escape[3]     nodes to be deleted from set of visited node in aco_search
    
    :param current_node:
    :param next_edge:
    :param p:
    :param hg:
    :param used_edges:
    '''
    
    logger = logging.getLogger(__name__)
    delete_nodes_visited = []
    safe_node_found = False
    # check if we can escape from current node
    curr_node_set = []
    curr_node_set.append(current_node)
    outgoings = hg.get_successors(curr_node_set)
    logger.debug("....successors of current node {1}: {0}".format(outgoings,current_node))
    outgoings = outgoings.remove(next_edge)
    logger.debug("Used edges: {0}".format(used_edges))
    logger.debug("Outgoings before: {0}".format(outgoings))
    if outgoings is not None:
        outgoings.difference_update(used_edges)
        logger.debug("Usable ougoings from current node: {0}".format(outgoings))
    if outgoings is not None:
        logger.debug("..... Current node {0} has possible escape edge")
        new_edge = random.sample(set(outgoings),1)[0]
        used_edges.append(new_edge)
        logger.debug("..... Current node {0} has posible escape edge {1}".format(current_node,new_edge))
        return new_edge, p, current_node, delete_nodes_visited

    current_node_set = []
    current_node_set.append(current_node)
    while not safe_node_found:
        # go back one node (with get predecessors - returns a set!)
        logger.debug("....current node set: {0}".format(current_node_set))
        #### prec_edge_set = p.get_predecessors(current_node_set)
        prec_edge_set = set()
        # get all the nodes in the backward stars
        for node in current_node_set:
            logger.debug("This is node in the for loop: {0}".format(node))
            logger.debug("Backward star: {0}".format(p.get_backward_star(node)))
            prec_edge_set = prec_edge_set.union(p.get_backward_star(node))
        logger.debug("..... set of predecessors to choose from: {0}".format(prec_edge_set))
        prec_edge_set.difference_update(used_edges)
        logger.debug("..... set of predecessors to choose from after used edges update: {0}".format(prec_edge_set))

        # choose edge to back (in current path)
        p_back_edge = random.sample(set(prec_edge_set),1)[0]
        # get id of chosen back edge in hg
        tail = p.get_hyperedge_tail(p_back_edge)
        head = p.get_hyperedge_head(p_back_edge)
        back_edge = hg.get_hyperedge_id(tail,head)
        logger.debug("...... Going back using edge: {0} in HG [{1} in current path]".format(back_edge,p_back_edge))
        logger.debug(".....go back edge HEAD, TAIL: {0}, {1}".format(head, tail))
        ## current_node = p.get_hyperedge_tail(p_back_edge)
        current_node_set = p.get_hyperedge_tail(p_back_edge)
        logger.debug("...... Now in node {0}, looking for an escape".format(current_node_set))
        # remove edge used to go back
        # look for other forward edges

        #### forward_edges = hg.get_successors(random.sample(set(current_node_set), 1))
        # look forward using all forward stars
        forward_edges = set()
        for node in current_node_set:
            logger.debug("This is node in the for loop: {0}".format(node))
            forward_edges = forward_edges.union(hg.get_forward_star(node))

        logger.debug("Forward edges to choose from: {0}".format(forward_edges))
        # remove edge used to go back from path p
        logger.debug("Removing hyperedge from path: ({0}, {1}, {2}) ".format(p_back_edge,p.get_hyperedge_tail(p_back_edge),p.get_hyperedge_head(p_back_edge)))
        # remove edge used to go back from current optimal path
        p.remove_hyperedge(p_back_edge)
        # remove edge used to go back from possible choices to escape the loop
        forward_edges.remove(back_edge)
        if not forward_edges == set():
            new_edge = random.sample(set(forward_edges),1)[0]
            logger.debug("...... escape found! Edge: {0}".format(new_edge))
            ## safe_node = current_node
            current_node = random.sample(set(current_node_set), 1)
            safe_node = current_node
            safe_node_found = True
            # TO-DO prepare return
            logger.debug("....RETURNING FROM loop escape, delete_nodes_visited: {0}".format(delete_nodes_visited))
            return new_edge, p, safe_node, delete_nodes_visited
        # only the nodes in the loop are saved as nodes_to_delete
        for node in current_node_set:
            delete_nodes_visited.append(node)
    return None

""" ====================================== """
""" SEARCH FOR BF paths    """
""" =====================================+ """


def aco_search_nonrec(hg, ant_attributes, IGNORE_PHERO = False):
    '''
    NON RECURSIVE
    non-recursive version of aco search (breadth-first exploring of the hypergraph)
    simulates the behaviour of one single ant and returns the optimal path discovered by that ant

    Extended with SMARTCHOICE

    :param hg: hypergraph
    '''

    nodes_for_enum = [200]
    index = 0

    # get the logger
    logger = logging.getLogger(__name__)

    # assumption:  ONE END event (there can be more than one start event, one will be chosen randomly)
    start_end = get_start_end_node(hg)
    start_node_set = start_end[0]
    end_node_set = start_end[1]
    start_node = random.sample(set(start_node_set), 1)[0]
    logger.debug("Found START node set: {0}".format(start_node_set))
    logger.debug("Chosen START node (if many available): {0}".format(start_node))
    logger.debug("Found END node set: {0}".format(end_node_set))
    # ASSUMPTION: only one end node
    end_node = end_node_set[0]
    logger.debug("Found END node: {0}".format(end_node))

    # count number of nodes to process
    number_of_nodes = len(hg.get_node_set())
    logger.debug("Number of nodes to process: {0}".format(number_of_nodes))

    # array of nodes to process, add start_node as first node to process
    nodes_to_process = []
    nodes_to_process.append(start_node)

    nodes_visited = []
    used_edges = []
    
    # begin looking forward...
    p = DirectedHypergraph()                    # current optimal path
    stop = False
    i = 0                                       # index of current node to process
    current_node = nodes_to_process[0]
    waiting = {}
    # to escape, isolate the nodes already visited because of waiting
    #nodes_visited_waiting = []

    while not stop:
        logger.debug("============= VISITING NEXT NODE: --- {0} ---- ========================".format(current_node))
        f_edge_set = hg.get_forward_star(current_node)

        nodes_for_enum.insert(index,current_node)
        index += 1

        # choose next edge based on smartchoice or pheromone distribution
        next_edge = None
        #is_smartchoice = hg.get_node_attribute(current_node, 'smartchoice')
        is_smartchoice = False
        if is_smartchoice == True:
            # do something with smartchoice
            is_smart_attr, is_smart_node, is_smart_service = hg.get_node_attribute(current_node, 'smart_attribute'), hg.get_node_attribute(current_node, 'smart_node'), hg.get_node_attribute(current_node, 'smart_service')
            if  is_smart_attr == True:
                # select next edge based on ATTRIBUTE smartchoice
                # TO BE COMPLETED
                logger.debug("Choosing next node using smart_attribute...")
                # retrieve the attribute value required for the choice at this node
                choice_attr = hg.get_node_attribute(current_node, 'choice_attr')
                attr_value = ant_attributes[choice_attr]
                logger.debug("Attribute - {0} - value: {1}".format(choice_attr, attr_value))
                # choose next edge
                opt_dict = hg.get_node_attribute(current_node, 'opt_dict')
                next_edge = opt_dict[attr_value]
                logger.debug("==> Next edge chosen (using smart_attribute) is: {0}".format(next_edge))
            elif is_smart_node == True:
                # select next edge based on NODE smartchoice
                # idea: reuse pherochoice with a copy edge_set that uses probailities read from the node instead of phero levels
                logger.debug("Choosing next node using smart_node...")
                f_edge_set_copy = f_edge_set
                # extract one random number between 0.1
                random_v = random.random()
                # build dict of probabilities
                edge_prob_cumul = {}
                total = 0
                for edge in f_edge_set_copy:
                    edge_prob = hg.get_node_attribute(current_node, 'edge_prob')[edge]
                    edge_prob_cumul[edge] = total + edge_prob
                    total += edge_prob
                for edge in edge_prob_cumul:
                    if random_v <= edge_prob_cumul[edge]:
                        next_edge = edge
                        break
                logger.debug("Next edge phero level is: {0}".format(hg.get_hyperedge_attribute(next_edge, 'phero')))
                logger.debug("==> Next edge chosen (using smart_node) is: {0}".format(next_edge))
            elif is_smart_service == True:
                logger.debug("Choosing next node using smart_service...")
                # select next edge based on SERVICE smartchoice
                # get the service URI
                service_uri = hg.get_node_attribute(current_node, 'uri')
                logger.debug("Invoking service at: {0}".format(service_uri))
                # call the service (min REST client)
                response = requests.get(service_uri)
                ret_value = response.json()['ret_value']
                logger.debug("returned value: {0}".format(ret_value))
                # decide next edge based on the returned value
                edge_list = hg.get_node_attribute(current_node, 'opt_dict')
                next_edge = edge_list[ret_value]
                logger.debug("==> Next edge chosen (using smart_service) is: {0}".format(next_edge))
        else:
            next_edge = phero_choice_single_node(f_edge_set, hg, IGNORE_PHERO)
            logger.debug("==> Next edge chosen using traditional pheromone: {0}".format(next_edge))
        # check if next_edge chosen with pheromone is different
        # REMOVE FOR SIMULATION
        if is_smartchoice:
            phero_edge = phero_choice_single_node(f_edge_set, hg, IGNORE_PHERO)
            logger.debug("==> Next would be edge (chosen using pheromone): {0}".format(phero_edge))

        # look in the head of chosen next edge
        next_head = hg.get_hyperedge_head(next_edge)
        # if a node in next edge has already been visited, then we might be an a loop....check
        escape = False
        for node in next_head:
            if node in nodes_visited:
                logger.debug("===OO=== Node {0}; Possible escape needed, should investigate more...".format(node))
                # check if node is head of waiting hyperedges (if yes, then node is waiting, we are not in a loop!
                waiting_head = False
                waiting_edges = waiting.keys()
                head = []
                head.append(node)
                for edge in waiting_edges:
                    if hg.get_hyperedge_head(edge) == head:
                        waiting_head = True
                if waiting_head or node == end_node:
                    logger.debug("==OO== ...I was not in a real loop, continue :)")
                else:
                    logger.debug("==OO== ...I am in a LOOP, must ESCAPE!")
                    escape = True
            if escape:
                logger.debug("#Escape begins ...")
                # remove current from node to process and related egdge from path p
                nodes_to_process.remove(current_node)
                i = i-1
                # ESCAPE FRom the looP
                escape = escape_from_loop(current_node,next_edge,p,hg,used_edges)
                next_edge = escape[0]
                p = escape[1]
                current_node = escape[2][0]
                delete_nodes = escape[3]
                # deleting nodes in the loop
                logger.debug("Nodes to delete: {0}".format(delete_nodes))
                # delete current node from visited nodes
                nodes_visited.remove(current_node)
                for node in delete_nodes:
                    logger.debug("Removing node from list of nodes to process: {0}".format(node))
                    nodes_to_process.remove(node)
                    i -= 1                          # update counter of current node
                    if node in nodes_visited:
                        logger.debug("Removing node from list of visited nodes: {0}".format(node))
                        nodes_visited.remove(node)
                logger.debug(".... #Escape terminated!")
                logger.debug(".... current node: {0}".format(current_node))
            # ESCAPE TB TB TB 
        # wait for matches if its hyperedge
        """ wait for matches TBC"""
        logger.debug("==> Current node {0}, successors: {1}".format(current_node,hg.get_successors(current_node)))
        # need a set to use get_successors
        current_node_set = set()
        current_node_set.update({current_node})
        logger.debug("==> Current node set: {0}".format(current_node_set))
        if next_edge not in hg.get_successors(current_node_set):
            # current_node is not the head of the chosen edge...so it must be an hyperedge
            logger.debug("==> I am in a hyperedge, check waiting...")
            # look if there is a match waiting to happen
            if next_edge in waiting.keys():
                # add current node
                content = waiting[next_edge] 
                content.append(current_node)
                waiting[next_edge] = content
                current_tail = hg.get_hyperedge_tail(next_edge)
                #logger.debug("+++ +++ +++ This is the tail of the edge: {0}".format(current_tail))
                #logger.debug("+++ +++ +++ This is the waiting list edge {1}: {0}".format(waiting[next_edge],next_edge))
                if set(waiting[next_edge]) == set(current_tail) :
                    logger.debug("+++ +++ +++ Waiting edge found, add hyperedge")
                    # add hyperedge to optimal path
                    p, edge_id = add_edge(p,hg, next_edge)
                    # delete entry in waiting
                    del waiting[next_edge]

                    

                    #UPDATE CURRENT NODE !!!!!! TBC TBC TBC TBC
            # node is extreme of a hyperarc, we have to stop and wait for a match
            else:
                logger.debug("+++ +++ +++ I am the first ant here, put myself to waiting")
                waiting[next_edge] = []
                content = waiting[next_edge]
                content.append(current_node)
                waiting[next_edge] = content
            
        else:
            # single node is tail of edge, so we can add it to optimal path
            # add egde, tail and head to optimal path p
            logger.debug("Adding new edge to current path ({0}, {1}, {2})".format(next_edge,hg.get_hyperedge_tail(next_edge),hg.get_hyperedge_head(next_edge)))
            p, edge_id = add_edge(p,hg,next_edge)

        # update nodes to process
        nodes_to_process = add_head_to_nodes_to_process(next_edge, hg, nodes_to_process)
        # save current node as visited
        nodes_visited.append(current_node)
        logger.debug("Nodes visited: {0}".format(nodes_visited))
        logger.debug("Nodes waiting: {0}".format(waiting))
        # terminating condition: next node is end event and it is only one left to process!
        #nodes_visited.append(current_node)
        #nodes_to_process.remove(current_node)

        # check next node
        i += 1
        logger.debug("Evaluating terminal condition - current node: {0}".format(current_node))
        current_node = nodes_to_process[i]
        logger.debug("Evaluating terminal condition - next node: {0}".format(current_node))
        if current_node == end_node:
            if waiting == {}:
                stop = True
                logger.debug(" ===!!! Optimisation terminated at node: {0}".format(current_node))
            else:
                logger.debug("Next node to process is end node, but I cannnot stop now....")
                nodes_to_process.append(current_node)
                i += 1
                current_node = nodes_to_process[i]
                logger.debug("==> continue, next node will be: {0}".format(current_node))
        else:                                   # it is not end node
            logger.debug("==> continue node processing, next node is: {0}".format(current_node))

        """ old terminatng condition
        if not len(nodes_to_process) == len(nodes_visited):
            # check next node to process
            i += 1
            current_node = nodes_to_process[i]
            # if it end_node, mark as processed and goto next
            if current_node == end_node:
                logger.debug("End node {0} reached, nothing to process forward")
                nodes_visited.append(current_node)
                if not len(nodes_to_process) == len(nodes_visited):
                    i += 1
                    current_node = nodes_to_process[i]
        if len(nodes_to_process) == len(nodes_visited) and waiting == {}:
            logger.debug("Optimisation terminated, all nodes processed and end node found: {0}".format(end_node))
            stop = True
        if len(nodes_to_process) == len(nodes_visited) and not waiting == {}:
            logger.error("Something went wrong here :(((")
        # get ready to continue
        END OLD TERMINATING CONDITION"""
    #return p, nodes_visited
    return p, nodes_for_enum


def get_fstar(node_set, hg:DirectedHypergraph):
    fstar = set()
    for node in node_set:
        fstar.update(hg.get_forward_star(node))
    return fstar

def keep_edges(edge_set, hg, edge_type = "BF"):
    to_remove = []
    if edge_type == "BF":
        for edge in edge_set:
            if not (is_B_edge(hg, edge) or is_F_edge(hg, edge)):
                to_remove.append(edge)
    elif edge_type == "B":
        for edge in edge_set:
            if not (is_B_edge(hg, edge)):
                to_remove.append(edge)
    elif edge_type == "F":
        for edge in edge_set:
            if not (is_F_edge(hg, edge)):
                to_remove.append(edge)
    return edge_set.difference(to_remove)


""" ====================================== """
""" SEARCH FOR GENERIC B, F, B+F paths     """
""" =====================================+ """

def aco_search_generic_path(hg:DirectedHypergraph, ant_attributes, IGNORE_PHERO = False, SEARCH_TYPE="BF"):
    logger = logging.getLogger(__name__)  # get the logger
    # get start and end node
    start_end = get_start_end_node(hg)
    start_node_set = start_end[0]
    end_node_set = start_end[1]
    start_node = random.sample(set(start_node_set), 1)[0]
    logger.info("Found START node set: {0}".format(start_node_set))
    logger.debug("Chosen START node (if many available): {0}".format(start_node))
    logger.info("Found END node set: {0}".format(end_node_set))
    # ASSUMPTION: only one end node
    end_node = end_node_set[0]
    # count number of nodes to process
    number_of_nodes = len(hg.get_node_set())
    logger.debug("Number of nodes to process: {0}".format(number_of_nodes))
    p = DirectedHypergraph()  # the optimal path
    nodes_to_process = []
    nodes_to_process.append(start_node)
    i = 0
    STOP = False
    edge_added_hg = []
    edge_added_match = {}  # {node_id hg: node_id p}
    current_node_set = set()
    current_node_set.add(start_node)
    while not STOP:
        logger.info("Visiting new node_set: {0}".format(current_node_set))
        # 1) get fstar of current_node_set
        fstar = get_fstar(current_node_set, hg)
        # 2) Delete non F-/B- edges from fstar
        fstar = keep_edges(fstar, hg, edge_type=SEARCH_TYPE)
        # 2.1) If fstar is empty then return NO FEASIBLE SOLUTION
        if fstar == set():
            logger.info("NO EDGE TO CONTINUE FOUND - STOPPING")
            return p, False
        # 3) choose one edge in fstar (insert ACO here)
        # next_edge = random.sample(set(fstar), 1)[0]
        # TODO used ACO intead of random search
        next_edge = phero_choice_single_node(fstar, hg, IGNORE_PHERO)
        # 3.1) [possibly improve solution using local search]
        # TODO improve solution using local search
        # 4) If exists node in H(edge): node has already been visited, then edge = cycle_escape()
        p_node_set = p.get_node_set()
        head = hg.get_hyperedge_head(next_edge)
        if p_node_set.intersection(head) != set():
            logger.info("I walked through a cycle because I am again visiting node: {0}".format(p_node_set.intersection(head)))
            p, next_edge_p_id = add_edge(p, hg, next_edge)
            edge_added_match[next_edge_p_id] = next_edge
            p, next_edge_id_p, edge_added_match = loop_escape_generic(p,hg,next_edge_p_id, edge_added_match, SEARCH_TYPE)
            if next_edge_id_p == None:
                logger.info("No solution found while escaping from cycle")
                return p, False
            head = p.get_hyperedge_head(next_edge_id_p)
        else:
            # 5) add egde to optimal path
            p, next_edge_p_id = add_edge(p,hg,next_edge)
            # [Save edge_id in p in hash table]
            edge_added_match[next_edge_p_id] = next_edge
            # 6) if end_node in current_node_set then return_p
        if end_node in head:
            logger.info("Found END NODE!")
            STOP = True
        else:
            logger.debug("Exploring edge - head: {0} - {1}".format(next_edge, head))
            current_node_set = head
    return p, True

def loop_escape_generic(p:DirectedHypergraph, hg:DirectedHypergraph, next_edge_p, edge_added_match, SEARCH_TYPE = "BF"):
    logger = logging.getLogger(__name__)  # get the logger
    ESCAPE_FOUND = False
    blacklist = set()
    # while escape edge not found
    while not ESCAPE_FOUND:
        # 1) save tail of current_edge in p
        tail = p.get_hyperedge_tail(next_edge_p)
        # 2) remove current_edge from p
        # TODO (update edge_added_match, cleanup p if needed)
        p.remove_hyperedge(next_edge_p)
        # 2.1) if p has no edges, then NO feasible solution can be found (return p = None)
        if p.get_hyperedge_id_set() == set():
            logger.info("NO ESCAPE FOUND AND NO EDGES LEFT!")
            return p, None, edge_added_match
        # 3) get fstar of tail
        fstar = get_fstar(tail, hg)
        # 4) keep only B/F/BF edges in tail and remove edge already used
        fstar = keep_edges(fstar, hg, edge_type=SEARCH_TYPE)
        # 4.1) update blacklist and compare to fstar
        blacklist.update(next_edge_p)
        #fstar.remove(edge_added_match[next_edge_p])
        fstar.difference_update(blacklist)
        # 5) if exists edge in tail such that: edge != current_edge (use HG edge ids), then escape edge found
        if fstar != set():
            logger.info("Escape edge found!")
            ESCAPE_FOUND = True
            #   5.1) add edge to p (save edge_id_in_p to be returned
            escape_edge = random.sample(set(fstar), 1)[0]
            p, escape_edge_p = add_edge(p,hg,escape_edge)
            logger.debug("Escape edge ids in hg and p: {0}, {1}".format(escape_edge, escape_edge_p))
            # cleanup edge_addeed_match
            del edge_added_match[next_edge_p]
            edge_added_match[escape_edge_p] = escape_edge
            #   5.2) return p, edge_id_in_pm edge_added_match
            return p, escape_edge_p, edge_added_match
        else:
        # 6) else: continue cycle
            bstar = set()
            for node in tail:
                bstar = bstar.union(p.get_backward_star(node))
            if len(bstar) == 1:
                next_edge_p = random.sample(bstar, 1)[0]
                logger.info("Backtracking in p on edge: {0}".format(next_edge_p))
            else:
                logger.warning("I returned back to the start node, no tail to escape here")
                return p, None, edge_added_match
    pass



def is_B_edge(hg:DirectedHypergraph, edge):
    return len(hg.get_hyperedge_head(edge)) == 1

def is_F_edge(hg:DirectedHypergraph, edge):
    return len(hg.get_hyperedge_tail(edge)) == 1




"""
NEW METHODS FOR MOACO
"""

def extend_phero_matrix(H:DirectedHypergraph):
    """
    Adds dimension 1 and 2 phero information to a hypergraph H
    :param H: 
    :return: 
    """
    Hext = DirectedHypergraph()
    edges = H.get_hyperedge_id_set()
    for edge in edges:
        tail, head, attrs = H.get_hyperedge_tail(edge), H.get_hyperedge_head(edge), H.get_hyperedge_attributes(edge)
        phero = H.get_hyperedge_attribute(edge, 'phero')
        attrs['phero_01'], attrs['phero_02'] = phero, phero
        Hext.add_hyperedge(tail, head, attrs)
    return Hext


""" ======================================="""
""" TEST HYPERGRAPHS """
""" ======================================="""


def test_hg_loop_F():
    HG = DirectedHypergraph()
    HG.add_node("A", source=True)
    HG.add_node("H", sink=True)
    HG.add_nodes(["A", "C", "D", "F", "G", "J", "K", "M", "N"], {'sink': False})
    HG.add_nodes(["C", "D", "F", "G", "H","J", "K", "M", "N"], {'source': False})
    #print_hg_std_out_only(HG)
    # HG.add_hyperedge(["A"], ["B"], phero=0)
    # HG.add_hyperedge(["A"], ["E"], phero=0)
    HG.add_hyperedge(["A"], ["D", "C"], phero=0)
    HG.add_hyperedge(["C"], ["F", "G"], phero=0)
    HG.add_hyperedge(["G"], ["J", "K"], phero=0)
    HG.add_hyperedge(["K"], ["M", "N"], phero=0)
    HG.add_hyperedge(["K"], ["H"], phero=0)
    HG.add_hyperedge(["N"], ["C"], phero=0)
    return HG

def test_hg_loop_B():
    HG = DirectedHypergraph()
    HG.add_node("A", source=True)
    HG.add_node("H", sink=True)
    HG.add_nodes(["A", "B", "C", "D", "E", "F", "G", "J", "K", "M", "N", "I"], {'sink': False})
    HG.add_nodes(["B", "C", "D", "E", "F", "G", "H","J", "K", "M", "N", "I"], {'source': False})
    print_hg_std_out_only(HG)
    #HG.add_hyperedge(["A"], ["B"], phero=0)
    #HG.add_hyperedge(["A"], ["E"], phero=0)
    HG.add_hyperedge(["A", "B"], ["C"], phero=0)
    HG.add_hyperedge(["C"], ["K"], phero=0)
    HG.add_hyperedge(["C"], ["F"], phero=0)
    HG.add_hyperedge(["C", "D"], ["E"], phero=0)
    HG.add_hyperedge(["K", "J"], ["I"], phero=0)
    HG.add_hyperedge(["A", "B"], ["C"], phero=0)
    HG.add_hyperedge(["F", "E"], ["G"], phero=0)
    HG.add_hyperedge(["N", "F"], ["M"], phero=0)
    HG.add_hyperedge(["M"], ["H"], phero=0)
    HG.add_hyperedge(["M"], ["C"], phero=0)
    return HG

def test_hg_02():
    HG = DirectedHypergraph()
    HG.add_node("A", source=True)
    HG.add_node("H", sink=True)
    HG.add_nodes(["A", "B", "C", "D", "E", "F", "G", "X1", "X2", "X3"], {'sink': False})
    HG.add_nodes(["B", "C", "D", "E", "F", "G", "H", "X1", "X2", "X3"], {'source': False})
    print_hg_std_out_only(HG)
    HG.add_hyperedge(["A"], ["E"], phero=0)
    HG.add_hyperedge(["A"], ["D"], phero=0)
    HG.add_hyperedge(["A"], ["B", "C"], phero=0)
    HG.add_hyperedge(["B"], ["E"], phero=0)
    HG.add_hyperedge(["C"], ["F"], phero=0)
    HG.add_hyperedge(["C"], ["H"], phero=0)
    HG.add_hyperedge(["C", "D"], ["G"], phero=0)
    HG.add_hyperedge(["G"], ["H"], phero=0)
    HG.add_hyperedge(["E", "F"], ["H"], phero=0)
    HG.add_hyperedge(["A"], ["X1"], phero=0)
    HG.add_hyperedge(["X1"], ["X2", "X3"], phero=0)
    HG.add_hyperedge(["X1"], ["D"], phero=0)
    return HG

def test_hg_simple():
    HG = DirectedHypergraph()
    #HG.add_node("A", source=True)
    #HG.add_node("H", sink=True)
    HG.add_nodes(["A", "B", "C", "D", "E", "F"], {'sink': False})
    HG.add_nodes(["B", "C", "D", "E", "F"], {'source': False})
    print_hg_std_out_only(HG)
    HG.add_hyperedge(["A"], ["E"], phero=0)
    HG.add_hyperedge(["A"], ["D"], phero=0)
    HG.add_hyperedge(["A"], ["H", "C"], phero=0)
    HG.add_hyperedge(["B", "A"], ["F"], phero=0)
    return HG


def test_hg_simple2():
    HG = DirectedHypergraph()
    HG.add_hyperedge(["A"], ["B", "C", "D"], phero=0)
    HG.add_hyperedge(["E", "B", "C"], ["F"], phero=0)
    HG.add_hyperedge(["B", "C"], ["G"], phero=0)
    HG.add_hyperedge(["D", "H"], ["I"], phero=0)
    print_hg_std_out_only(HG)
    return HG

if __name__ == "__main__":
    # SET LOGGER
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    logger = logging.getLogger(__name__)
    # END SET LOGGER

    HG = test_hg_loop_F()
    # HG = test_hg_02()
    PRINT_ATTRS = True
    print_hg_std_out_only(HG, PRINT_ATTRS)
    print('\n \n')

    HGext = extend_phero_matrix(HG)
    print_hg_std_out_only(HGext, PRINT_ATTRS)








