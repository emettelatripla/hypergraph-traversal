import random, logging, sys
from halp.directed_hypergraph import DirectedHypergraph
import copy

from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only
from halp.algorithms.directed_paths import is_connected

def find_all(H:DirectedHypergraph, source_nodes):
    edge_set = H.get_hyperedge_id_set()
    x = {}
    for edge in edge_set:
        x[edge] = H.get_hyperedge_tail(edge)
    v = set(source_nodes)
    d = set(source_nodes)
    f = []
    while v != set():
        i = v.pop()
        d.add(i)
        for edge in edge_set:
            if i in x[edge]:
                x[edge].remove(i)
                if x[edge] == []:
                    f.append(edge)
                    for j in H.get_hyperedge_head(edge):
                        if j not in d:
                            v.add(j)
    return f

def nodes_in_head(H:DirectedHypergraph, edge_set):
    uk = set()
    for edge in edge_set:
        uk = uk.union(H.get_hyperedge_head(edge))
    return uk

def cleanup(H:DirectedHypergraph):
    node_set = set()
    for edge in H.get_hyperedge_id_set():
        node_set = node_set.union(H.get_hyperedge_head(edge))
        node_set = node_set.union(H.get_hyperedge_tail(edge))
    h_node_set = H.get_node_set()
    for node in h_node_set:
        if node not in node_set:
            H.remove_node(node)
    return H


def minimise(P: DirectedHypergraph, RF:DirectedHypergraph, source_nodes, target_nodes):
    f = find_all(P, source_nodes)
    P1  = P.copy()
    if not set(target_nodes).issubset(nodes_in_head(P, f)):
        P1 = DirectedHypergraph()
    else:
        h_edge_set = P.get_hyperedge_id_set()
        for edge in h_edge_set:
            if not RF.has_hyperedge(P.get_hyperedge_tail(edge), P.get_hyperedge_head(edge)):
                p_copy = P1.copy()
                p_copy.remove_hyperedge(edge)
                p_copy = cleanup(p_copy)
                f = find_all(p_copy, source_nodes)
                if set(target_nodes).issubset(nodes_in_head(P, f)):
                    P1.remove_hyperedge(edge)
                    P1 = cleanup(P1)
    return P1




def find_path_final(Hcopy, RNOT,RMUST, S, T, EN, F, level):
    # input()
    Fcopy = copy.deepcopy(F)
    RMUSTcopy = RMUST.copy()
    RNOTcopy = RNOT.copy()
    # print("\n" + level + " new call to find path: {0}".format(count))
    H1 = Hcopy.copy()
    for edge in RNOT.get_hyperedge_id_set():
        id = Hcopy.get_hyperedge_id(RNOT.get_hyperedge_tail(edge), RNOT.get_hyperedge_head(edge))
        H1.remove_hyperedge(id)
    H1 = cleanup(H1)
    Fh1 = find_all(H1, S)
    edge_set_must = RMUST.get_hyperedge_id_set()
    uk_edge_set = set(Fh1).union(set(edge_set_must))
    UK = Hcopy.copy()
    edge_set_h = Hcopy.get_hyperedge_id_set()
    for edge in edge_set_h:
        if edge not in uk_edge_set:
            UK.remove_hyperedge(edge)
    UK = cleanup(UK)
    P = minimise(UK, RMUST, S, T)
    if P.get_hyperedge_id_set() != set():
        level += "+"
        my_var.en.append(P)
        F = find_all(P, S)
        for r in reversed(F):
            if not RMUST.has_hyperedge(Hcopy.get_hyperedge_tail(r), Hcopy.get_hyperedge_head(r)):
                RNOT.add_hyperedge(Hcopy.get_hyperedge_tail(r), Hcopy.get_hyperedge_head(r))
                special_print_hg(RMUST, "RMUST", level, Hcopy)
                special_print_hg(RNOT, "RNOT", level, Hcopy)
                # count += 1
                print("F: {0}".format(F))
                print("r: {0}".format(r))
                F, RMUST = find_path_final(Hcopy, RNOT, RMUST, S, T, EN, F, level)
                RMUST.add_hyperedge(Hcopy.get_hyperedge_tail(r), Hcopy.get_hyperedge_head(r))
        return Fcopy,  RMUSTcopy
    special_print(my_var.en, "EN", level, Hcopy)
    return Fcopy,  RMUSTcopy




class my_var():
    en = []
    def __init__(self):
        pass
    def __init__(self, v):
        self.v = v
    def set(self, v):
        self.v = v
    def get(self):
        return self.v



def special_print(EN, name, level, Hcopy):

    for HG in EN:
        print(level+" Hypergraph: {0}".format(name))
        for edge in HG.get_hyperedge_id_set():
            print(level+" == {2} ==  : {0} ==> {1}".format(HG.get_hyperedge_tail(edge), HG.get_hyperedge_head(edge), Hcopy.get_hyperedge_id(HG.get_hyperedge_tail(edge), HG.get_hyperedge_head(edge))))

