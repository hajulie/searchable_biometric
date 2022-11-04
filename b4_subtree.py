# bloom4, each tree is a lsh

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

from b4_objs import node_data, Iris, to_iris

storage_name = "heap.bin"


class subtree(object):
    def __init__(self, identifier, branching_f, error_rate, lsh, vector_length):
        self.identifier = identifier
        self.lsh = lsh
        self.l = len(lsh)
        self.vector_length = vector_length
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.num_nodes = 0
        self.max_elem = None

        self.tree = None
        self.depth = None
        self.root = branching_f - 1

        self.levels = {}

    @staticmethod
    def create_subtree(id, branching_factor, error_rate, lsh, elements, vector_length):
        st = subtree(id, branching_factor, error_rate, lsh, vector_length)
        st.build_tree(elements)
        return st

    # testing funcions
    def show_tree(self):
        return self.tree.show()

    # calculate the number of max elements based on the size of the given list
    def calculate_max_elem(self, num_elements):
        # leaf nodes are hash output
        self.max_elem = 2 ** (math.ceil(math.log2(num_elements)))

    # calculate depth of the tree
    def calculate_depth(self):
        self.depth = math.ceil(math.log(self.max_elem, self.branching_factor))

    # helper function to compute LSH
    def calculate_LSH(self, item):
        res = []
        for i, j in enumerate(self.lsh):
            res.append(j.hash(item))
        return res

    """functions for nodes"""

    def get_node(self, identifier):
        return self.tree.get_node(identifier)

    def get_node_data(self, node):
        # might need to change this later, specifying bloom_filter bc current node object has plaintext and bloom filer
        return self.tree.get_node(node).data

    def get_node_items(self, node):
        return self.get_node(node).data.items

    def add_child(self, parent_node, child):
        node_type = self.tree.get_node(parent_node).data

        if node_type is not None:
            node_type.add_child(child)

    # returns children of current node
    def get_children(self, node):
        return self.tree.children(node)

    # checks if item is in the bloomfilter of the node
    def check_bf(self, node, element):
        return self.tree.get_node(node).in_bloomfilter(element)

    # return BLOOM FILTER of root
    def return_root(self):
        return self.get_node(self.root).data.bloom_filter

    def return_root_data(self):
        return self.get_node(self.root).data

    # checks bloom filter if item exists in root
    def check_root(self, element):
        return self.get_node(self.root).data.in_bloomfilter(element)

    # get depth of tree or node
    def get_depth(self, node=None):
        if node == None:
            return self.depth
        else:
            return self.tree.depth(node)

    def check_leaf(self, node):
        return self.get_node(node).is_leaf()

    """END"""

    # creates a new node: bloom filter with elements from actual_elements
    def new_node(self, current_node, parent_node, num_expected_elements=0, elements=None, leaf=False):
        self.num_nodes += 1

        if current_node == "root":
            # corner case: current_node == "root", parent_node == self.root,
            bf = BloomFilter(max_elements=num_expected_elements * (self.l), error_rate=self.error_rate)
            _node_ = node_data(bloom_filter=bf, children=[], left_max_lsh=None)
            _node_.add_multiple(elements)
            self.tree.create_node(current_node, self.root, data=_node_)
        else:
            if leaf:
                if elements is not None:
                    _node_ = elements
                else:
                    _node_ = [(self.vector_length-1, 2)]*self.l
            else:
                bf = BloomFilter(max_elements=(self.l * num_expected_elements), error_rate=self.error_rate)
                _node_ = node_data(bloom_filter=bf, children=[],left_max_lsh=None)
                _node_.add_multiple(elements)
            self.add_child(parent_node, current_node)
            self.tree.create_node(str(current_node), current_node, data=_node_, parent=parent_node)


    def build_tree(self, og_elements):
        self.tree = Tree()
        num_elements = len(og_elements)
        level = 0

        self.calculate_max_elem(num_elements)  # max number of elements WITH calculation of eLSH outputs
        self.calculate_depth()
        elements = [self.calculate_LSH(i.vector) for i in og_elements]

        # initialize root node
        self.new_node("root", self.root, num_elements, elements=elements)
        #To enable comparison based sort in the ORAM implementation
        elements.sort(key=str)
        current_node = self.root
        parent_node = self.root - 1  # -1 is just for it to work overall

        while level != self.depth:
            level += 1
            nodes_in_level = self.branching_factor ** level
            items_in_filter = self.branching_factor ** (self.depth - level)

            if level == self.depth:
                for n in range(nodes_in_level):
                    current_node += 1
                    if current_node % self.branching_factor == 0:
                        parent_node += 1

                    # if n < self.l:
                    if n < num_elements:
                        self.new_node(current_node, parent_node, num_expected_elements=1, elements=elements[n], leaf=True)
                    else:
                        self.new_node(current_node, parent_node, num_expected_elements=1, elements=None, leaf=True)

            else:
                for n in range(nodes_in_level):
                    current_node += 1
                    if current_node % self.branching_factor == 0:
                        parent_node += 1

                    begin = n * items_in_filter
                    end = (n * items_in_filter) + items_in_filter
                    elements_in_filter = elements[begin:end]
                    self.new_node(current_node, parent_node, num_expected_elements=items_in_filter, elements=elements_in_filter)


        while parent_node>0:
            parent_node_data = self.get_node_data(parent_node)
            (child_1, child_2) = parent_node_data.get_children()
            if child_1 >= child_2:
                raise ValueError
            parent_node_data.add_children_lsh(self.get_node_data(child_1), self.get_node_data(child_2))
            parent_node -= 1


    def search(self, item):
        depth = self.tree.depth()
        stack = []
        nodes_visited = []
        leaf_nodes = []
        returned_iris = []
        access_depth={}
        root_bf = self.tree[self.root].data

        access_depth[0] = []
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
                    try:
                        nodes_per_level = access_depth[child_depth]
                    except KeyError:
                        nodes_per_level = []
                    nodes_per_level.append(child)
                    access_depth[child_depth] = nodes_per_level

                    if self.tree[child].data != None and child_depth != depth:
                        if self.tree[child].data.in_bloomfilter(current_hash):
                            stack.append(child)
                            break
                    elif self.tree[child].data != None and child_depth == depth:
                        if LSH.compareLSH(self.tree[child].data, current_hash):
                            stack.append(child)
                            break
            else:
                leaf_nodes.append(current_node)

        hashes = []
        for l in leaf_nodes:
            hashes.append(self.tree[l].data)

        return nodes_visited, leaf_nodes, access_depth, hashes