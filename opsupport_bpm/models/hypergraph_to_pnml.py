'''
Created on Aug 2, 2016

The main idea here is, given the initial Petri net, to delete what is not in the optimal hyperpath

Quick & dirty: find all transitions that are not in the optimal path and remove them, together with all the arcs
having them as source or targets

Contains also the methods reuqired to highlight the optimal path in a hypergraph on a corresponding pnml Petri net

@author: UNIST
'''
import logging

from opsupport_bpm.models.pnml_to_hypergraph import get_transition_name
from opsupport_bpm.models.pnml_to_hypergraph import get_transitions
import xml.etree.ElementTree as ET


def show_opt_path_pnet(hg_opt, tree, file_root):
    '''
    given optimal path (hypergraph hg_opt) and a Petri net (tree), it highlights the optimal path in the Petri net
    (highlihgting the non xor/tau nodes in the Petri net 
    This functions also "re-colors" the tau-split and joins in the pnet
    :param hg_opt: optimal path
    :param tree: the tree XML element of a pnml file
    :param file_root: the root of the file (e.g., "bpichallenge_2012", "road_fine_process")
    '''
    logger = logging.getLogger(__name__)
    #get the list of nodes
    pnet = tree.getroot()
    #nodes = get_transitions_from_opt_path(hg_opt)
    nodes = hg_opt.get_node_set()
    #color
    red_color = ET.Element('fill', color = '#c30e2d')
    grey_color = ET.Element('fill', color = '#A9A9A9')
    #for each node, add fill color in pnet
    trans_pnet = get_transitions(pnet)
    
        #find node in pnet
    for t_pnet in trans_pnet:
        t_name = t_pnet.find("./name/text").text
        in_opt_path = False
        for node in nodes:
            if  t_name == node:
                in_opt_path = True
                logger.debug("Transition {0} is in the optimal path - Node: {1}".format(t_name,node))
        if in_opt_path:
            if t_name[0:3] == 'tau':
                logger.debug("Found tau transition on optimal path: making it visible...")
                t_pnet.find('./toolspecific').attrib['activity'] = t_name
            #node found, add red_color as element
            logger.debug("Colouring red - node: {0} ...".format(t_name))
            graphics = t_pnet.find('graphics')
            #graphics = t_children.Element('graphics')
            graphics.append(red_color)
        #adjust tau split and tau join
#         else:
#             if node[:2] == 'tau':
#                 logger.debug("Found tau transition outside optimal path found: making it visible and grey...")
#                 # make it visible
#                 t_pnet.find('./toolspecific').attrib['activity'] = node
#                 # change colour
#                 graphics = t_pnet.find('graphics')
#                 graphics.append(grey_color)
    output_file = "C://BPMNexamples/output/"+file_root+"_highlight.pnml"
    logger.debug("writing output on file: {0}".format(output_file))
    tree.write(output_file, encoding='utf-8')
    
def reduce_opt_path_pnet(tree, file_root):
    '''
    given a pnet with highlighted optimal path, it deletes all the non relevant detail from the pnet
    :param tree: the tree element of a pnml file
    :param file_root: the root of the file (e.g., "bpichallenge_2012", "road_fine_process")
    '''
    logger = logging.getLogger(__name__)
    logger.debug("Reducing pnet...")
    pnet = tree.getroot()
    #STEP 1: delete not highlighted transitions
    #trans_pnet = get_transitions(pnet)
    trans_pnet = pnet.findall('.net/page/transition')
    page = pnet.findall('.net/page')
    for t_pnet in trans_pnet:
        graphics = t_pnet.find('graphics')
        fills = graphics.findall('fill')
        delete = True
        for fill in fills:
            if fill.attrib['color'] == '#c30e2d':
                delete = False
        if delete:
            #remove transition
            #logger.debug("Found transitions to remove (reduce): {0}".format(get_transition_name(t_pnet)))
            #t2s = pnet.findall('.net/page/transition')
            t_name = get_transition_name(t_pnet)
            page = pnet.find('./net/page')
            #find arcs to remove
            t_id = t_pnet.get('id')
            arcs = pnet.findall('./net/page/arc')
            for arc in arcs:
                if arc.get('source') == t_id or arc.get('target') == t_id:
                    page.remove(arc)
            #remove transition
            page.remove(t_pnet)      
    #STEP 2: delete arcs sourcing from or targeting non highlighted transitions and places
    # TO BE COMPLETED
    #write the output
    tree.write("C://BPMNexamples/output/"+file_root+"_reduced.pnml", encoding='utf-8')

def get_transitions_from_opt_path(hg_opt):
    '''
    returns the list of names of transition in the hypergraph (excluding xor splits and joins)
    :param hg_opt: optimal path (must be halp hypergraph)
    '''
    nodes = hg_opt.get_node_set()
    transitions = []
    for node in nodes:
        if hg_opt.get_node_attribute(node, 'type') == 'transition':
            transitions.append(hg_opt.get_node_attribute(node, 'name'))
    return transitions

def get_pnet_from_file(file_name):
    '''
    returns a pnet xml object of the file in file_name
    :param file_name: a pnml file
    '''
    tree = ET.parse(file_name)
    pnet = tree.getroot()
    return pnet

def get_transitions_from_pnet(pnet):
    '''
    returns all the transitions in a pnet
    :param pnet: root of the pnml file
    '''
    transitions = get_transitions(pnet)
    return transitions


def convert_path_to_pnet(pnet_file_name, hg_opt):
    '''
    converts a path into a petri net (TO BE COMPLETED)
    :param pnet_file_name: the name of the pnml file where the Petri net will be written
    :param hg_opt: optimal path (must be a halp hypergraph)
    '''
    #get pnet xml object
    pnet = get_pnet_from_file(pnet_file_name)
    #get transitions from pnet
    t_set_pnet = get_transitions_from_pnet(pnet)
    #get transition list from optimal path
    t_set_opt = get_transitions_from_pnet(hg_opt)
    #REMOVE TRANSITIONS FROM PNET
    #REMOVE ARCS FROM PNET
    #CHECK PLACES OF PNET
    #REWRITE PNET


def main():
    file_name = "something"
    pnet = get_pnet_from_file(file_name)

if __name__ == '__main__':
    main