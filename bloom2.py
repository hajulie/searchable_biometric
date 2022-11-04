#commit 0f010b9775ac485dd789bd70590bb8a55421fbb3

from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as extended_lsh
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad

import pyoram
from pyoram.util.misc import MemorySize
from pyoram.oblivious_storage.tree.path_oram import PathORAM

storage_name = "heap.bin"

class bftree(object):
    def __init__(self, branching_f, error_rate, n=1024, r=307, c= 0.5 * (1024/307), s=12, l=1000, block_size=256):
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.max_elem = None
        self.tree = None
        self.root = branching_f-1
        self.depth = None 
        
        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s #samples s bits l times 
        self.l = l

        self.hash_to_iris = {} 

    #calculate the number of max elements based on the size of the given list 
    def calculate_max_elem(self, num_elements): 
        #leaf nodes are hash output
        self.max_elem = self.l * (2**(math.ceil(math.log2(num_elements)))) #l * (2^{ceil(log_2(elements in list))})

    #calculate depth of the tree 
    def calculate_depth(self):
        self.depth = math.ceil(math.log(self.max_elem, self.branching_factor))

    #compute eLSH and returns the list of length l
    def compute_eLSH(self, elsh_object, element): 
        output = elsh_object.hash(element) #length of l 

        for h in output:
            if str(h) in self.hash_to_iris:
                self.hash_to_iris[str(h)] += [element]
            else: 
                self.hash_to_iris[str(h)] = [element]
        return output

    #creates a new bloom filter with elements from actual_elements
    def new_filter(self, num_expected_elements, actual_elements=None): 
        temp = BloomFilter(max_elements=(self.l*num_expected_elements), error_rate=self.error_rate)
        return temp

    def add_to_filter(self, filter, elements): #elements needs to be in a list format
        for i in elements: 
            if type(i) != str: 
                i = str(i)
            filter.add(i)
        return filter
    
    def add_with_eLSH(self, filter, elsh, elements): #add to bloom filter with applying eLSH 
        for i in elements:
            current_hash = self.compute_eLSH(elsh, i) #computes the hash
            for j in current_hash: #iterates through [0, l)
                p = str(j) 
                filter.add(p) #adds hash to bloom filter 
        return filter        

    #build the tree; assumption of one iris 
    def build_index(self, elements): 
        self.tree = Tree() 
        num_elements = len(elements)
        level = 0 #levels increase going down 

        self.calculate_max_elem(num_elements) #max number of elements WITH calculation of eLSH outputs 
        self.calculate_depth()

        self.eLSH = [None for i in range(self.depth + 1)] #keeps track of eLSH per level 
        self.block_count = 2**(self.depth+1)-1 #total number of nodes in the tree 

        #elsh object for root 
        current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, self.l)
        self.eLSH[level] = current_elsh
        bfilter_root = self.new_filter(num_elements)
        f = self.add_with_eLSH(bfilter_root, current_elsh, elements)
        self.tree.create_node("root", self.root, data=f)
        
        current_node = self.root
        parent_node = self.root-1 #-1 is just for it to work overall
        while level != self.depth: 
            level += 1

            # current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, self.l) #new elsh for new tree depth 
            current_elsh = self.eLSH[0]
            self.eLSH[level] = self.eLSH[0] #<- for now 

            hashes = []
            for e in elements:
                hashes += self.compute_eLSH(current_elsh, e)

            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(self.depth-level)
            if level == self.depth:
                for n in range(nodes_in_level):
                    current_node += 1
                    if current_node % self.branching_factor == 0:
                        parent_node += 1
                    
                    if n < len(hashes): 
                        self.tree.create_node(str(current_node), current_node, data=str(hashes[n]), parent=parent_node)
                    else: 
                        self.tree.create_node(str(current_node), current_node, data=None, parent=parent_node)
            else:
                for n in range(nodes_in_level): 
                    current_node += 1
                    if current_node % self.branching_factor == 0: 
                        parent_node += 1
                    
                    begin = n*items_in_filter
                    end = (n*items_in_filter)+items_in_filter
                    
                    elements_in_filter = hashes[begin:end]

                    if elements_in_filter == []:
                        self.tree.create_node(str(current_node), current_node, data=None, parent=parent_node)
                    else: 
                        bf = self.new_filter(items_in_filter)
                        # f = self.add_with_eLSH(bf, current_elsh, elements_in_filter)
                        f = self.add_to_filter(bf, elements_in_filter)
                        self.tree.create_node(str(current_node), current_node, data=f, parent=parent_node)
            print("depth is "+str(self.depth))
            return self.tree

    def tree_to_arr(self): 
        arr_nodes = self.tree.all_nodes()
        return arr_nodes     

    def search(self, item): #list_item : if any item in the list_item is in bloom filter visit all children 
        depth = self.tree.depth()
        stack = [] 
        nodes_visited = [] 
        leaf_nodes = [] 
        returned_iris = []
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
        
        for l in leaf_nodes: 
            iris = self.hash_to_iris[self.tree.get_node(l).data]
            returned_iris.append(iris)
        return nodes_visited, leaf_nodes, access_depth, returned_iris
                    

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


if __name__ == '__main__':
    #small test 
    import random

    n = 2
    fpr = 0.001 
    temp_l = 5

    try_nums = [2]

    for n in try_nums: 
        print('\n--- size of database = %i ---' %n )
        try_data = ([[random.getrandbits(1) for i in range(1024)] for i in range(n)])

        t = bftree(2, fpr, n, l = temp_l)
        t.build_index(try_data)
        t.tree.show()
        child = random.randint(0,n-1)
        attempt = try_data[child]
        p_child = child
        print("Search for leaf %i" % p_child)
        s = t.search(attempt)
        print("All nodes visited:", s[0])
        print("Matched leaf nodes:", s[1])
        print("Nodes matched at each level:", s[2])
        
        match = 0 
        non = 0
        for i in s[3]: 
            for r in i: 
                if r == attempt: 
                    match += 1
                else: 
                    non += 1 

        print("Matches:", match)
        print("Non Matches:", non)