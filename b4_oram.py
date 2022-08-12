from Crypto.Util.Padding import pad, unpad
import pickle
import math, os, sys
from memory_profiler import profile

import pyoram
from pyoram.oblivious_storage.tree.path_oram import PathORAM

from LSH import LSH
from b4_objs import node_data, Iris, to_iris

storage_name = "heap"
ext = ".bin"

class oblivious_ram(object): 

    def __init__(self):
        self.maintree = None 
        self.subtrees = None 
        self.block_size = None
        self.node_map = None 
        self.storage_name = storage_name
        self.oram_map = None
        self.oram = None
        self.root = []
        self.leaf_nodes = None

    def check_hash_to_iris(self, h): 
        current_map = self.maintree.hash_to_iris
        return current_map[str(h)]

    def padding(self, item):
        if len(item) == self.block_size:
            with_padding = item
        else: 
            with_padding = pad(item, self.block_size)
        return with_padding

    @profile
    def create_map(self): 
        # init map 
        # self.node_map[tree][node]
        self.node_map = [ {} for i in range(self.maintree.l)]
        self.leaf_nodes = [{} for i in range(self.maintree.l)]

        for (index_, subtree) in enumerate(self.maintree.subtrees):
            subtree_map = self.node_map[index_]
            for node in range(subtree.root, subtree.num_nodes): 
                if node == subtree.root: 
                    self.root.append(node)
                else: 
                    subtree_map[node] = []
                    current_node_data = subtree.get_node_data(node) 
                    temp = pickle.dumps(current_node_data)

                    temp_blocks = [] 
                    num_blocks = len(temp) // self.block_size                
                    
                    for k in range(num_blocks):
                        block, temp = temp[:self.block_size], temp[self.block_size:]
                        temp_blocks.append(block)

                    padded = self.padding(temp)
                    temp_blocks.append(padded)

                    #TEST WITH PRINT STATEMENT
                    for j in range(len(temp_blocks)):
                        subtree_map[node] += ([temp_blocks[j]]) #? not sure if this will translate into oram 

    @profile
    def depth_oram(self): # oram per level

        depth = self.maintree.subtrees[0].get_depth()

        self.oram = [None for i in range(depth+1)] 
        # self.oram_map = [{} for i in range(depth+1)]
        self.oram_map = [{} for i in range(len(self.maintree.subtrees))]
        add_to = [0 for i in range(depth+1)]

        for (ind, subtree) in enumerate(self.maintree.subtrees):
            node_block_list = self.node_map[ind]
            for node in node_block_list: 
                node_depth = subtree.get_depth(node)

                #check if ORAM exists for this depth 
                #NOTE: the *256 for block_count was a guess, might need to do some thinking to figure out a real number for that 
                if self.oram[node_depth] == None: 
                    current_file_name = self.storage_name + str(node_depth) 
                    if os.path.exists(current_file_name):
                        os.remove(current_file_name)
                    current = PathORAM.setup(self.storage_name + str(node_depth), block_size=self.block_size, block_count=self.maintree.total_nodes*256, storage_type='file')
                    self.oram[node_depth] = (current)
                    current.close() 
                    f = PathORAM(self.storage_name + str(node_depth), current.stash, current.position_map, key=current.key, storage_type='file')
                else: 
                    current = self.oram[node_depth]
                    f = PathORAM(self.storage_name + str(node_depth), current.stash, current.position_map, key=current.key, storage_type='file')

                for block in node_block_list[node]: 
                    f.write_block(add_to[node_depth], block)
                    if node in self.oram_map[ind]:
                        self.oram_map[ind][node].append(add_to[node_depth])
                    else: 
                        self.oram_map[ind][node] = [add_to[node_depth]]
                    add_to[node_depth] += 1 
                f.close()

    def retrieve_data(self, tree, depth, node): 
        current_oram_map = self.oram_map[tree]
        # print(current_oram_map)
        current_oram = self.oram[depth]
        current_oram_file = PathORAM(self.storage_name + str(depth), current_oram.stash, current_oram.position_map, key=current_oram.key, storage_type='file')
        raw_data = [] 
        if node not in current_oram_map: 
            print("Value does not exist") #for testing
        else: 
            in_map = current_oram_map[node]
            for pos in in_map:
                raw_data.append(current_oram_file.read_block(pos))
            
            rebuilt_node = unpad(b''.join(raw_data), self.block_size)
            orig = pickle.loads(rebuilt_node)
        current_oram_file.close()
        return orig 

    # if things in tree are node_data not actual nodes 

    def search(self, item):
        queue = []
        next_level_queue = []
        current_level = 1 #hard coded for now

        leaf_nodes = []
        hashes = []
        lookup = []


        if type(item) != Iris:
            item = to_iris([item])
        hashes = self.maintree.eLSH.hash(item[0].vector)

        # get matching root nodes
        matching_subtrees = self.maintree.search_root_nodes(item[0].vector)
        print(matching_subtrees)

        # create list of children nodes to visit
        for st in matching_subtrees:
            lst_children = self.maintree.subtrees[st].get_children(1) # root is always node 1
            for child in lst_children:
                queue.append((st, child.identifier))

        while queue != []:
            current_node = queue.pop(0)
            tree, node = current_node[0], current_node[1]
            current_item = hashes[tree]
            current_tree = self.subtrees[tree]

            original_node_data = self.retrieve_data(tree, current_level, node)
            # print(original_node_data)
            # print(current_level)
            # print(self.maintree.depth)
            # print(current_item)

            if current_level != self.maintree.depth and original_node_data.in_bloomfilter(current_item):
                lst_children = original_node_data.get_children()

                if lst_children != []:
                    for child in lst_children:
                        next_level_queue.append((tree, child))

            elif current_level == self.maintree.depth and LSH.compareLSH(original_node_data, current_item):
                hashes.append(item)
                leaf_nodes.append(current_node)


            if queue == []:
                queue = next_level_queue
                next_level_queue = []
                current_level += 1


        # retrieve irises corresponding to returned leaf nodes
        irises = []
        # for i in hashes:
        #     returned_irises = self.check_hash_to_iris(i)
        #     irises.append(returned_irises)

        return irises, leaf_nodes

    def apply(self, main_tree, block_size=256): 
        self.maintree = main_tree
        self.subtrees = main_tree.subtrees
        self.block_size = block_size
        self.create_map()
        self.depth_oram()
