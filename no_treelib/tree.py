#bloom4, each tree is a lsh 

from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as eLSH_import
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad


class Node(object): 
    
    def __init__(self, identifier, parent, depth, bloom_filter=None):
        self.identifier = identifier
        self.parent = parent
        self.children = []
        self.depth = depth

        self.bloom_filter = bloom_filter
        self.items = [] #for testing 
        self.irises = [] 

    def get_children(self):
        return self.children
    
    def get_parent(self):
        return self.parent
    
    def get_identifier(self):
        return self.identifier

    def get_depth(self): 
        return self.depth

    def is_leaf(self): 
        return self.children == []

    def return_irises(self): #returns irises of leaves 
        if self.is_leaf():
            return self.irises

    def get_hash(self):
        if self.is_leaf():
            return self.items[0]
        else: 
            raise Exception("Node is not a leaf")

    def add_item(self, lsh_output, original=None): 
        # item should be an LSH output, while original is optional for testing 
        self.bloom_filter.add(str(lsh_output))
        if original != None: 
            self.items.append(original) 

    def add_multiple(self, lst_items): 
        if type(lst_items[0]) == list:
            for i in lst_items:
                self.add_item(i) 
        else: 
            self.add_item(lst_items)

    def add_child(self, child): 
        self.children.append(child)

    def in_bloomfilter(self, item):
        if type(item) == str: 
            return item in self.bloom_filter
        else: 
            str_item = str(item)
            return str_item in self.bloom_filter
    
    def add_bloomfilter(self):
        # for future? 
        pass

class SubTree(object): 

    def __init__(self, tree_identity, branching, error_rate, lsh): 
        self.identifier = tree_identity
        self.lsh = lsh
        self.l = len(lsh)
        self.branching_factor = branching
        self.error_rate = error_rate
        
        self.nodes = {} 
        self.num_nodes = 0 
        self.max_elem = None

        self.depth = None
        self.root = branching - 1 

    def get_node(self, node_identity):
        return self.nodes[node_identity]

    def check_node_bf(self, node_identitiy, item): 
        return self.nodes[node_identitiy].in_bloom_filter(item)

    def check_node_leaf(self, node_identity): 
        return self.nodes[node_identity].is_leaf()

    def get_node_children(self, node_identitiy):
        return self.nodes[node_identitiy].get_children()

    def get_node_depth(self, node_identity): 
        return self.nodes[node_identity].get_depth()
    
    def get_leaf_item(self, node_identity):
        return self.nodes[node_identity].get_hash()

    def add_child_to_node(self, parent, child): 
        parent_node = self.nodes[parent]
        parent_node.add_child(child)

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

    def new_node(self, current, parent, depth, num_expected_elements=0, elements=None): 
        self.num_nodes += 1
        if current == self.root:
            bf = BloomFilter(max_elements=num_expected_elements*(self.l), error_rate=self.error_rate)
            _node_ = Node(current, parent, depth, bloom_filter=bf)
            _node_.add_multiple(elements)
            self.nodes[current] = _node_ 
        elif elements != None: 
            bf = BloomFilter(max_elements=num_expected_elements*(self.l), error_rate=self.error_rate)
            _node_ = Node(current, parent, depth, bloom_filter=bf)
            _node_.add_multiple(elements)
            self.add_child_to_node(parent, current)
            self.nodes[current] = _node_ 
        else: 
            self.add_child_to_node(parent, current)
            _node_ = Node(current, parent, depth)

    def new_node(self, current, num_elements, elements=None): 
        self.num_nodes += 1 
        bf = BloomFilter(max_elements=num_elements, error_rate=self.error_rate)
        _node_ = Node(current )


    def build_tree(self, elements): # builds tree in reverse level order 
        # elements are Iris objects, not hashes. 
        num_elements = len(elements)
        self.calculate_max_elem(num_elements)

        queue = [] 

        for iris in elements: 
            hashes = self.calculate_LSH(iris.vector)
            self.new_node(current, parent, depth)



    def build_tree(self, elements):
        # elements should be the list of original irises, NOT hashes 
        num_elements = len(elements)

        self.calculate_max_elem(num_elements)
        hashes = [self.calculate_LSH(i.vector) for i in elements]
        
        # initialize root node 
        self.new_node(self.root, None, 0, num_elements, hashes)

        current_node = self.root

        level = 0 
        while level != self.depth: 
            level += 1 
            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(self.depth-level)

            if level == self.depth: # last level, leaf nodes 
                for n in range(nodes_in_level):
                    current_node += 1
                    if current_node % self.branching_factor == 0 :
                        parent_node += 1

                    if n < self.l : 
                        self.new_node(current_node, parent_node, level, 1, hashes[n])
                    else: 
                        self.new_node(current_node, parent_node, level)
            
            else: 
                for n in range(nodes_in_level):
                    current_node += 1
                    if current_node % self.branching_factor == 0: 
                        parent_node += 1

                    begin = n*items_in_filter
                    end = (n*items_in_filter) + items_in_filter
                    hashes_in_filter = hashes[begin:end]

                    if hashes_in_filter == []:
                        self.new_node(current_node, parent_node, level)
                    else: 
                        self.new_node(current_node, parent_node, level, num_expected_elements=items_in_filter, elements=hashes_in_filter)

    def search(self, item): 
        stack = []
        leaf_nodes = []
        returned_iris = []

        nodes_visit = []
        nodes_per_depth = [[] for i in range(self.depth + 1)]

        if self.check_node_bf(self.root, item): 
            stack.append(self.root)
        
        while stack != []:
            current_node = stack.pop() 
            nodes_visit.append(current_node)
            children = self.get_node_children(current_node)

            if children != []:
                for c in children: 
                    child_depth = self.get_node_depth(c)
                    nodes_per_depth[child_depth].append(c)
                    if self.check_node_bf(c, item):
                        stack.append(c)
            
            else: 
                leaf_nodes.append(current_node)
        
        hashes = [self.get_leaf_item(leaf) for leaf in leaf_nodes]

        return nodes_visit, leaf_nodes, nodes_per_depth, hashes

                




