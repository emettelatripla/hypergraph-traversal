import csv
import json
import logging
import sys

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_nonrec
from opsupport_bpm.models.hypergraph import reset_pheromone

from opsupport_bpm.models.bf_trace_enumerator import BF_PathEnumerator

class ProteinSignallingDataset():

    def __init__(self):
        self.file_name = None
        self.type = None

    def __init__(self,file_name, fieldnames):
        self.file_name = file_name
        self.field_names = fieldnames

    def dump_json_to_file(self, json_file_name):
        json_file = open(json_file_name, 'w')
        csv_file = open(self.file_name, 'r')
        reader = csv.DictReader(csv_file, self.field_names)
        for row in reader:
            json.dump(row, json_file)
            json_file.write('\n')
        json_file.close()
        csv_file.close()


    def read_dataset(self):
        """
        :return:
        """
        csv_file = open(self.file_name, 'r')
        reader = csv.DictReader(csv_file, self.field_names)
        links = {}
        for row in reader:
            links[row['source_name']] = row['target_name']
        csv_file.close()

        return links


if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    logger = logging.getLogger(__name__)


    """ STEP 0: setup file names and paths"""
    logger.warning("Setting up file names...")

    """ PURCHASING EXAMPLE """
    csvfile_name = "C://opsupport_bpm_files/protein/test2.csv"
    fieldnames = ('source_name', 'source_uniprotAC', 'source_speciedID', 'source_species', 'source_topology', 'source_pathways',
                  "target_name", "target_uniprotAC", "target_species", "target_topology", "target_pathways", "layer", "interaction_type", "directness", "effect")

    PSD = ProteinSignallingDataset(csvfile_name, fieldnames)
    links = PSD.read_dataset()
    # for i in links:
    #     logger.debug("Source: {0} - Target: {1}".format(i, links[i]))

    hg_data = {}
    for source in links:
        if source in hg_data:
            logger.debug("adding new target to existing source")
            hg_data[source] = hg_data[source].append(links[source])
        else:
            target = links[source]
            targets = []
            targets.append(target)
            hg_data[source] = targets


    for source in hg_data:
        logger.debug("Source: {0} - Targets: {1}".format(source, hg_data[source]))
