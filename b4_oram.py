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

    def __init__(self, files_dir=""):
        self.files_dir = files_dir
        self.maintree = None 
        self.subtrees = None 
        self.block_size = 256
        self.node_map = None 
        self.storage_name = storage_name
        self.oram_map = None
        self.oram = None
        self.root = []
        self.leaf_nodes = None
        self.tmp_map = []

    def check_hash_to_iris(self, h): 
        current_map = self.maintree.hash_to_iris
        return current_map[str(h)]

    def padding(self, item):
        if len(item) == self.block_size:
            with_padding = item
        else: 
            with_padding = pad(item, self.block_size)
        return with_padding

    def create_blocks(self, serialized_node):
        blocks_list = []
        num_blocks = (len(serialized_node) // self.block_size) + 1

        for i in range(num_blocks):
            block = self.padding(serialized_node[i * self.block_size : (i + 1) * self.block_size])
            blocks_list.append(block)

        return blocks_list

    def retrieve_data(self, tree, depth, node):
        current_oram_map = self.oram_map[tree]
        current_oram = self.oram[depth-1]
        raw_data = []

        if node not in current_oram_map:
            print("Value does not exist") #for testing
        else:
            current_oram_file = PathORAM(self.files_dir + self.storage_name + str(depth - 1), current_oram.stash, current_oram.position_map, key=current_oram.key, storage_type='file')
            blocks_pos = current_oram_map[node]

            for pos in blocks_pos:
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

        # create list of children nodes to visit
        for st in matching_subtrees:
            lst_children = self.maintree.subtrees[st].get_children(1) # root is always node 1
            for child in lst_children:
                queue.append((st, child.identifier))

        while queue != []:
            current_node = queue.pop(0)
            tree, node = current_node[0], current_node[1]
            current_item = hashes[tree]

            original_node_data = self.retrieve_data(tree, current_level, node)

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

        return irises, leaf_nodes, [], []

    def init_maps(self):
        nodes_map = []

        for st_id in range(len(self.subtrees)):
            st = self.subtrees[st_id]

            for node_id in range(st.root, st.num_nodes+1):
                if node_id == st.root:
                    self.root.append(node_id)
                else:
                    # serialize node data
                    current_node = st.get_node_data(node_id)
                    # print("size node data = " + str(len(current_node)))
                    print(current_node)
             #       print("About to pickle node")
                    pickled_node = pickle.dumps(current_node)
                    #print("size pickled = " +str(len(pickled_node)))
                    # print(pickled_node)
                    depth = st.get_depth(node_id)
                 #   print("size pickled = " + str(len(pickled_node))+" at depth "+str(depth))

                    # if new depth, create corresponding array
                    if len(nodes_map) < depth:
                        nodes_map.append([])

                    blocks_list = self.create_blocks(pickled_node)

                    for block in blocks_list:
                        nodes_map[depth-1].append((st_id, node_id, [block]))

        return nodes_map

    def build_oram(self, nodes_map):
        self.oram = [None for i in range(self.maintree.subtrees[0].get_depth())]
        self.oram_map = [{} for i in range(len(self.subtrees))]

        for (depth, serialized_nodes) in enumerate(nodes_map):
         #   print("Depth "+str(depth)+", serialized nodes "+str(serialized_nodes))
            block_count = len(serialized_nodes)
          #  print("#blocks = " + str(block_count))
            block_id = 0

            file_name = self.files_dir + self.storage_name + str(depth)
            if os.path.exists(file_name):
                os.remove(file_name)

            with PathORAM.setup(file_name, self.block_size, block_count, storage_type='file') as f:
                self.oram[depth] = f

                for (st_id, node_id, blocks_list) in serialized_nodes:
                    if node_id not in self.oram_map[st_id]:
                        self.oram_map[st_id][node_id] = []

                    for block in blocks_list:
                        f.write_block(block_id, block)
                        # add node to block mapping for client
                        self.oram_map[st_id][node_id].append(block_id)
                        block_id = block_id + 1



    def apply(self, main_tree, block_size=256): 
        self.maintree = main_tree
        self.subtrees = main_tree.subtrees
        client_map = self.init_maps()
        self.build_oram(client_map)
