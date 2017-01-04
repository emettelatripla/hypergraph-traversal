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

from halp.directed_hypergraph import DirectedHypergraph 
from opsupport_bpm.aco.aco_pheromone import final_phero_update
from opsupport_bpm.aco.aco_pheromone import partial_phero_update
from opsupport_bpm.aco.aco_pheromone import phero_choice
from opsupport_bpm.aco.aco_pheromone import phero_choice_single_node
from opsupport_bpm.aco.aco_utility import calculate_utility
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only

import requests


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
            
        
        

""" THIS WORKS WITH NO RECURSION ACO SEARCH !!!"""
def aco_algorithm_norec(hg, ANT_NUM, COL_NUM, tau, W_UTILITY):
    '''
    NON RECURSIVE ACO
    Main procedure for aco optimisation of hypergraph
    :param hg: hypergraph
    :param ANT_NUM: number of ants per colony
    :param COL_NUM: number of colonies
    :param tau: pheromone evaporation coefficient
    :param W_UTILITY: dictionary of utility weights, e.g. (cost : 0.2, avail : 0.2, qual : 0.2, time : 0.4)
    '''
    # check start and end nodes in hg
    logger = logging.getLogger(__name__)
    #logger.debug("Start and end node found, begin optimisation: {0} - {1}".format(start_node,end_node))
    #set the values of the utility function weights
    W_COST = W_UTILITY['cost']
    W_AVAIL = W_UTILITY['avail']
    W_QUAL = W_UTILITY['qual']
    W_TIME = W_UTILITY['time']
    #setup the logger
    #logging.basicConfig(filename='aco.log',level=logging.INFO)
    #currently optimal path
    p_opt = DirectedHypergraph()
    utility_opt = 0.0
    #counters for colony
    col = 0
    while col < COL_NUM:
        #counter for ant number
        ant = 0
        logger.info("--- Processing COLONY n. {0} -------------------".format(col))
        #h_graph to store partial pheromone update
        hg_phero = hg.copy()
        #do something
        p = DirectedHypergraph()
        #add source node to optimal path (and its attributes)
        #for node in start_node_set:
            #p.add_node(node, hg.get_node_attributes(node))
        while ant < ANT_NUM:
            logger.info("----- Processing COLONY n. {1}, ANT n. {0} -----------------".format(ant, col))
            p = DirectedHypergraph()
            """ call aco_search on p"""
            # recursive
            #visited = []
            #p = aco_search(p, hg, start_node_set, 0, visited)

            # SET ATTRIBUTE OF THIS ANT
            ant_attrs = None

            p = aco_search_nonrec(hg, ant_attrs)
            # non recursive
            #p = aco_search_norec(p, hg, start_node_set)
            #PRINT CURRENT OPTIMAL PATH
            print_hg_std_out_only(p)
            #calculate utility of p
            utility = calculate_utility(p, W_COST, W_TIME, W_QUAL, W_AVAIL)
            #do partial pheromone update
            partial_phero_update(hg_phero, p, W_COST, W_TIME, W_QUAL, W_AVAIL)
            #check if p is better than current optimal solution
            #update if p is optimal
            logger.debug("-------- Utility of current path: {0} ----------------------".format(utility))
            logger.debug("-------- Current OPTIMAL UTILITY: {0} ----------------------".format(utility_opt))
            if utility > utility_opt:
                utility_opt = utility
                p_opt = p
                logger.info("----------------- ***** optimal path updated!!! *****---------------")
            ant = ant + 1
            #pheromone update
            #TBC TBC
        col = col + 1
        #actual pheromone update after processing an entire colony
        final_phero_update(hg, p_opt, tau)
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
    p.add_hyperedge(tail_next_edge, head_next_edge, phero = phero_next_edge, id = edge, name = edge)
    return p



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


def aco_search_nonrec(hg, ant_attributes):
    '''
    NON RECURSIVE
    non-recursive version of aco search (breadth-first exploring of the hypergraph)
    simulates the behaviour of one single ant and returns the optimal path discovered by that ant

    Extended with SMARTCHOICE

    :param hg: hypergraph
    '''

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

        # choose next edge based on smartchoice or pheromone distribution
        next_edge = None
        is_smartchoice = hg.get_node_attribute(current_node, 'smartchoice')
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
                # call the service
                response = requests.get(service_uri)
                ret_value = response.json()['ret_value']
                logger.debug("returned value: {0}".format(ret_value))
                # decide next edge based on the returned value
                edge_list = hg.get_node_attribute(current_node, 'opt_dict')
                next_edge = edge_list[ret_value]
                logger.debug("==> Next edge chosen (using smart_service) is: {0}".format(next_edge))
        else:
            next_edge = phero_choice_single_node(f_edge_set, hg)
            logger.debug("==> Next edge chosen using traditional pheromone: {0}".format(next_edge))
        # check if next_edge chosen with pheromone is different
        # REMOVE FOR SIMULATION
        if is_smartchoice:
            phero_edge = phero_choice_single_node(f_edge_set, hg)
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
                    p = add_edge(p,hg, next_edge)
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
            p = add_edge(p,hg,next_edge)
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
    return p
        





