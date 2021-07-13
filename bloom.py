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
        # print("tree depth", tree_depth)
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
                    self.tree.create_node(str(current_node), current_node, data=None, parent=parent_node)
                else: 
                    bf = self.new_filter(items_in_filter, elements_in_filter)
                    self.tree.create_node(str(current_node), current_node, data=bf, parent=parent_node)

        return self.tree

    def search(self, list_item): #list_item : if any item in the list_item is in bloom filter visit all children. 
        depth = self.tree.depth()
        stack = [] 
        nodes_visited = [] 
        leaf_nodes = [] 
        access_depth = [[] for i in range(depth+1)] #nodes accessed per depth s
        root_bf = self.tree[self.root].data

        access_depth[0].append(self.root)
        for item in list_item: 
            if item in root_bf: 
                stack.append(self.root)
                break

        while stack != []: 
            print("stack", stack)
            current_node = stack.pop()
            nodes_visited.append(current_node)
            children = self.tree.children(current_node) 
            if children != []: 
                for c in children: 
                    child = c.identifier
                    child_depth = self.tree.depth(child)
                    access_depth[child_depth].append(child)
                    if self.tree[child].data != None and item in self.tree[child].data: 
                        for item in list_item: 
                            if item in self.tree[child].data: 
                                stack.append(child)
                                break
            else: 
                leaf_nodes.append(current_node)
        return nodes_visited, leaf_nodes, access_depth
                    

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
# print(r)
# r = t.tree.depth(2)
# print(type(r))
# print("CHILDRE", t.tree.children(15))
# print(t.search('Abe'))
# print(sys.getsizeof(t.tree))
# print(find_size(t))

# from test_data import mock_data
# t = bftree(5, 0.01, 1000)
# t.build_index(mock_data)

t = bftree(2, 0.01, 8)
t.build_index(['John', 'Jane', 'Smith', 'Doe', 'Abe', 'John', 'John'])
t.tree.show()
s = t.search(['John'])