def special_print_hg(HG, name, level, Hcopy):
    print(level+" Hypergraph: {0}".format(name))
    for edge in HG.get_hyperedge_id_set():
        print(level+" == {2} ==  : {0} ==> {1}".format(HG.get_hyperedge_tail(edge), HG.get_hyperedge_head(edge), Hcopy.get_hyperedge_id(HG.get_hyperedge_tail(edge), HG.get_hyperedge_head(edge))))


def p(s):
    powerset = set()
    for i in range(2**len(s)):
        subset = tuple([x for j,x in enumerate(s) if (i >> j) & 1])
        powerset.add(subset)
    return powerset

#
# def smart_sort(F,P:DirectedHypergraph, source_nodes, target_nodes):
#     sorted_F = []
#     # find edge with target_nodes in head
#     for edge in F:
#         if set(target_nodes).issubset(P.get_hyperedge_head(edge)):
#             # sorted_F.append(edge)
#             sorted_F.insert(0, edge)
#     SOURCE_FOUND = False
#     while not SOURCE_FOUND:
#         tail = set()
#         for edge in sorted_F:
#             tail = tail.union(set(P.get_hyperedge_tail(edge)))
#         for edge in F:
#             if edge not in sorted_F:
#                 if set(P.get_hyperedge_head(edge)).issubset(tail):
#                     if edge not in sorted_F:
#                         #sorted_F.append(edge)
#                         sorted_F.insert(0, edge)
#                         source_nodes_power = p(source_nodes)
#                         source_nodes_power = source_nodes_power.difference(set())
#                         for s in source_nodes_power:
#                             if set(s).issubset(P.get_hyperedge_tail(edge)):
#                                 SOURCE_FOUND = True
#     return sorted_F

    # go back





def test_hg_02():
    HG = DirectedHypergraph()
    HG.add_node("A", source=True)
    HG.add_node("H", sink=True)
    HG.add_nodes(["A", "B", "C", "D", "E", "F", "G", "X1", "X2", "X3"], {'sink': False})
    HG.add_nodes(["B", "C", "D", "E", "F", "G", "H", "X1", "X2", "X3"], {'source': False})
    #print_hg_std_out_only(HG)
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
    HG.add_hyperedge(["F"], ["A"], phero=0)
    # HG.add_hyperedge(["X1"], ["X2", "X3"], phero=0)
    # HG.add_hyperedge(["X1"], ["D"], phero=0)
    return HG

def test_paper():
    HG = DirectedHypergraph()
    #print_hg_std_out_only(HG)
    HG.add_hyperedge(["v1", "v3"], ["v2"], phero=0)
    HG.add_hyperedge(["v2", "v5"], ["v3", "v6", "v8"], phero=0)
    HG.add_hyperedge(["v4"], ["v5", "v7"], phero=0)
    HG.add_hyperedge(["v7"], ["v8", "v9"], phero=0)
    HG.add_hyperedge(["v11"], ["v10"], phero=0)
    HG.add_hyperedge(["v10"], ["v3"], phero=0)
    HG.add_hyperedge(["v4", "v1"], ["v7", "v12"], phero=0)
    return HG

def test_process():
    HG = DirectedHypergraph()
    # print_hg_std_out_only(HG)
    HG.add_hyperedge(["start"], ["G"], phero=0)
    HG.add_hyperedge(["start"], ["A", "B"], phero=0)
    HG.add_hyperedge(["G"], ["H"], phero=0)
    HG.add_hyperedge(["H"], ["end"], phero=0)
    HG.add_hyperedge(["A"], ["C"], phero=0)
    HG.add_hyperedge(["B"], ["D"], phero=0)
    HG.add_hyperedge(["B"], ["E"], phero=0)
    HG.add_hyperedge(["C", "D"], ["end"], phero=0)
    HG.add_hyperedge(["C", "E"], ["end"], phero=0)
    return HG

def test_simple():
    HG = DirectedHypergraph()
    # print_hg_std_out_only(HG)
    HG.add_hyperedge(["start"], ["X"], phero=0)
    HG.add_hyperedge(["X"], ["Y"], phero=0)
    HG.add_hyperedge(["Y"], ["end"], phero=0)
    HG.add_hyperedge(["start"], ["A", "B"], phero=0)
    HG.add_hyperedge(["A", "B"], ["C"], phero=0)
    HG.add_hyperedge(["C"], ["end"], phero=0)
    return HG

