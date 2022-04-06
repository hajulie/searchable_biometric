#bloom4, each tree is a lsh 

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
from b4_objs import node, Iris, to_iris
from b4_subtree import subtree

# storage_name = "heap.bin"

class main_tree(object): 

    def __init__(self, branching_factor, error_rate, n=1024, r=307, c=0.5*(1024/307), s=12, l=1000): 
        self.branching_factor = branching_factor
        self.error_rate = error_rate
        self.max_elem = None

        self.depth = None
        self.root = branching_factor - 1

        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s #samples s bits l times 
        self.l = l
        self.lsh = None
        self.hash = [ [] for i in range(l) ] #lsh output 

        self.eyes = []
        self.subtrees = [None for i in range(l)] #keeps track of subtrees 
        self.hash_to_iris = {}

        self.total_nodes = 0 

    #compute eLSH and returns the list of length l
    def compute_eLSH_one(self, element): 
        output = self.eLSH.hash(element.vector) #length of l 

        for index, h in enumerate(output):
            self.hash[index] += [h] 
            if str(h) in self.hash_to_iris:
                self.hash_to_iris[str(h)] += [element]
            else: 
                self.hash_to_iris[str(h)] = [element]
        return output

    def compute_eLSH(self, elements): #computes the mapping from hash to iris 
        for i in elements: 
            self.compute_eLSH_one(i)

    #creates a new node: bloom filter with elements from actual_elements
    def new_node(self, num_expected_elements, actual_elements=None): 
        bf = BloomFilter(max_elements=(self.l*num_expected_elements), error_rate=self.error_rate)
        n = node(bf)
        return n

    #TREE SPECIFIC FUNCS 
    def build_index(self, elements):
        num_elements = len(elements)
        level = 0 #levels increase going down 

        self.eyes = elements

        self.eLSH = eLSH_import.eLSH(LSH, self.n, self.r, self.c, self.s, self.l)
        self.lsh = self.eLSH.hashes
        # print("self.eyes", self.eyes)
        self.compute_eLSH(self.eyes)

        for h in range(self.l): 
            st = subtree(self.branching_factor, self.error_rate, self.lsh[h])
            st.build_tree( self.eyes )
            self.subtrees[h] = st 
            self.total_nodes += st.num_nodes

    def search(self, item): 
        if type(item) == Iris: 
            item = item.vector

        nodes_visited = [] 
        leaf_nodes = [] 
        returned_iris = [] 
        returned_hashes = []
        access_depth = [] #nodes accessed per depth 
        
        for sub_tree in self.subtrees: 
            st_nodes, st_leaf, st_access, st_hashes = sub_tree.search(item)

            nodes_visited += [st_nodes]
            leaf_nodes += [st_leaf]
            access_depth += access_depth
            
            for i in st_hashes:
                returned_hashes.append(i)

        for h in returned_hashes:
            returned_iris.append(self.hash_to_iris[str(h)])

        return nodes_visited, leaf_nodes, returned_iris, access_depth

"""
str_data : the data in form of list of strings 
"""
def build_db(_branching_factor, _false_pos, vector_data, n=1024, r=307, c=0.5*(1024/307), s=12, l=1000):
    # converts irises in vector form to iris object 
    data = to_iris(vector_data)

    t = main_tree(_branching_factor, _false_pos, n=n, r=r, c=c, s=s, l=l)
    t.build_index(data)
    
    return t, data

