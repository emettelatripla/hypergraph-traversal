'''
Created on Aug 2, 2016

Some experiments about converting a BPMN model into a halp hypergraph...

@author: UNIST
'''
import logging

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import print_hg_std_out_only
import xml.etree.ElementTree as ET


def convert_bpmn_to_process_hgraph(bpmn_file_name):
    '''
    Convert a bpmn model into a hypergraph
    UNTESTED AND TO BE COMPLETED: DO NOT USE
    :param bpmn_file_name: file containing the BPMN xml
    '''
    hyperg = DirectedHypergraph();
    #namespace
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #parse bpmn file
    tree = ET.parse(bpmn_file_name)
    bpmndiagram = tree.getroot()
    #parse process
    processes = bpmndiagram.findall("./bpmn:process", ns)
    for process in processes:
        #pick start event
        starts = bpmndiagram.findall("./bpmn:process/bpmn:startEvent", ns)
        for start in starts:
            hyperg.add_node(start.attrib['id'], name=start.attrib['name'], cost=0.1, qual=0.1, avail=0.1, time=0.1)
            #logger.info(get_tag(start))
            visited = []
            hyperg = inspect_task(start, hyperg, bpmndiagram, [])
    print_hg_std_out_only(hyperg)
    return hyperg


def inspect_task(node, hyperg, bpmndiagram, visited):
    '''
    
    :param node:
    :param hyperg:
    :param bpmndiagram:
    :param visited:
    '''
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #if end event: stop
    if get_tag(node) == 'endEvent':
        visited.append(node)
        logger.info("Visiting END EVENT")
    #if AND split/join do not process and move to target node
    elif get_tag(node) == 'parallelGateway':
        logger.info("Visiting PARALLEL gateway: "+get_id(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                inspect_task(node, hyperg, bpmndiagram, visited)
    elif get_tag(node) == 'startEvent' or get_tag(node) == 'task' or get_tag(node) == "exclusiveGateway":
        logger.info("Visiting Element: "+get_id(node)+" NAME: "+get_name(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        #find all outgoings to task or xor join/split
        task_outgoings = []
        for outgoing in outgoings:
            if get_tag(get_target_ref(outgoing, bpmndiagram)) == 'task' or get_tag(get_target_ref(outgoing, bpmndiagram)) == 'exclusiveGateway':
                task_outgoings.append(get_target_ref(outgoing, bpmndiagram))
        #add hyperedge in hypergraph
        #build tail
        tail_hyper = []
        tail_hyper.append(get_id(node))
        #add node explicitly
        add_node_in_hypergraph(node, hyperg)
        #build head
        head_hyper = []
        for outgoing in outgoings:
            head_hyper.append(get_id(get_target_ref(outgoing, bpmndiagram)))
            add_node_in_hypergraph(get_target_ref(outgoing, bpmndiagram), hyperg)
        #add hyperdge
        add_edge_in_hypergraph(tail_hyper, head_hyper, hyperg)
        #still traversing the process, not sure if needed!!!!
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                inspect_task(node, hyperg, bpmndiagram, visited)
    return hyperg

def add_node_in_hypergraph(node, hyperg):
    '''
    
    :param node:
    :param hyperg:
    '''
    hyperg.add_node(get_id(node), name = get_name(node), sink = False, source = False, cost = 0.1, qual = 0.6, avail = 0.9, time = 0.2)

def add_edge_in_hypergraph(tail, head, hyperg):
    '''
    
    :param tail:
    :param head:
    :param hyperg:
    '''
    for node in tail:
        if not hyperg.has_node(node):
            logging.warning("This node is not in graph: "+str(node))
    for node in head:
        if not hyperg.has_node(node):
            logging.warning("This node is not in graph: "+str(node))
    hyperg.add_hyperedge(tail, head, phero=0.4)       

#a simple traversal algorithm
def bpmn_diagram_traversal(node, hyperg, bpmndiagram, visited):
    '''
    
    :param node:
    :param hyperg:
    :param bpmndiagram:
    :param visited:
    '''
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    #if end event: stop
    if get_tag(node) == 'endEvent':
        visited.append(node)
        logger.info("END EVENT found!!!")
    #if AND split/join do not process and move to target node
    elif get_tag(node) == 'parallelGateway':
        logger.info("Visiting PARALLEL gateway: "+get_id(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                bpmn_diagram_traversal(node, hyperg, bpmndiagram, visited)
    elif get_tag(node) == 'startEvent' or get_tag(node) == 'task' or get_tag(node) == "exclusiveGateway":
        logger.info("Visiting Element: "+get_id(node)+" NAME: "+get_name(node))
        outgoings = get_outgoing_flows(node, bpmndiagram)
        for outgoing in outgoings:
            node = get_target_ref(outgoing, bpmndiagram)
            if visited.count(node) == 0:
                visited.append(node)
                bpmn_diagram_traversal(node, hyperg, bpmndiagram, visited)
    return hyperg

            


    
#BPMN: given SequenceFlow >> id of the target element
def get_target_ref(flow, bpmndiagram):
    '''
    
    :param flow:
    :param bpmndiagram:
    '''
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    element_id = flow.attrib['targetRef']
    element = bpmndiagram.find("./bpmn:process/*[@id='"+element_id+"']", ns)
    return element

#BPMN: given SequenceFlow >> id of the source element
def get_source_ref(flow, bpmnDiagram):
    '''
    
    :param flow:
    :param bpmnDiagram:
    '''
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    element_id = flow.attrib['sourceRef']
    element = bpmndiagram.find("./bpmn:process/*[@id='"+element_id+"']", ns)
    return element
    
#BPMN: given Element >> get list of of id of outgoing sequence flows
def get_outgoing_flows(element, bpmndiagram):
    '''
    
    :param element:
    :param bpmndiagram:
    '''
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@sourceRef='"+element.attrib['id']+"']", ns)
    return out_flows

#BPMN: given Element >> get list of of id of incoming sequence flows
def get_incoming_flows(element, bpmndiagram):
    '''
    
    :param element:
    :param bpmndiagram:
    '''
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    out_flows = bpmndiagram.findall("./bpmn:process/bpmn:sequenceFlow[@targetRef='"+element.attrib['id']+"']", ns)
    return out_flows
    

def get_id(element):
    '''
    
    :param element:
    '''
    if 'id' in element.keys():
        return element.attrib['id']
    else:
        return element.text

def get_name(element):
    '''
    
    :param element:
    '''
    return element.attrib['name']

def get_text(element):
    return element.text

def get_tag(element):
    prefix = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    return element.tag[len(prefix):]


if __name__ == "__main__":
    #setup the logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # # Open XML document using minidom parser
    file_name = "C://BPMNexamples/simplexor.bpmn"
    tree = ET.parse(file_name)
    bpmndiagram = tree.getroot()
    #get info from startEvent
    ns = {'bpmn':'http://www.omg.org/spec/BPMN/20100524/MODEL' }
    # starts = bpmndiagram.findall("./bpmn:process/bpmn:task", ns)
    # for start in starts:
    #     logger.info("===== Found START event...")
    #     print("ID: "+str(get_id(start)))
    #     print("Name: "+str(get_name(start)))
    #     outflows = get_outgoing_flows(start, bpmndiagram)
    #     for flow in outflows:
    #         print("Outgoing flow: "+get_id(flow))
    #         logger.info(">> Target ref: "+str(get_target_ref(flow, bpmndiagram)))
    #     print("===========================")
    #      
    # xorgateways = bpmndiagram.findall("./bpmn:process/bpmn:exclusiveGateway", ns)
    # andgateways = bpmndiagram.findall("./bpmn:process/bpmn:parallelGateway", ns)
    #  
    # gateways = list(set(xorgateways).union(andgateways))
    # for gateway in gateways:
    #     print("+++++ Found new gateway....")
    #     print("ID: "+str(get_id(gateway)))
    #     outgoings = get_outgoing_flows(gateway, bpmndiagram)
    #     incomings = get_incoming_flows(gateway, bpmndiagram)
    #     for incoming in incomings:
    #         print("Incoming flow: "+get_id(incoming))
    #     for outgoing in outgoings:
    #         print("Outgoing flow: "+get_id(outgoing))
    #     print("+++++++++++++++++++++++++++")
    
    convert_bpmn_to_process_hgraph(file_name)
