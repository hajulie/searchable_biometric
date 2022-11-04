#bloom4, each tree is a lsh 

from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as eLSH_import
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad


class Node(object): 
    
    def __init__(self, identifier, depth, bloom_filter=None):
        self.identifier = identifier
        self.parent = None
        self.children = []
        self.depth = depth

        self.bloom_filter = bloom_filter
        self.items = [] 
        self.iris = []
        self.leaf_hash = None

    @staticmethod
    def create_node(identifier, depth): 
        return Node(identifier, depth)

    def get_children(self):
        return self.children
    
    def get_parent(self):
        return self.parent
    
    def get_identifier(self):
        return self.identifier

    def get_depth(self): 
        return self.depth

    def get_items(self):
        return self.items

    def is_leaf(self): 
        return self.children == []

    def set_leaf(self, iris_object, _hash): 
        self.iris.append(iris_object)
        self.leaf_hash = _hash

    def get_irises(self): #returns irises of leaves 
        if self.is_leaf():
            return self.irises

    def set_bloomfilter(self, bf): 
        self.bloom_filter = bf

    def get_hash(self):
        if self.is_leaf():
            return self.items[0]
        else: 
            raise Exception("Node is not a leaf")

    def add_item(self, lsh_output, original=None): 
        # item should be an LSH output, while original is optional for testing 
        self.bloom_filter.add(str(lsh_output))
        self.items.append(lsh_output)
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

    def set_parent(self, parent):
        self.parent = parent 

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

    def new_node(self, identifier, node_depth, lst_elements, iris_object=None): 
        self.num_nodes += 1 
        _node_ = Node(identifier, node_depth)
        if iris_object != None: #is leaf node 
            assert(len(lst_elements) == 1)
            _node_.set_leaf(iris_object, lst_elements[0])
        else: 
            num_elements = len(lst_elements)
            bf = BloomFilter(max_elements=num_elements, error_rate=self.error_rate)
            _node_.set_bloomfilter(bf)
            _node_.add_multiple(lst_elements)

        self.nodes[identifier] = _node_

    def set_relations(self, child1, child2, parent): 
        parent.add_child(child1)
        parent.add_child(child2)
        child1.set_parent(parent)
        child2.set_parent(parent)

    def build_tree(self, elements): # builds tree in reverse level order 
        # elements are Iris objects, not hashes. 
        num_elements = len(elements)
        self.calculate_max_elem(num_elements)

        queue = [] 
        queue2 = []
        node_identifier = 0
        node_depth = self.depth

        for iris in elements: 
            hashes = self.calculate_LSH(iris.vector)
            print('HASHES', hashes) #TESTPRINT
            for h in hashes: 
                node_identifier += 1 
                _node = self.new_node(node_identifier, node_depth, [h], iris_object=iris)
                queue.append(_node)

        node_depth -= 1 
        while queue != []: 
            node_identifier += 1 
            child1, child2 = queue.pop(0), queue.pop(0)
            lst_elements = child1.get_items() + child2.get_items()
            new_node = self.new_node(node_identifier, node_depth, lst_elements)
            self.set_relations(child1, child2, new_node)
            queue2.append(new_node)

            if queue == []: 
                if len(queue2) == 1: # reached root node 
                    queue = [] 
                else: 
                    queue = queue2
                    queue2 = []
                node_depth -= 1 

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

                




