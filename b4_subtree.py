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

from b4_objs import node, Iris, to_iris

storage_name = "heap.bin"

class subtree(object):
    def __init__(self, branching_f, error_rate, lsh):
        self.lsh = lsh
        self.l = len(lsh)
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.num_nodes = 0 
        self.max_elem = None
        
        self.tree = None
        self.depth = None 
        self.root = branching_f-1

    #calculate the number of max elements based on the size of the given list 
    def calculate_max_elem(self, num_elements): 
        #leaf nodes are hash output
        self.max_elem = 2**(math.ceil(math.log2(num_elements)))

    #calculate depth of the tree 
    def calculate_depth(self):
        self.depth = math.ceil(math.log(self.max_elem, self.branching_factor))

    #helper func to calculate lsh 
    def calculate_LSH(self, item): 
        res = [] 
        for i, j in enumerate(self.lsh): 
            res.append(j.hash(item))
        return res

    def get_node_data(node):
        #might need to change this later, specifying bloom_filter bc current node object has plaintext and bloom filer 
        return self.tree.get_node(node).data.bloom_filter

    #creates a new node: bloom filter with elements from actual_elements
    def new_node(self, current_node, parent_node, num_expected_elements=0, elements=None): 
        self.num_nodes += 1 
        if current_node == "root":
            #corner case: current_node == "root", parent_node == self.root, 
            bf = BloomFilter(max_elements=(self.l), error_rate=self.error_rate)
            _node_ = node(bf)
            _node_.add_multiple(elements)
            self.tree.create_node(current_node, self.root, data=_node_)
        elif elements != None: 
            bf = BloomFilter(max_elements=(self.l*num_expected_elements), error_rate=self.error_rate)
            _node_ = node(bf)
            _node_.add_multiple(elements)
            self.tree.create_node(str(current_node), current_node, data=_node_, parent=parent_node)
        else: 
            self.tree.create_node(str(current_node), current_node, data=None, parent=parent_node)
    
    def build_tree(self, og_elements): 
        self.tree = Tree() 
        num_elements = len(og_elements)
        level = 0 

        self.calculate_max_elem(num_elements) #max number of elements WITH calculation of eLSH outputs 
        self.calculate_depth()
        elements = [self.calculate_LSH(i.vector) for i in og_elements]

        #initialize root node
        self.new_node("root", self.root, num_elements, elements=elements)

        current_node = self.root
        parent_node = self.root-1 #-1 is just for it to work overall
        
        while level != self.depth: 
            level += 1 
            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(self.depth-level)
            if level == self.depth:
                for n in range(nodes_in_level):
                    current_node += 1 
                    if current_node % self.branching_factor == 0: 
                        parent_node += 1 

                    if n < self.l:
                        self.new_node(current_node, parent_node, num_expected_elements=1, elements=elements[n])
                    else:
                        self.new_node(current_node, parent_node)

            else: 
                for n in range(nodes_in_level): 
                    current_node += 1
                    if current_node % self.branching_factor == 0: 
                        parent_node += 1

                    begin = n*items_in_filter
                    end = (n*items_in_filter)+items_in_filter
                    elements_in_filter = elements[begin:end]

                    if elements_in_filter == []:
                        self.new_node(current_node, parent_node)
                    else: 
                        self.new_node(current_node, parent_node, num_expected_elements=items_in_filter, elements=elements_in_filter)

    def get_leaf_node(self, identifier): 
        return self.tree.get_node(identifier)

    def search(self, item):
        depth = self.tree.depth()
        stack = [] 
        nodes_visited = [] 
        leaf_nodes = [] 
        returned_iris = []
        access_depth = [[] for i in range(depth+1)] #nodes accessed per depth 
        root_bf = self.tree[self.root].data

        access_depth[0].append(self.root)
        current_hash = self.calculate_LSH(item)
        if root_bf.in_bloomfilter(current_hash): 
            stack.append(self.root)

        while stack != []: 
            current_node = stack.pop()
            nodes_visited.append(current_node)
            children = self.tree.children(current_node) 
            
            if children != []: 
                child_depth = self.tree.depth(current_node) + 1

                for c in children: 
                    child = c.identifier 
                    access_depth[child_depth].append(child)                    
                    if self.tree[child].data != None: 
                        if self.tree[child].data.in_bloomfilter(current_hash): 
                            stack.append(child)
                            break
            else: 
                leaf_nodes.append(current_node)

        hashes = [] 
        for l in leaf_nodes: 
            hashes.append(self.tree[l].data.items[0])


        return nodes_visited, leaf_nodes, access_depth, hashes
