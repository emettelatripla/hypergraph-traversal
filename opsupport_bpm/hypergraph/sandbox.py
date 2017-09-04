import random, logging, sys
from halp.directed_hypergraph import DirectedHypergraph
from halp.utilities.directed_matrices import get_head_incidence_matrix, get_tail_incidence_matrix, get_hyperedge_id_mapping, get_node_mapping
from opsupport_bpm.aco.aco_pheromone import final_phero_update
from opsupport_bpm.aco.aco_pheromone import partial_phero_update
from opsupport_bpm.aco.aco_pheromone import phero_choice_single_node
from opsupport_bpm.aco.aco_utility import calculate_utility
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only
from halp.algorithms.directed_paths import is_connected
from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_B_path, aco_search_F_path, aco_search_BF_path, aco_search_generic_path

def create_hg_from_file(file_name):
    HG = DirectedHypergraph()
    file = open(file_name, "r")

    node_id_set = []
    # create node id set
    for line in file.readlines():
        line_str = line.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
            if int(element) not in node_id_set:
                node_id_set.append(int(element))
    range = len(node_id_set) - 1
    logger.debug(node_id_set)
    ran_source = random.randrange(0, range, 1)
    ran_sink = random.randrange(0, range, 1)
    while ran_source == ran_sink:
        ran_source = random.randrange(0, range, 1)
    i = 0
    for node_id in node_id_set:
        if i == ran_source:
            HG.add_node(node_id, {'source': True, 'sink': False})
            logger.debug("Found source node: {0}".format(node_id))
        elif i == ran_sink:
            HG.add_node(node_id, {'source': False, 'sink': True})
            logger.debug("Found sink node: {0}".format(node_id))
        else:
            HG.add_node(node_id, {'source': False, 'sink': False})
        i += 1

    file.seek(0)

    for line2 in file.readlines():
        line_str = line2.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
        range = len(line_num) - 1
        split = random.randrange(0,range, 1)
        if split == 0:
            split = 1
        tail, head = line_num[:split], line_num[split:]
        # generating edge
        HG.add_hyperedge(tail, head, {'phero' : 0})

    file.close()

    return HG

def create_B_hg_from_file(file_name):
    HG = DirectedHypergraph()
    file = open(file_name, "r")

    node_id_set = []
    # create node id set
    for line in file.readlines():
        line_str = line.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
            if int(element) not in node_id_set:
                node_id_set.append(int(element))
    range = len(node_id_set) - 1
    logger.debug(node_id_set)
    ran_source = random.randrange(0, range, 1)
    ran_sink = random.randrange(0, range, 1)
    while ran_source == ran_sink:
        ran_source = random.randrange(0, range, 1)
    i = 0
    for node_id in node_id_set:
        if i == ran_source:
            HG.add_node(node_id, {'source': True, 'sink': False})
            logger.debug("Found source node: {0}".format(node_id))
        elif i == ran_sink:
            HG.add_node(node_id, {'source': False, 'sink': True})
            logger.debug("Found sink node: {0}".format(node_id))
        else:
            HG.add_node(node_id, {'source': False, 'sink': False})
        i += 1

    file.seek(0)

    for line2 in file.readlines():
        line_str = line2.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
        tail, head = line_num[:-1], line_num[-1:]
        # generating edge
        HG.add_hyperedge(tail, head, {'phero' : 0})

    file.close()

    return HG


def create_F_hg_from_file(file_name):
    HG = DirectedHypergraph()
    file = open(file_name, "r")

    node_id_set = []
    # create node id set
    for line in file.readlines():
        line_str = line.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
            if int(element) not in node_id_set:
                node_id_set.append(int(element))
    range = len(node_id_set) - 1
    logger.debug(node_id_set)
    ran_source = random.randrange(0, range, 1)
    ran_sink = random.randrange(0, range, 1)
    while ran_source == ran_sink:
        ran_source = random.randrange(0, range, 1)
    i = 0
    for node_id in node_id_set:
        if i == ran_source:
            HG.add_node(node_id, {'source': True, 'sink': False})
            logger.debug("Found source node: {0}".format(node_id))
        elif i == ran_sink:
            HG.add_node(node_id, {'source': False, 'sink': True})
            logger.debug("Found sink node: {0}".format(node_id))
        else:
            HG.add_node(node_id, {'source': False, 'sink': False})
        i += 1

    file.seek(0)

    for line2 in file.readlines():
        line_str = line2.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
        tail, head = line_num[:1], line_num[1:]
        # generating edge
        HG.add_hyperedge(tail, head, {'phero' : 0})

    file.close()

    return HG


def create_BF_hg_from_file(file_name):
    HG = DirectedHypergraph()
    file = open(file_name, "r")

    node_id_set = []
    # create node id set
    for line in file.readlines():
        line_str = line.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
            if int(element) not in node_id_set:
                node_id_set.append(int(element))
    range = len(node_id_set) - 1
    logger.debug(node_id_set)
    ran_source = random.randrange(0, range, 1)
    ran_sink = random.randrange(0, range, 1)
    while ran_source == ran_sink:
        ran_source = random.randrange(0, range, 1)
    i = 0
    for node_id in node_id_set:
        if i == ran_source:
            HG.add_node(node_id, {'source': True, 'sink': False})
            logger.debug("Found source node: {0}".format(node_id))
        elif i == ran_sink:
            HG.add_node(node_id, {'source': False, 'sink': True})
            logger.debug("Found sink node: {0}".format(node_id))
        else:
            HG.add_node(node_id, {'source': False, 'sink': False})
        i += 1

    file.seek(0)

    for line2 in file.readlines():
        line_str = line2.split(" ")
        line_num = []
        for element in line_str:
            element.rstrip()
            line_num.append(int(element))
        if random.random() > 0.5:
            # create F- edge
            tail, head = line_num[:1], line_num[1:]
        else:
            tail, head = line_num[:-1], line_num[-1:]
        # generating edge
        HG.add_hyperedge(tail, head, {'phero' : 0})

    file.close()

    return HG

def check_properties(hg:DirectedHypergraph):
    print("Is BF-Hypergraph? {0}".format(hg.is_BF_hypergraph()))
    print("Is B-Hypergraph? {0}".format(hg.is_B_hypergraph()))
    print("Is F-Hypergraph? {0}".format(hg.is_F_hypergraph()))
    node_set = hg.get_node_set()
    for i in range(0,30, 1):
        start = random.sample(node_set,1)[0]
        end = random.sample(node_set, 1)[0]
        print("Is {0} connected to {1}: {2}".format(start, end, is_connected(hg,start,end)))






if __name__ == "__main__":
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    logger = logging.getLogger(__name__)

    #HG = create_hg_from_file("hg.dat")
    #print_hg_std_out_only(HG)

    # check_properties(HG)

    # p, sol = aco_search_BF_path(HG, None)
    for i in range(10):
        HG = create_hg_from_file("hg.dat")
        p, sol = aco_search_generic_path(HG, None)
        print("Solution found: {0}".format(sol))
        if sol:
            print("####### Found p; is B-path? {0}".format(p.is_B_hypergraph()))
            print("####### Found p; is F-path? {0}".format(p.is_F_hypergraph()))
            print("####### Found p; is BF-path? {0}".format(p.is_BF_hypergraph()))
            print_hg_std_out_only(p)