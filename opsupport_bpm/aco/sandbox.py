import random
import logging

from halp.directed_hypergraph import DirectedHypergraph

class PathFinder:

    def __init__(self):
        pass

    def __init__(self,HG):
        self.hg = HG
        self.path_opt = DirectedHypergraph()

    def print_hg(self):
        self._print_hypergraph(self.hg)

    def print_path_opt(self):
        self._print_hypergraph(self.path_opt)

    def _print_hypergraph(self, hg:DirectedHypergraph):
        print("HYPERGRAPH...")
        node_set, edge_set  = hg.get_node_set(), hg.get_hyperedge_id_set()
        for node in node_set:
            print("NODE: {0} ATTRIBUTES: {1}".format(node, hg.get_node_attributes(node)))
        for edge in edge_set:
            print("EDGE: {0} {1} ==> {2}".format(edge, hg.get_hyperedge_tail(edge),
                                                                         hg.get_hyperedge_head(edge)))
        print("...DONE")

    def find_path_B(self):
        """
            aco searching for a B-hyperpath
            :param hg:
            :param ant_attributes:
            :param IGNORE_PHERO:
            :return:
            """
        logger = logging.getLogger(__name__)  # get the logger
        # get start and end node
        start_end = get_start_end_node(hg)
        start_node_set = start_end[0]
        end_node_set = start_end[1]
        start_node = random.sample(set(start_node_set), 1)[0]
        logger.debug("Found START node set: {0}".format(start_node_set))
        logger.debug("Chosen START node (if many available): {0}".format(start_node))
        logger.debug("Found END node set: {0}".format(end_node_set))
        # ASSUMPTION: only one end node
        end_node = end_node_set[0]
        # count number of nodes to process
        number_of_nodes = len(hg.get_node_set())
        logger.debug("Number of nodes to process: {0}".format(number_of_nodes))

        p = DirectedHypergraph()

        nodes_to_process = []
        nodes_to_process.append(start_node)
        i = 0

        STOP = False

        waiting = {}

        while not STOP:
            current_node = nodes_to_process[i]
            current_node_set = [current_node]
            # current_node_set = set()
            # current_node_set.update({current_node})
            # get forward star
            curr_fstar = hg.get_forward_star(current_node)
            # choose based on pheromone
            if curr_fstar != []:
                # choose based on pheromone
                # next_edge = phero_choice_single_node(curr_fstar, hg, IGNORE_PHERO)
                # UPDATE WITH ACTUAL PHEROMONE CALL!!!
                next_edge = random.sample(set(curr_fstar), 1)[0]
                logger.debug("Next edge chosen using pheromone: {0}".format(next_edge))
            else:
                # stuck! no edges are available to continue search
                logger.debug("This ant is stuck, no available edges to walk!")
                pass
            # do the synch if needed
            if next_edge not in hg.get_successors(current_node_set):
                logger.debug("==> I am in a hyperedge, check waiting...")
                # look if there is a match waiting to happen
                if next_edge in waiting.keys():
                    # add current node
                    content = waiting[next_edge]
                    content.append(current_node)
                    waiting[next_edge] = content
                    current_tail = hg.get_hyperedge_tail(next_edge)
                    if set(waiting[next_edge]) == set(current_tail):
                        logger.debug("+++ +++ +++ Waiting edge found, add hyperedge")
                        p = add_edge(p, hg, next_edge)
                        # delete entry in waiting
                        del waiting[next_edge]
                # node is extreme of a hyperarc, we have to stop and wait for a match
                else:
                    logger.debug("+++ +++ +++ I am the first ant here, put myself to wait")
                    waiting[next_edge] = []
                    content = waiting[next_edge]
                    content.append(current_node)
                    waiting[next_edge] = content
            else:
                # single node is tail of edge, so we can add it to optimal path
                # add egde, tail and head to optimal path p
                logger.debug(
                    "Adding new edge to current path ({0}, {1}, {2})".format(next_edge,
                                                                             hg.get_hyperedge_tail(next_edge),
                                                                             hg.get_hyperedge_head(next_edge)))
                p = add_edge(p, hg, next_edge)
            # move on (add nodes to process and increment i:
            # 1) add nodes in H(next_edge) to nodes_to_process
            nodes = hg.get_hyperedge_head(next_edge)

            # terminating condition
            if end_node in nodes:
                if waiting == {}:
                    STOP = True
                    p = add_edge(p, hg, next_edge)
                    # logger.debug("Found BF-path: {0}".format(p.is_BF_hypergraph()))
                if waiting != {}:
                    STOP = True
                    # delete unwanted edges
                    p = add_edge(p, hg, next_edge)
                    # p = adjust_p_for_B_paths(p, end_node, start_node)

            nodes_to_process.extend(nodes)
            # increase i
            i += 1
            # check terminating condition
            # if terminating, adjust p removing undesired edges

        return p

    def find_path_F(self):
        pass

    def find_path_BF(self):
        pass



if __name__ == "__main__":
    HG = DirectedHypergraph()
    HG.add_node("A", source=True)
    HG.add_node("H", sink=True)
    HG.add_nodes(["A", "B", "C", "D", "E", "F", "G"], {'sink': False})
    HG.add_nodes(["B", "C", "D", "E", "F", "G", "H"], {'source': False})
    HG.add_hyperedge(["A"], ["B"], phero=0)
    HG.add_hyperedge(["A"], ["D"], phero=0)
    HG.add_hyperedge(["A"], ["B", "C"], phero=0)
    HG.add_hyperedge(["B"], ["E"], phero=0)
    HG.add_hyperedge(["C"], ["F"], phero=0)
    HG.add_hyperedge(["C"], ["H"], phero=0)
    HG.add_hyperedge(["C", "D"], ["G"], phero=0)
    HG.add_hyperedge(["G"], ["H"], phero=0)
    HG.add_hyperedge(["E", "F"], ["H"], phero=0)

    PF = PathFinder(HG)
    PF.print_hg()