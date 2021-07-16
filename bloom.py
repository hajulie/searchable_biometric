from bloom_filter import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as extended_lsh
from LSH import LSH
import pickle

class bftree(object):
    def __init__(self, branching_f, error_rate, max_elements, n=1024, r=307, c=0.5 * 1024/307, s=12, l=1000):
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.max_elem = max_elements
        self.tree = None
        self.root = branching_f-1
        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s
        self.l = l 

    #creates a new bloom filter with elements from actual_elements
    def new_filter(self, num_expected_elements, actual_elements=None): 
        temp = BloomFilter(max_elements=self.max_elem, error_rate=self.error_rate)
        return temp

    def add_with_eLSH(self, filter, eLSH, elements): #add to bloom filter with applying eLSH 
        for i in elements: #convert i to string first? 
            # print(i)
            if type(i) == str: 
                temp = ''.join(format(ord(k), '08b') for k in i)
                i = [int(k) for k in temp]
                i = i + ([0 for i in range(self.n - len(i))]) #padding
            current_hash = eLSH.hash(i)
            for j in current_hash: 
                # print(j)
                p = pickle.dumps(j)
                filter.add(p) #might have to convert this to string first 

        return filter        

    #build the tree 
    def build_index(self, elements): 
        self.tree = Tree() 
        num_elements = len(elements)
        level = 0 #levels increase going down 

        tree_depth = math.ceil(math.log(num_elements, self.branching_factor))
        self.eLSH = [None for i in range(tree_depth + 1)]

        #elsh object for root 
        current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, num_elements)
        self.eLSH[level] = current_elsh
        bfilter_root = self.new_filter(num_elements)
        self.add_with_eLSH(bfilter_root, current_elsh, elements)
        self.tree.create_node("root", self.root, data=bfilter_root)

        
        # print("tree depth", tree_depth)
        current_node = self.root
        parent_node = self.root-1 #-1 is just for it to work overall
        while level != tree_depth: 
            level += 1
            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(tree_depth-level)
            current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, nodes_in_level)
            self.eLSH[level] = current_elsh
            for n in range(nodes_in_level): 
                current_node += 1
                if current_node % self.branching_factor == 0: 
                    parent_node += 1
                elements_in_filter = elements[(n*items_in_filter):(n*items_in_filter)+items_in_filter]

                if elements_in_filter == []:
                    self.tree.create_node(str(current_node), current_node, data=None, parent=parent_node)
                else: 
                    bf = self.new_filter(items_in_filter)
                    self.add_with_eLSH(bf, current_elsh, elements_in_filter)
                    self.tree.create_node(str(current_node), current_node, data=bf, parent=parent_node)

        return self.tree

    def search(self, list_item): #list_item : if any item in the list_item is in bloom filter visit all children \\ kinda funky, but list_item must be list 
        depth = self.tree.depth()
        stack = [] 
        nodes_visited = [] 
        leaf_nodes = [] 
        access_depth = [[] for i in range(depth+1)] #nodes accessed per depth s
        root_bf = self.tree[self.root].data

        for i in range(len(list_item)):
            thing = list_item[i]
            if type(thing) == str: 
                temp = ''.join(format(ord(k), '08b') for k in thing)
                thing = [int(k) for k in temp]
                thing = thing + ([0 for i in range(self.n - len(list_item))]) #padding
                list_item[i] = thing
            

        access_depth[0].append(self.root)
        current_elsh = self.eLSH[0]
        for item in list_item: 
            # print(item)
            current_hash = current_elsh.hash(item)
            # print(current_hash)
            for j in current_hash:
                p = pickle.dumps(j)
                if p in root_bf: 
                    stack.append(self.root)
                    break

        while stack != []: 
            # print("stack", stack)
            current_node = stack.pop()
            nodes_visited.append(current_node)
            children = self.tree.children(current_node) 
            if children != []: 
                for c in children: 
                    child = c.identifier
                    child_depth = self.tree.depth(child)
                    current_elsh = self.eLSH[child_depth]
                    access_depth[child_depth].append(child)
                    if self.tree[child].data != None: 
                        for i in list_item:
                            current_hash = current_elsh.hash(i)
                            for j in current_hash:
                                p = pickle.dumps(j)
                                if p in self.tree[child].data: 
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

#small test 
from other import try_data
import random

t = bftree(2, 0.01, 8)
t.build_index(try_data)
t.tree.show()
attempt = try_data[0]
for i in range(100): 
    index = random.randrange(0,1024) 
    attempt[index] = ~attempt[index]
s = t.search([attempt])
print(s)