from bloom_filter import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as extended_lsh
from LSH import LSH
import pickle

import pyoram
from pyoram.util.misc import MemorySize
from pyoram.oblivious_storage.tree.path_oram import PathORAM

from six.moves import xrange

storage_name = "oram.bin"


class bftree(object):
    def __init__(self, branching_f, error_rate, max_elements, n=1024, r=307, c= 0.5 * (1024/307), s=12, l=1000):
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.max_elem = max_elements
        self.tree = None
        self.root = branching_f-1
        self.depth = None
        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s
        self.l = l 

    #creates a new bloom filter with elements from actual_elements
    def new_filter(self, num_expected_elements, actual_elements=None): 
        temp = BloomFilter(max_elements=(self.l*num_expected_elements), error_rate=self.error_rate)
        return temp

    def add_with_eLSH(self, filter, elsh, elements): #add to bloom filter with applying eLSH 
        for i in elements:
            current_hash = elsh.hash(i)
            count_hash = 0 
            for j in current_hash: 
                count_hash += 1
                p = str(j)
                filter.add(p) 

        return filter        

    #build the tree 
    def build_index(self, elements): 
        self.tree = Tree() 
        num_elements = len(elements)
        level = 0 #levels increase going down 

        tree_depth = math.ceil(math.log(num_elements, self.branching_factor))
        self.depth = tree_depth
        self.eLSH = [None for i in range(tree_depth + 1)]

        #elsh object for root 
        current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, self.l)
        self.eLSH[level] = current_elsh
        bfilter_root = self.new_filter(num_elements)
        f = self.add_with_eLSH(bfilter_root, current_elsh, elements)
        self.tree.create_node("root", self.root, data=f)
        
        current_node = self.root
        parent_node = self.root-1 #-1 is just for it to work overall
        while level != tree_depth: 
            level += 1
            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(tree_depth-level)
            current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, self.l) #new elsh for new tree depth 
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
                    f = self.add_with_eLSH(bf, current_elsh, elements_in_filter)
                    self.tree.create_node(str(current_node), current_node, data=f, parent=parent_node)

        return self.tree

    def tree_to_arr(self): 
        arr_nodes = self.tree.all_nodes()
        return arr_nodes

    def oram(self): #UNFINISHED AND DOES NOT WORK 
        if os.path.exists(storage_name): 
            os.remove(storage_name)
        
        arr_nodes = self.tree_to_arr()
        for i in range(len(arr_nodes)): 
            arr_nodes[i] = bytearray(pickle.dumps(arr_nodes[i]))
        print(arr_nodes)

        f = PathORAM.setup(storage_name, block_size=3*16, block_count=self.max_elem, storage_type='file')
        f.close()
        
        with PathORAM(storage_name, f.stash, f.position_map, key=f.key, storage_type='file') as f: 
            orig = f.read_blocks(list(xrange(self.max_elem)))
            # g.write_block(0, bytes(b'aaa'))
            f.write_block(1, bytes(arr_nodes[0]))
            # for i in xrange(self.max_elem):
                # g.write_block(1, bytes(arr_nodes[i]))
            print(f.read_block(list(xrange(self.max_elem))))

    def search(self, item): #list_item : if any item in the list_item is in bloom filter visit all children 
        depth = self.tree.depth()
        stack = [] 
        nodes_visited = [] 
        leaf_nodes = [] 
        access_depth = [[] for i in range(depth+1)] #nodes accessed per depth 
        root_bf = self.tree[self.root].data

        access_depth[0].append(self.root)
        current_elsh = self.eLSH[0]
        current_hash = current_elsh.hash(item)
        for j in current_hash:
            p = str(j)
            if p in root_bf: 
                stack.append(self.root)
                break

        while stack != []: 
            current_node = stack.pop()
            nodes_visited.append(current_node)
            children = self.tree.children(current_node) 
            
            if children != []: 
                child_depth = self.tree.depth(current_node) + 1
                current_elsh = self.eLSH[child_depth]

                current_hash = current_elsh.hash(item)

                for c in children: 
                    child = c.identifier 
                    access_depth[child_depth].append(child)                    
                    if self.tree[child].data != None: 
                        count = 0 
                        for j in current_hash: 
                            count += 1
                            p = str(j) 
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

#small test 
from other import try_data
import random

n = 2
fpr = 0.000001 
temp_l = 1000

try_nums = [16]

for n in try_nums: 
    print('\n--- size of database = %i ---' %n )
    try_data = ([[random.getrandbits(1) for i in range(1024)] for i in range(n)])

    t = bftree(2, fpr, n, l = temp_l)
    t.build_index(try_data)
    # print(t.tree.all_nodes())
    # t.oram()
    t.tree.show()
    child = random.randint(0,n-1)
    attempt = try_data[child]
    p_child = child + 16
    print("Search for leaf %i" % p_child)
    s = t.search(attempt)
    print("All nodes visited:", s[0])
    print("Matched leaf nodes:", s[1])
    print("Nodes matched at each level:", s[2])