def test_inf():
    HG = DirectedHypergraph()
    # print_hg_std_out_only(HG)
    HG.add_hyperedge(["start"], ["SF"], phero=0)
    HG.add_hyperedge(["start"], ["tau"], phero=0)
    HG.add_hyperedge(["tau"], ["n4"], phero=0)
    HG.add_hyperedge(["SF"], ["n4"], phero=0)
    HG.add_hyperedge(["n4"], ["tau0"], phero=0)
    HG.add_hyperedge(["tau0"], ["tau1", "n22"], phero=0)
    HG.add_hyperedge(["n22"], ["SAP"], phero=0)
    HG.add_hyperedge(["n22"], ["tautree8"], phero=0)
    HG.add_hyperedge(["SAP"], ["end"], phero=0)
    HG.add_hyperedge(["tautree8"], ["end"], phero=0)
    HG.add_hyperedge(["tau1"], ["end"], phero=0)
    return HG

if __name__ == "__main__":
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    logger = logging.getLogger(__name__)

    RF = DirectedHypergraph()

    # H = test_paper()
    # Hcopy = H.copy()
    # # findall = find_all(H, ["v1", "v4"])
    # # print(findall)
    # # for i in range(len(findall)):
    # #     print("edge {0} {1} ==> {2}".format(findall[i], H.get_hyperedge_tail(findall[i]), H.get_hyperedge_head(findall[i])))
    # # minimise = minimise(H, RF, ["v1", "v4"], ["v8"])
    # # print_hg_std_out_only(cleanup(minimise))
    # EN = find_path(Hcopy, H, RF, ["v1", "v4"], ["v8"], [], "-", 0)
    # i = 1
    # for hg in EN:
    #     print("New path found: {0}".format(i))
    #     print_hg_std_out_only(hg)
    #     i += 1

    # H = test_hg_02()
    # findall = find_all(H, ["A"])
    # print(findall)
    # minimise = minimise(H, RF, ["A"], ["H"])
    # print_hg_std_out_only(cleanup(minimise))
    # EN = find_path(H, RF, ["A"], ["H"], [])
    # i = 1
    # for hg in EN:
    #     print("New path found: {0}".format(i))
    #     print_hg_std_out_only(hg)
    #     i += 1

    # H = test_process()
    # H = test_simple()
    # H = test_hg_02()
    H = test_inf()
    Hcopy = H.copy()
    rmust = DirectedHypergraph()
    rnot = DirectedHypergraph()
    # findall = find_all(H, ["start"])
    # print(findall)
    # for i in range(len(findall)):
    #     print("edge {0} {1} ==> {2}".format(findall[i], H.get_hyperedge_tail(findall[i]),
    #                                         H.get_hyperedge_head(findall[i])))
    # minimise = minimise(H, RF, ["start"], ["end"])
    # F = minimise.get_hyperedge_id_set()
    # print(F)
    # print_hg_std_out_only(cleanup(minimise))
    EN = my_var([])
    # find_path2(Hcopy, H, rnot, rmust, ["start"], ["end"], my_var.en, "+", 0, [])
    find_path_final(Hcopy, rnot, rmust, ["start"], ["end"], my_var.en, [], "+")
    i = 1
    for hg in my_var.en:
        print("New path found: {0}".format(i))
        print_hg_std_out_only(cleanup(hg))
        i += 1
    print("Number of paths found: {0}".format(len(my_var.en)))

    # H = test_hg_02()
    # EN = find_path(H, RF, ["A"], ["H"], [])
    # i = 1
    # for hg in EN:
    #     print("New path found: {0}".format(i))
    #     print_hg_std_out_only(cleanup(hg))
    #     i += 1

    # """ TEST WITH HYPERGRAPH FROM PROCESS MODEL """
    # import xml.etree.ElementTree as ET
    # from opsupport_bpm.models.pnml_to_hypergraph import convert_pnet_to_hypergraph
    # from opsupport_bpm.util.print_hypergraph import write_hg_to_file
    #
    # file_name = 'C://opsupport_bpm_files/pnml_input/inductive/PurchasingExample.pnml'
    # # file_name = 'C://opsupport_bpm_files/output_single/bpi_challenge2012_highlight.pnml'
    # tree = ET.parse(file_name)
    # pnet = tree.getroot()
    #
    # print(pnet.tag)
    #
    # transitions = pnet.findall("./net/page/transition")
    # for transition in transitions:
    #     name = transition.find("./name/text").text
    #     logger.debug("Found new Transition: " + str(transition.attrib['id']) + " NAME: " + name)
    #
    #
    # HG = convert_pnet_to_hypergraph(pnet)
    # HGcopy = HG.copy()
    # start, end = [], []
    # for node in HG.get_node_set():
    #     if HG.get_node_attribute(node, 'source') == True:
    #         start.append(node)
    #     elif HG.get_node_attribute(node, 'sink') == True:
    #         end.append(node)
    #
    # # write_hg_to_file(HG, "opt.hgr")
    # EN1 = find_path(HGcopy, HG, RF, start, end, [])
    # i = 1
    # for hg in EN1:
    #     print("New path found: {0}".format(i))
    #     print_hg_std_out_only(cleanup(hg))
    #     i += 1
    # print("Number of paths found: {0}".format(len(EN)))
    # print("Start: {0}".format(start))
    # print("End: {0}".format(end))






