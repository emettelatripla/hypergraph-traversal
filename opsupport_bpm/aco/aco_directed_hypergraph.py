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



# node_set: the source node set (only one node in process models)
# hg: the process model (hypergraph)
#ANT_NUM number of ants in one colony
#COL_NUM number of colonies
#tau: pheromone evaporation coefficient 
#W_UTILITY: weights of the utility function
def aco_algorithm(start_node_set, hg, ANT_NUM, COL_NUM, tau, W_UTILITY):
    '''
    WORKS ONLY WITH RECURSIVE ACO SEARCH !!!
    Main procedure for aco optimisation of hypergraph
    :param start_node_set: the set of starting nodes
    :param hg: hypergraphs
    :param ANT_NUM: number of ants in one colony
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
        for node in start_node_set:
            p.add_node(node, hg.get_node_attributes(node))
        while ant < ANT_NUM:
            logger.info("----- Processing COLONY n. {1}, ANT n. {0} -----------------".format(ant, col))
            p = DirectedHypergraph()
            #add source node to optimal path (and its attributes)
            for node in start_node_set:
                p.add_node(node, hg.get_node_attributes(node))
            """ call aco_search on p"""
            # recursive
            visited = []
            p = aco_search(p, hg, start_node_set, 0, visited)
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
    logger.info("********** OPTIMAL PATH FOUND ******************")
    print_hg_std_out_only(p_opt)
    logger.info("****** UTILITY: "+str(calculate_utility(p_opt, W_COST, W_TIME, W_QUAL, W_AVAIL)))
    logger.info("***********************************************")
    return p_opt


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
            p = aco_search_nonrec(hg)
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

""" used by escape from loop to delete all nodes not connected after deleting p_back_edge"""
def safe_remove_edge(p, p_back_edge):
    '''
    remove an edge from a path
    :param p: path
    :param p_back_edge: edge
    '''
    #logger = logging.getLogger(__name__)
    #back_tail = p.get_hyperedge_tail(p_back_edge)
    #back_head = p.get_hyperedge_head(p_back_edge)
    # we are going back, so only head may remain disconnected
    p.remove_hyperedge(p_back_edge)
    #for node in back_head:
    #    logger.debug("Undoing edge {1}, removing node from path: {0}".format(node,p_back_edge))
    #    p.remove_node(node)
    return p

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
    delete_nodes_to_process = []
    safe_node_found = False
    # check if we can escape from current node
    curr_node_set = []
    curr_node_set.append(current_node)
    outgoings = hg.get_successors(curr_node_set)
    logger.debug("....successors of current node {1}: {0}".format(outgoings,current_node))
    outgoings = outgoings.remove(next_edge)
    if not outgoings is None:
        outgoings.difference_update(used_edges)
    if not outgoings is None:
        logger.debug("..... Current node {0} has possible escape edge")
        new_edge = random.sample(set(outgoings),1)[0]
        used_edges.append(new_edge)
        logger.debug("..... Current node {0} has posible escape edge {1}".format(current_node,new_edge))
        # TO DO: prepare the output to return
        #p.remove_hyperedge(next_edge)
        #delete_nodes_to_process.append(next_edge)
        #p.remove_node(current_node)
        #delete_nodes_visited.append(current_node)
        safe_node = current_node
        safe_node_found = True
        return new_edge, p, current_node, delete_nodes_visited
    while not safe_node_found:
        # go back one node (with get predecessors - returns a set!)
        curr_node_set = []
        curr_node_set.append(current_node)
        prec_edge_set = p.get_predecessors(curr_node_set)
        prec_edge_set.difference_update(used_edges)
        # choose edge to back
        p_back_edge = random.sample(set(prec_edge_set),1)[0]
        # get id of edge in hg
        tail = p.get_hyperedge_tail(p_back_edge)
        head = p.get_hyperedge_head(p_back_edge)
        back_edge = hg.get_hyperedge_id(tail,head)
        logger.debug("...... Going back using edge: {0} in HG [{1} in current path]".format(back_edge,p_back_edge))
        current_node = p.get_hyperedge_tail(p_back_edge)
        logger.debug("...... Now in node {0}, looking for an escape".format(current_node))
        # remove edge used to go back
        # look for other forward edges
        forward_edges = hg.get_successors(current_node)
        logger.debug("Forward edges to choose from: {0}".format(forward_edges))
        # remove edge used to go back from path p
        logger.debug("Removing hyperedge from path: ({0}, {1}, {2}) ".format(p_back_edge,p.get_hyperedge_tail(p_back_edge),p.get_hyperedge_head(p_back_edge)))
        p = safe_remove_edge(p, p_back_edge)
        for node in current_node:
            delete_nodes_visited.append(node)
        #forward_edges.remove(back_edge)
        if not forward_edges == set():
            new_edge = random.sample(set(forward_edges),1)[0]
            logger.debug("...... escape found! Edge: {0}".format(new_edge))
            safe_node = current_node
            safe_node_found = True
            # TO-DO prepare return   
            return new_edge, p, current_node, delete_nodes_visited
    return None


def aco_search_nonrec(hg):
    '''
    NON RECURSIVE
    non-recursive version of aco search (breadth-first exploring of the hypergraph)
    simulates the behaviour of one single ant and returns the optimal path discovered by that ant
    :param hg: hypergraph
    '''
     
    logger = logging.getLogger(__name__)
    start_end = get_start_end_node(hg)
    # assumption: only ONE START event and ONE END event
    start_node_set = start_end[0]
    end_node_set = start_end[1]
    logger.debug("Found START node: {0}".format(start_node_set))
    logger.debug("Found END node: {0}".format(end_node_set))
    number_of_nodes = len(hg.get_node_set())
    logger.debug("Number of nodes to process: {0}".format(number_of_nodes))
    # array of nodes to process
    nodes_to_process = []
    # randomly choose one start noe
    start_node = random.sample(set(start_node_set),1)[0]
    # ASSUMPTION: only one end node
    end_node = end_node_set[0]
    nodes_to_process.append(start_node)
    nodes_visited = []
    used_edges = []
    
    # begin looking forward...
    p = DirectedHypergraph()
    stop = False
    i = 0
    current_node = nodes_to_process[0]
    waiting = {}
    # to escape, isolate the nodes already visited because of waiting
    nodes_visited_waiting = []
    while not stop:
        logger.debug("============= VISITING NEXT NODE: --- {0} ---- ========================".format(current_node))
        f_edge_set = hg.get_forward_star(current_node)
        # choose next edge
        # TBC: create phero_choice single node function
        next_edge = phero_choice_single_node(f_edge_set, hg)
        logger.debug("Next edge returned: {0}".format(next_edge))
        # look in the head of next hedge
        next_head = hg.get_hyperedge_head(next_edge)
        # if a node in next edge has already been visited, then escape!
        escape = False
        for node in next_head:
            if node in nodes_visited:
                logger.debug("Node {0}; Possible escape needed, should investigate more...".format(node))
                # check if in p exist an edge with node as tail
                #logger.debug("Forward star is {0}, node is {1}".format(p.get_forward_star(node),node))
                # check if node is head of waiting hyperedges
                waiting_head = False
                waiting_edges = waiting.keys()
                head = []
                head.append(node)
                for edge in waiting_edges:
                    if hg.get_hyperedge_head(edge) == head:
                        waiting_head = True
                if waiting_head or node == end_node:
                    # I know I am ina loop now, must escape!
                    logger.debug("...I was not in a real loop, continue :)")
                else:
                    logger.debug("...I am in a LOOP, must ESCAPE!")
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
                for node in delete_nodes:
                    logger.debug("Removing node from list of visited nodes: {0}".format(node))
                    nodes_visited.remove(node)
                logger.debug(".... #Escape terminated!")
                logger.debug(".... current node: {0}".format(current_node))
            # ESCAPE TB TB TB 
        # wait for matches if its hyperedge
        """ wait for matches TBC"""
        logger.debug("Successors of current node {0}: {1}".format(current_node,hg.get_successors(current_node)))
        # need a set to use get_successors
        current_node_set = set()
        current_node_set.update({current_node})
        logger.debug("Current node set: {0}".format(current_node_set))
        if next_edge not in hg.get_successors(current_node_set):
            logger.debug("+++ +++ +++ I am in a hyperedge, check waiting...")
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
    return p
        
        
    
       
    





""" recursive version of aco_search """
#start_node_set: current position (can be a set of nodes) in the search
#p: current path
#hg: process model
# depth : just to pretty print with indentation
# list of nodes visited so far
def aco_search(p, hg, node_set, depth, visited):
    '''
    RECURSIVE VERSION OF ACO SEARCH !!! DOES NOT WORK ON HYPERGRAPHS WITH LOOPS
    :param p: current (partial) optimal path
    :param hg: hypergraph
    :param node_set: current set of nodes explored by ant
    :param depth: levels of recursion
    :param visited: set of visited nodes in aco
    '''
    logger = logging.getLogger(__name__)
    visited = []
    visited.append(node_set)
    #select next hyperedge from node according to pheromone distribution
    edge_set = set()
    for node in node_set:
        edge_set = set.union(edge_set,hg.get_forward_star(node))
    #select edge based on value of pheromone attribute (and add h_edge to current solution
    next_edge = phero_choice(edge_set, hg, visited)
    """ if phero choice returns None, then it means "go-back" """
    """ go back until you find an edge that you can follow """
    while next_edge == None:
        # get the list of incoming edges
        prec_edges = p.get_predecessors(node_set)
        logger.debug("+++ NODE SET: {0} ...".format(str(node_set)))
        # choose one randomly
        prec_edge = random.sample(prec_edges,1)
        logger.debug("+++ Go back using edge: {0} ...".format(str(prec_edge[0])))
        # get the tail and call phero choice without the prec_edge chosen!
        search_tail = p.get_hyperedge_tail(prec_edge[0])
        logger.debug("+++ Going back, visiting node(s): {0} ...".format(str(search_tail)))
        # get the edges outgoing from tail (forward star)
        search_edges = hg.get_successors(search_tail)
        # remove prec_edge from forward star
        logger.debug("+++ Going back: remove edge {0} from edge list {1} ...".format(str(prec_edge[0]), str(search_edges)))
        search_edges.remove(prec_edge[0])
        logger.debug("+++ Going back using edge: {0} ...".format(str(search_edges)))
        # call phero choice
        if search_edges == set():
            # go back, no available edges to explore
            next_edge = None
            logger.debug("+++ Going back one level more, no edges available".format(str(next_edge)))
        else:
            next_edge = phero_choice(search_edges, hg, visited)
            logger.debug("+++ Found new unexplored edge: {0} ...".format(str(next_edge)))
        if next_edge == None:
            #get ready to loop again
            node_set = search_tail
        # (remember to loop back if no prec_edges are available to be chosen)
    tail = hg.get_hyperedge_tail(next_edge)
    head = hg.get_hyperedge_head(next_edge)
    attrs = hg.get_hyperedge_attributes(next_edge)
    #print_hyperedge(next_edge, hg)
    #get the id of the next_edge and use it as id of new edge in p
    edge_id = next_edge
    attrs.update({'id' : edge_id})
    phero_value = attrs['phero']
    #add selected hyperedge/node to p
    p.add_hyperedge(tail, head, attrs)
    next_head = hg.get_hyperedge_head(next_edge)
    for node in next_head:
        p.add_node(node, hg.get_node_attributes(node))
    #must add also all nodes in the tail (i fnot already)
    next_tail = hg.get_hyperedge_tail(next_edge)
    for node in next_tail:
        p.add_node(node, hg.get_node_attributes(node))
    #if new node added is sink, then return p
    isSink = False
    print(1*depth*"-"+"+++ nodes to call: {0}".format(next_head))
    logger.debug("~~~~ Inspecting head of chosen edge - phero value: {0}".format(phero_value))
    for node in next_head:
        if hg.get_node_attribute(node,'sink') == True:
            #print(2*depth*"-"+"--- STOP ---: {0}".format(str(node)))
            isSink = True
            logger.debug("~~~~ STOPPING AT: {0}, {1}".format(node, hg.get_node_attribute(node,'sink')))
        #if isSink == False:
        else:
            #print(2*depth*"-"+"CALLING ACO SEARCH on: {0}".format(str(node)))
            #p = aco_search(p, hg, next_head, depth+1)
            node_s = []
            node_s.append(node)
            # store the node as visited
            #print(str(depth+1))
            # avoid loops by chekcing if node has been visited already
            #if node_s not in visited:
            p = aco_search(p, hg, node_s, depth+1, visited)
    #else recursive call
    return p



