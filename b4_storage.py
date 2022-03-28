from Crypto.Util.Padding import pad, unpad
import pickle
import math, os, sys

import pyoram
from pyoram.util.misc import MemorySize
from pyoram.oblivious_storage.tree.path_oram import PathORAM

storage_name = "heap.bin"

class storage_layer(object): 

    def __init__(self, maintree, block_size=256):
        self.maintree = maintree
        self.block_size = block_size
        self.node_map = None 
        self.storage_name = "heap.bin"
        self.oram_map = None
        self.oram = None

    def padding(self, item):
        last_block = len(item) % self.block_size
        front, end = item[:last_block], item[-last_block:]
        if len(end) == self.block_size:
            with_padding = end
        else: 
            with_padding = pad(end, self.block_size)
        temp = front + with_padding

    def create_map(self): 
        # init map 
        self.node_map = [ {} for i in range(self.maintree.l)]

        for (index_, subtree) in enumerate(self.maintree.subtrees):
            subtree_map = self.node_map[index_]
            for node in range(subtree.root, subtree.num_nodes): 
                current_node_data = subtree.get_node_data(node) 
                temp = pickle.dumps(current_node_data)

                temp_blocks = [] 
                num_blocks = len(temp) // self.block_size                
                
                for k in range(num_blocks):
                    block, temp = temp[:self.block_size], temp[self.block_size:]
                    temp_block.append(block)

                padded = self.padding(temp)
                temp_blocks.append(padded)

                for j in range(len(temp_blocks)):
                    self.node_map[node].append(temp_blocks[j]) #? not sure if this will translate into oram 
                    
        def put_oram(self): # one oram 
            self.oram_map = {}

            if os.path.exists(self.storage_name): 
                os.remove(self.storage_name)

            f = PathORAM.setup(self.storage_name, block_size=self.block_size, block_count=self.maintree.total_nodes, storage_type='file')
            f.close() 

            f = PathORAM(self.storage_name, f.stash, f.position_map, key=f.key, storage_type='file')

            add_to = 0
            for (ind, subtree) in enumerate(self.maintree.subtrees): 
                node_block_list = self.node_map[ind]
                for node in node_block_list: 
                    for block in node_block_list[node]: 
                        f.write_block(add_to, block)
                        if node in self.oram_map: 
                            self.oram_map[node].append(add_to) #keeps track of the associated node and which block it was written into 
                        else: 
                            self.oram_map[node] = [add_to]

            self.oram = f 

        def mul_oram(self): #multiple orams 
            self.oram_map = []

            for (ind, subtree) in enumerate(self.maintree.subtrees): 
                if os.path.exists(self.storage_name + str(ind)):
                    os.remove(self.storage_name + str(ind)) 

                f = PathORAM.setup(self.storage_name + str(ind), block_size=self.block_size, block_count=self.maintree.total_nodes, storage_type='file')
                f.close()

                f = PathORAM(self.storage_name, f.stash, f.position_map, key=f.key, storage_type='file')

                add_to = 0 
                node_block_list = self.node_map[ind]

                for node in node_block_list:
                    for block in node_block_list[node]: 
                        f.write_block(add_to, block)
                        if node in self.oram_map: 
                            self.oram_map[node].append(add_to) #keeps track of the associated node and which block it was written into 
                        else: 
                            self.oram_map[node] = [add_to]
                
                self.oram_map.append(f)




def apply_storage_layer(main_tree, block_size=256, oram=None):
    tree = storage_layer(maintree, block_size)
    tree.create_map()

    if oram == 0: #one oram layer
        tree.put_oram()

    elif oram == 1: # multiple oram layers 
        tree.mul_oram 


