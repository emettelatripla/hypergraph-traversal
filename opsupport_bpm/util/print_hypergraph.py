'''
Created on Aug 2, 2016

Methods to print hypergraphs

Persistence of hypergraph (write and read to/from file) with custom attributes, such as phero for edges, cost, qual etc. for nodes

@author: UNIST
'''
from halp.directed_hypergraph import DirectedHypergraph
import logging
import ast

def write_hg_to_file(hg, file_name):
    '''
    write hypergraph on a file. 
    Nodes in the file are written like (separator: &&&): n2&&&attr1=value1&&&attr2=value2...
    Hyperedges (n1,n2)->(n3,n4) are written as (separator: &&&): e1&&&attr1=value1&&&attr2=value2...
    :param hg:
    :param file_name:
    '''
    out_file = open(file_name, 'w')
    sep = '\t'
    
    #out_file.write("nodes\n")
    # write nodes
    for node in hg.get_node_set():
        node_attrs = hg.get_node_attributes(node)
        line = 'node' + sep + str(node) + sep + str(node_attrs)
        line += '\n'
        out_file.write(line)
      
    #out_file.write("edges\n")  
    # write edges
    for edge in hg.get_hyperedge_id_set():
        edge_attrs = hg.get_hyperedge_attributes(edge)
        line = 'edge' + sep + str(edge) + sep + str(edge_attrs)
        line = line + '\n'
        out_file.write(line)
    
    out_file.close()
        
            

def read_hg_from_file(file_name):
    '''
    returns a hypergraph based on the info in a file. Assumption: file_name has been written using write_hg_on_file
    :param file_name:
    '''
    hg = DirectedHypergraph()
    
    in_file = open(file_name, 'r')
    lines = in_file.readlines()
    sep = '\t'
    for line in lines:
        #line.strip()
        values = line.split(sep)
        #for value in values:
        if values[0] == 'node':
            # I am processing a node
            node_id = values[1]
            node_attrs = ast.literal_eval(values[2])
            hg.add_node(node_id, node_attrs)
        if values[0] == 'edge':
            tail = None
            head = None
            edge = values[1]
            edge_attrs = ast.literal_eval(values[2])
            # I am processsing an edge
            for j in range(2, len(values), 1):
                values[j] = values[j].strip()
                tail = edge_attrs['tail']
                #print(tail)
                #tail_list = eval(tail)
                head = edge_attrs['head']
                # turn string representation of head into an actual list
                #head_list = ast.literal_eval(head)
            #print("ID, TAIL, HEAD: {2} - {0} - {1} - {3}".format(tail,head,values[1], edge_attrs))
            hg.add_hyperedge(tail, head, edge_attrs)
    print_hg_std_out_only(hg)
    in_file.close()    
    return hg
    

def print_hg(hg, file_name):
    """
    Writes hypergraph on file and then displays the content of the file line by line on default logger
    :param hg hypergraph
    :param file-name the path to the file
    """
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    hg.write(file_name, ',','\t')
    logger.info("========= Printing hypergraph... =================================")
    f = open(file_name, 'r')
    contents = f.readlines()
    #for i in contents:
    #    print(i)
    f.close()
    for node in hg.get_node_set():
        print_node(node, hg)
    for edge in hg.get_hyperedge_id_set():
        print_hyperedge(edge, hg)
    logger.info("========== ... Printing hypergraph complete ======================")
    
def print_hg_std_out_only(hg):
    """
    Displays (or print) hypergraph on default logger
    :param hg hypergraph
    """
    #hg.write(file_name, ',','\t')
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("========= Printing hypergraph... =================================")
    for node in hg.get_node_set():
        print_node(node, hg)
    for edge in hg.get_hyperedge_id_set():
        print_hyperedge(edge, hg)
    logger.info("========== ... Printing hypergraph complete ======================")
    
def print_node(node, hg):
    """
    Displays information about a specific node on one single line in default logger
    :param node node
    :param hg hypergraph to which the node belongs
    """
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("NODE: {0} ### Attributes: {1}".format(str(node), hg.get_node_attributes(node)))
    
def print_hyperedge(h_edge, hg):
    """
    Displays information about a specific hyperedge on one single line in default logger
    :param h_edge hyperedge
    :param hg hypergraph to which the node belongs
    """
    #logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', filename='C://BPMNexamples/aco.log',level=logging.INFO)
    logger = logging.getLogger(__name__)
    #h_edge_name = str(hg.get_hyperedge_attribute(h_edge,'name'))
    h_edge_tail = str(hg.get_hyperedge_tail(h_edge))
    h_edge_head = str(hg.get_hyperedge_head(h_edge))
    #h_edge_phero = str(hg.get_hyperedge_attribute(h_edge, 'phero'))
    # logger.info("EDGE: {0} ### Tail: {1} >>> Head: {2} ### Phero: {3}".format(str(h_edge), h_edge_tail, h_edge_head, h_edge_phero))
    logger.info("EDGE: {0} ### Tail: {1} >>> Head: {2} ".format(str(h_edge), h_edge_tail, h_edge_head))
    
    
""" main to do some testing if required"""
if __name__ == "__main__":
    pass