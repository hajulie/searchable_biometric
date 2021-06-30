from bloom_filter import BloomFilter
from treelib import Node, Tree
import math, os, sys

class bftree(object):
    def __init__(self, branching_f, error_rate, max_elements):
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.max_elem = max_elements
        self.tree = None
        self.root = None

    #creates a new bloom filter with elements from actual_elements
    def new_filter(self, num_expected_elements, actual_elements=None): 
        temp = BloomFilter(max_elements=self.max_elem, error_rate=self.error_rate)
        if actual_elements != None: 
            for i in actual_elements:
                temp.add(i)
        return temp

    #build the tree 
    def build_index(self, elements): 
        self.tree = Tree() 
        self.root = self.branching_factor-1
        num_elements = len(elements)

        #root of tree
        bfilter_root = self.new_filter(num_elements, elements)
        self.tree.create_node("root", self.root, data=bfilter_root)

        #rest of tree
        level = 0 #levels increase going down 
        tree_depth = math.ceil(math.log(num_elements, self.branching_factor))
        current_node = self.root
        parent_node = self.root-1 #-1 is just for it to work overall
        while level != tree_depth: 
            level += 1
            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(tree_depth-level)
            for n in range(nodes_in_level): 
                current_node += 1
                if current_node % self.branching_factor == 0: 
                    parent_node += 1
                elements_in_filter = elements[(n*items_in_filter):(n*items_in_filter)+items_in_filter]

                if elements_in_filter == []:
                    self.tree.create_node(str(current_node)+str(elements_in_filter), current_node, data=None, parent=parent_node)
                else: 
                    bf = self.new_filter(items_in_filter, elements_in_filter)
                    self.tree.create_node(str(current_node) + str(elements_in_filter), current_node, data=bf, parent=parent_node)
        return self.tree

    #search for item 
    def search(self, item):
        nodes_visited = [] 
        root_bf = self.tree[self.root].data
        depth = self.tree.depth()

        if item in root_bf: 
            current_level = 0 
            parent = self.root 
            new_parent = self.root
            nodes_visited.append(parent)
            while current_level != depth: 
                current_level += 1
                children = self.tree.children(parent)
                for i in children: 
                    current_node = i.identifier
                    if self.tree[current_node].data != None and item in self.tree[current_node].data: 
                        nodes_visited.append(current_node)
                        new_parent = current_node
                    
                parent = new_parent
        else: 
            return nodes_visited
        return nodes_visited
                    

def find_size(bftree): 
    tree = bftree.tree
    total_size = tree[bftree.root].data.num_bits_m #bits 
    depth = bftree.tree.depth()
    branching_factor = bftree.branching_factor

    for d in range(1, depth): 
        left_most = d*branching_factor
        for current_node in range(left_most, left_most+branching_factor): 
            if tree[current_node].data != None: 
                total_size += tree[current_node].data.num_bits_m

    return total_size



# t = bftree(2, 0.01, 8)
# t.build_index(['John', 'Jane', 'Smith', 'Doe', 'Abe'])
# t.tree.show()
# r = t.tree.get_node(4)
# print("CHILDRE", t.tree.children(4))
# print(t.search('Abe'))
# print(sys.getsizeof(t.tree))
# print(find_size(t))

# from test_data import mock_data
# t = bftree(5, 0.01, 1000)
# t.build_index(mock_data)
