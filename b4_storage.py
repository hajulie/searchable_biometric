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
        self.storage_name = storage_name
        self.oram_map = None
        self.oram = None

    def padding(self, item):
        if len(item) == self.block_size:
            with_padding = item
        else: 
            with_padding = pad(item, self.block_size)
        
        return with_padding

    def create_map(self): 
        # init map 
        self.node_map = [ {} for i in range(self.maintree.l)]

        for (index_, subtree) in enumerate(self.maintree.subtrees):
            subtree_map = self.node_map[index_]
            for node in range(subtree.root, subtree.num_nodes): 
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

                #TEST WITH PRINT STATEME    NT
                for j in range(len(temp_blocks)):
                    subtree_map[node] += ([temp_blocks[j]]) #? not sure if this will translate into oram 
                    
    def put_oram(self): # one oram 
        self.oram_map = []

        if os.path.exists(self.storage_name): 
            os.remove(self.storage_name)

        #NOTE; the *256 for block_count was a guess, might need to do some thinking to figure out a real number for that 
        f = PathORAM.setup(self.storage_name, block_size=self.block_size, block_count=self.maintree.total_nodes*256, storage_type='file')
        f.close() 

        f = PathORAM(self.storage_name, f.stash, f.position_map, key=f.key, storage_type='file')

        add_to = 0
        for (ind, subtree) in enumerate(self.maintree.subtrees): 
            subtree_oram_map = {}
            node_block_list = self.node_map[ind]
            for node in node_block_list: 
                for block in node_block_list[node]: 
                    f.write_block(add_to, block)
                    if node in subtree_oram_map: 
                        subtree_oram_map[node] += [add_to] #keeps track of the associated node and which block it was written into 
                    else: 
                        subtree_oram_map[node] = [add_to]
                    add_to += 1
            self.oram_map.append(subtree_oram_map)

        self.oram = f 

    def mul_oram(self): # multiple orams per tree 
        self.oram_map = []

        for (ind, subtree) in enumerate(self.maintree.subtrees): 
            if os.path.exists(self.storage_name + str(ind)):
                os.remove(self.storage_name + str(ind)) 

            f = PathORAM.setup(self.storage_name + str(ind), block_size=self.block_size, block_count=self.maintree.total_nodes*256, storage_type='file')
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
    
    def depth_oram(self): #oram per level
        pass

    def noroot_oram(self, org): # root node not included in oram 
        pass

    def rebuild_node(self, node): 
        raw_data = []
        in_map = self.map[node]


# apply_storage_layer : splits the nodes of the trees into blocks (serialized, then split into blocks)
# oram types: 
# 0 = entire tree into 1 oram 
# 1 = oram for each tree 
# 2 = oram based on the depth of the nodes 
# 3 = root node not included in the oram. parameter org can be set to 0, 1, 2, corresponding to each of the different types of oram above 


def apply_storage_layer(main_tree, block_size=256, oram=None):
    storage_tree = storage_layer(main_tree, block_size)
    storage_tree.create_map()
    
    #TEST WITH PRINT STATEMENT
    # print("map create : \n \t ", storage_tree.node_map)

    if oram == 0: #one oram layer
        storage_tree.put_oram()

    elif oram == 1: # multiple oram layers 
        storage_tree.mul_oram()
    
    print("ORAM MAP: \n", storage_tree.oram_map)

    return storage_tree


