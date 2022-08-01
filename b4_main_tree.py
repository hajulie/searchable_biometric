from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as eLSH_import
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad

import pyoram
from pyoram.util.misc import MemorySize
from pyoram.oblivious_storage.tree.path_oram import PathORAM

import b4_objs
from b4_objs import node_data, Iris, to_iris
from b4_subtree import subtree
import b4_oram

storage_name = "heap.bin"


class main_tree(object):

    def __init__(self, branching_factor, error_rate, n=1024, r=307, c=0.5 * (1024 / 307), s=12, l=1000):
        # tree information
        self.branching_factor = branching_factor
        self.error_rate = error_rate
        self.max_elem = None

        # (calculated) tree information
        self.depth = None
        self.root = branching_factor - 1
        self.total_nodes = 0

        # eLSH information
        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s  # samples s bits l times
        self.l = l
        self.lsh = None

        # trees info
        self.eyes = []
        self.subtrees = [None for i in range(l)]  # keeps track of subtrees
        self.hash_to_iris = {}

    def put_elements_map(self, element, output):  # puts elements in hash_to_iris
        for index, h in enumerate(output):
            if str(h) in self.hash_to_iris:
                self.hash_to_iris[str(h)] += [element]
            else:
                self.hash_to_iris[str(h)] = [element]

    # compute eLSH and returns the list of length l
    def compute_eLSH_one(self, element):
        output = self.eLSH.hash(element.vector)  # length of l
        self.put_elements_map(element, output)
        return output

    # computes eLSH output of multiple elements F
    def compute_eLSH(self, elements):
        for i in elements:
            self.compute_eLSH_one(i)

    # TREE SPECIFIC FUNCS
    def build_index(self, elements, parallel=False):
        num_elements = len(elements)
        level = 0  # levels increase going down

        self.eyes = elements

        self.eLSH = eLSH_import.eLSH(LSH, self.n, self.r, self.c, self.s, self.l)
        self.lsh = self.eLSH.hashes
        # print("self.eyes", self.eyes)
        self.compute_eLSH(self.eyes)

        # print("Processes: " + str(mp.cpu_count()))
        if parallel:
            # self.subtrees = Parallel(n_jobs=2 * mp.cpu_count())(
            #     delayed(subtree.create_subtree)(self.branching_factor, self.error_rate, h, elements)
            #     for h in self.lsh)
            return

        else:
            for h in range(self.l):
                st = subtree.create_subtree(h, self.branching_factor, self.error_rate, self.lsh[h], self.eyes)
                st.show_tree()
                self.subtrees[h] = st
                self.total_nodes += st.num_nodes



    def search(self, item):
        if type(item) == Iris:
            item = item.vector

        nodes_visited = []
        leaf_nodes = []
        returned_iris = []
        returned_hashes = []
        access_depth = []  # nodes accessed per depth

        for sub_tree in self.subtrees:
            st_nodes, st_leaf, st_access, st_hashes = sub_tree.search(item)

            nodes_visited += [st_nodes]
            leaf_nodes += [st_leaf]
            access_depth += access_depth

            for i in st_hashes:
                returned_hashes.append(i)

        # print("here h ", self.hash_to_iris)
        for h in returned_hashes:
            returned_iris.append(self.hash_to_iris[str(h)])

        return nodes_visited, leaf_nodes, returned_iris, access_depth

    """functions for oram search """

    # checks root of specified subtree
    def check_subtree_root(self, subtree_num, item):
        return self.subtrees[subtree_num].check_root(item)

    # returns a node based on tree identifier specifcation
    def return_tree_node(self, subtree_num, node):
        return self.subtrees[subtree_num].get_node(node)


"""
str_data : the data in form of list of strings 
"""


def build_db(_branching_factor, _false_pos, vector_data, n=1024, r=307, c=0.5 * (1024 / 307), s=12, l=1000, parallel=False):
    # converts irises in vector form to iris object
    data = to_iris(vector_data)

    t = main_tree(_branching_factor, _false_pos, n=n, r=r, c=c, s=s, l=l)
    t.build_index(data, parallel)

    return t, data