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
    def __init__(self, branching_f, error_rate, max_elements, n=1024, r=307, c= 0.5 * (1024/307), s=12, l=1000, block_size=256):
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.max_elem = max_elements * l
        self.tree = None
        self.root = branching_f-1
        self.depth = None 
        self.num_blocks = None

        self.lsh_map = {}

        #lsh variables 
        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s #samples s bits l times 
        self.l = l

        #oram variable
        self.oram = None
        self.storage_name = "heap.bin"
        self.block_size = block_size #padding block size 
        self.block_count = None
        self.oram_block_size = 256
        self.map = None

    #creates a new bloom filter with elements from actual_elements
    def new_filter(self, num_expected_elements, actual_elements=None): 
        temp = BloomFilter(max_elements=(self.l*num_expected_elements), error_rate=self.error_rate)
        # print("pickle:", len(pickle.dumps(temp)))
        # print("num bits:", temp.num_bits_m)
        return temp

    def compute_elsh(self, elsh, element): #computes eLSH and maps hashes to the value 
        hashes = elsh.hash(element)
        for i in hashes: 
            if i in self.lsh_map: 
                self.lsh_map[i] += [element]
            else: 
                self.lsh_map[i] = [element]
        return hashes

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
        if tree_depth == 0: #corner case 
            tree_depth = 1
        self.depth = tree_depth
        self.eLSH = [None for i in range(tree_depth + 1)]
        self.num_blocks = 2**(self.depth+1)-1

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
            # current_elsh = extended_lsh.eLSH(LSH, self.n, self.r, self.c, self.s, self.l) #new elsh for new tree depth 
            # self.eLSH[level] = current_elsh #code for iteration 1; if elsh is diff for every level 
            self.eLSH[level] = self.eLSH[0] #code for elsh same at every level 
            for n in range(nodes_in_level): 
                current_node += 1
                if current_node % self.branching_factor == 0: 
                    parent_node += 1
                elements_in_filter = elements[(n*items_in_filter):(n*items_in_filter)+items_in_filter]

                if elements_in_filter == []:
                    self.tree.create_node(str(current_node), current_node, data=None, parent=parent_node)
                elif len(elements_in_filter) == 1: #adds to the tree wo adding to the bloom filter
                    self.tree.create_node(str(current_node), current_node, data=(elements_in_filter[0]), parent=parent_node)
                else: 
                    bf = self.new_filter(items_in_filter)
                    f = self.add_with_eLSH(bf, current_elsh, elements_in_filter)
                    self.tree.create_node(str(current_node), current_node, data=f, parent=parent_node)

        return self.tree

    def tree_to_arr(self): 
        arr_nodes = self.tree.all_nodes()
        return arr_nodes

    def put_oram(self): 
        #calculate top level size 
        size_root = len(pickle.dumps(self.tree.get_node(self.root).data)) // self.oram_block_size
        self.block_count = size_root * self.max_elem

        ###HELPER FUNCTIONS#
        #padding
        def oram_padding(item): 
            #takes the last block of the existing string, and pads it 
            last_block = len(item)% self.block_size
            front, end = item[:last_block], item[-last_block:]
            if len(end) == self.block_size: 
                with_pad = end
            else:
                with_pad = pad(end, self.block_size)
            temp = front + with_pad 
            
            return temp

            # #pads the rest of the block meant for oram with 00s 
            # temp_block = b'\x00' * self.block_size
            # blocks_to_add = (self.oram_block_size - len(temp))/self.block_size
            # # assert blocks_to_add - int(blocks_to_add) == 0
            # new = temp + (temp_block * int(blocks_to_add))
            # return new
        ###

        if os.path.exists(self.storage_name):
            os.remove(self.storage_name)

        f = PathORAM.setup(self.storage_name, block_size= self.oram_block_size, block_count=self.block_count, storage_type='file')
        f.close()
        
        self.map = {val : [] for val in range(self.root, self.num_blocks)}
        f = PathORAM(self.storage_name, f.stash, f.position_map, key=f.key, storage_type='file')

        add_to = 0 
        print("self.block_count:", self.num_blocks)
        for node in range(self.root, self.num_blocks): 
            print("node:", node)
            print("self.tree.get_node(node).data:", self.tree.get_node(node))
            temp = pickle.dumps(self.tree.get_node(node).data)

            temp_blocks = []
            num_blocks = len(temp) // self.oram_block_size
            for k in range(num_blocks):
                block, temp = temp[:self.oram_block_size], temp[self.oram_block_size:]
                temp_blocks.append(block)
            
            padded = pad(temp, self.block_size)
            temp_blocks.append(padded)

            for j in range(len(temp_blocks)):
                f.write_block(add_to, temp_blocks[j])
                self.map[node].append(add_to)
                add_to += 1

        self.oram = f
        # print(self.map)

    def search_oram(self, node): 
        raw_data = []
        in_map = self.map[node]
        for pos in in_map:
            raw_data.append(self.oram.read_block(pos))

        # print("raw data:", raw_data)
        new_split = [] 
        for v in raw_data: 
            v = bytes(v)
            # if self.oram_block_size != self.block_size:
            #     for i in range(0, self.oram_block_size//self.block_size): 
            #         front, v = v[:self.block_size], v[self.block_size:]
            #         if front != b'x\00' * self.block_size:
            #             new_split += [front]

            new_split += [v]

        # print("new_split:", new_split)

        if new_split == []: 
            orig = None
        else:
            new_split[-1] = unpad(new_split[-1], self.block_size)
            orig = b''.join(new_split)
            orig = pickle.loads(orig)
        
        # print("printed orig")
        return orig
            

    def search(self, item): #list_item : if any item in the list_item is in bloom filter visit all children 
        depth = self.tree.depth()
        stack = [] 
        nodes_visited = [] 
        leaf_nodes = [] 
        access_depth = [[] for i in range(depth+1)] #nodes accessed per depth 
        # print("root:", self.root)
        # print("self.map:", self.map)
        root_bf = self.search_oram(self.root)
        # print("root bf:", root_bf)

        access_depth[0].append(self.root)
        print("ELSH:", self.eLSH) 
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
                    child_data = self.search_oram(child)          
                    print("child_data:", child_data)          
                    if child_data != None: 
                        count = 0 
                        if child_depth != self.depth-1: 
                            for j in current_hash: 
                                count += 1
                                p = str(j) 
                                if p in child_data: 
                                    stack.append(child)
                                    break
                        else: 
                            for j in current_hash:
                                count += 1 
                                if p == child_data: 
                                    stack.append(child)
                                    break
            else: 
                leaf_nodes.append(self.lsh_map[current_node])
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

if __name__ == '__main__':
    #small test 
    import random

    n = 2
    fpr = 0.000001 
    temp_l = 1000

    try_nums = [1]

    for n in try_nums: 
        print('\n--- size of database = %i ---' %n )
        try_data = ([[random.getrandbits(1) for i in range(1024)] for i in range(n)])

        t = bftree(2, fpr, n, l = temp_l)
        t.build_index(try_data)
        # print(t.tree.all_nodes())
        t.tree.show()
        for i in range(t.root, t.num_blocks): 
            print(t.tree.get_node(i))
        t.put_oram()
        print("finished putting")
        # print("test:", len(pickle.dumps(t.tree.get_node(1).data)))
        child = random.randint(0,n-1)
        attempt = try_data[child]
        p_child = child + n
        print("Search for leaf %i" % p_child)
        s = t.search(attempt)
        print("All nodes visited:", s[0])
        print("Matched leaf nodes:", s[1])
        print("Nodes matched at each level:", s[2])