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

    def __init__(self, branching_factor, error_rate, n=1024, r=307, c=0.5*(1024/307), s=12, l=1000): 
        # tree information 
        self.branching_factor = branching_factor
        self.error_rate = error_rate
        self.max_elem = None

        # (calculated) tree information
        self.depth = None
        self.root = branching_factor - 1

        # eLSH information 
        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s #samples s bits l times 
        self.l = l
        self.lsh = None
        self.hash = [ [] for i in range(l) ] #storing each lsh output <-- might change how this happens 

        self.eyes = []
        self.subtrees = [None for i in range(l)] #keeps track of subtrees 
        self.hash_to_iris = {}

        self.total_nodes = 0 

        self.maintree_oram = None

    #compute eLSH and returns the list of length l
    def compute_eLSH_one(self, element): 
        output = self.eLSH.hash(element.vector) #length of l 

        print("HERE:", output)

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
        n = node_data(bf)
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

    def apply_oram(self, block_size=256): 
        
        pass
    
    def retrieve_oram(self, list_items): # retrieve list of items from oram 
        # given a list of nodes, retrieve the items from ORAM
        pass 
    
    def oram_search(self, item): 
        # search root 
        # get response from root nodes, retrieve from oram? 
        # rebuild the node, read the node
        # if node has data, then add children to the list of nodes to retrieve from oram 
        # if node doesn't have data, then just keep reading until stack is done. 

        queue = [] 
        leaf_nodes = [] 

        hashes = self.eLSH.hash(item.vector)

        for (index, item) in enumerate(hashes): 
            current_hash = self.lsh[index]
            current_tree = self.subtrees[index].tree

            # i REALLY don't think this is right 
            for root_node in self.maintree_oram.root: 
                if root_node.data.in_bloomfilter(item): 
                    lst_children = append(current_tree.root_node)
                    for child in lst_children:
                        queue.append((index, child))

        while queue != []: 
            current = queue.pop(0)
            tree, node = current[0], current[1]
            current_item = hashes[tree]
            current_tree = self.subtrees[tree].tree
            original_node = self.maintree_oram.retrieve_data(tree, node)

            if original_node.in_bloomfilter(current_item): 
                if children != []: 
                    lst_children = append(current_tree.original_node)
                    for child in lst_children:
                        queue.append((tree, child))
                else: 
                    leaf_nodes.append(current)
        

"""
str_data : the data in form of list of strings 
"""
def build_db(_branching_factor, _false_pos, vector_data, n=1024, r=307, c=0.5*(1024/307), s=12, l=1000):
    # converts irises in vector form to iris object 
    data = to_iris(vector_data)

    t = main_tree(_branching_factor, _false_pos, n=n, r=r, c=c, s=s, l=l)
    t.build_index(data)
    
    return t, data

