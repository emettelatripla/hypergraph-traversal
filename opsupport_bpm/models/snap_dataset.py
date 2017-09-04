import csv
import json
import logging
import sys
import random

from collections import Counter

from halp.directed_hypergraph import DirectedHypergraph
from opsupport_bpm.util.print_hypergraph import write_hg_to_file,\
    read_hg_from_file, print_hg_std_out_only

from opsupport_bpm.aco.aco_directed_hypergraph import aco_search_nonrec
from opsupport_bpm.models.hypergraph import reset_pheromone

from opsupport_bpm.models.bf_trace_enumerator import BF_PathEnumerator

class SnapDatasetLoader():

    def __init__(self):
        self._file_name, self.hg, self._split_char = None

    def _init_(self, file_name, split_char):
        self._file_name = file_name
        self.hg = DirectedHypergraph()
        self._split_char = split_char

    def to_hypergraph_simple(self):
        with open(self._file_name) as f:
            for line in f:
                line = line.partition('#')[0]
                line = line.rstrip()
                line_split = line.split(self._split_char)
                source, target = line_split[0], line_split[1]
                self.hg.add_hyperedge(source, target)

    def hg_stats(self):
        pass

    def to_hypergraph_complex(self):
        with open(self._file_name) as f:
            for line in f:
                line = line.partition('#')[0]
                line = line.rstrip()
                line_split = line.split(self._split_char)
                source, target = line_split[0], line_split[1]
                self.hg.add_hyperedge(source, target)


if __name__ == '__main__':

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    logger = logging.getLogger(__name__)

    class EN():
        lst = []

    class goo():
        def get_list(self):
            l = [0, 0, 0]
            for i in range(3):
                l[i] = random.random()
            return l


    def my_method(l, count):
        for j in l:
            if j > 0.5:
                EN.lst.append(j)
                print(EN.lst)
                print(j)
                for i in range(3):
                    l[i] = random.random()
                foo(count)
                print("L in loop: {0}".format(l))
                count += 1
            else:
                print(j)
                print("Returning...")
                return None

    def foo(count):
        input()
        print("Call to foo...")
        l = [0, 0, 0]
        for i in range(3):
            l[i] = random.random()
        print("L outside loop: {0}".format(l))
        EN.lst.append("XXXX")
        for j in l:
            if j > 0.5:
                EN.lst.append(j)
                print(EN.lst)
                print(j)
                for i in range(3):
                    l[i] = random.random()
                foo(count)
                print("L in loop: {0}".format(l))
                count += 1
            else:
                print(j)
                print("Returning...")
                return None
        return None

    foo(0)


