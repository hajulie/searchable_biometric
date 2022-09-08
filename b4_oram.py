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
        self.block_sizes = []
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

    def padding(self, item, depth):
        if len(item) == self.block_sizes[depth]:
            with_padding = item
        else: 
            with_padding = pad(item, self.block_sizes[depth])
        return with_padding

    # # @profile
    # def create_map(self):
    #     # init map
    #     # self.node_map[tree][node]
    #     self.node_map = [ {} for i in range(self.maintree.l)]
    #     self.leaf_nodes = [{} for i in range(self.maintree.l)]
    #
    #     for (index_, subtree) in enumerate(self.maintree.subtrees):
    #         subtree_map = self.node_map[index_]
    #         for node in range(subtree.root, subtree.num_nodes):
    #             if node == subtree.root:
    #                 self.root.append(node)
    #                 # if root block size hasn't been added yet (kinda useless but easier if we decide to include root in ORAM at some point)
    #                 if len(self.block_sizes) == 0:
    #                     self.block_sizes.append(0)
    #             else:
    #                 subtree_map[node] = []
    #                 current_node_data = subtree.get_node_data(node)
    #                 temp = pickle.dumps(current_node_data)
    #
    #                 # if block size for depth hasn't been added yet
    #                 if len(self.block_sizes) == subtree.get_depth(node):
    #                     self.block_sizes.append(len(temp))
    #                 elif self.block_sizes[subtree.get_depth(node)] != len(temp):
    #                     print("SIZES NOT EQUAL: " + str(self.block_sizes[subtree.get_depth(node)]) + " - " + str(len(temp)))
    #
    #
    #                 subtree_map[node] = temp
    #
    #     print(self.block_sizes)
    #
    #                 # temp_blocks = []
    #                 # num_blocks = len(temp) // self.block_sizes
    #                 #
    #                 # for k in range(num_blocks):
    #                 #     block, temp = temp[:self.block_sizes], temp[self.block_sizes:]
    #                 #     temp_blocks.append(block)
    #                 #
    #                 # padded = self.padding(temp)
    #                 # temp_blocks.append(padded)
    #                 #
    #                 # #TEST WITH PRINT STATEMENT
    #                 # for j in range(len(temp_blocks)):
    #                 #     subtree_map[node] += ([temp_blocks[j]]) #? not sure if this will translate into oram

    # # @profile
    # def depth_oram(self): # oram per level
    #
    #     depth = self.maintree.subtrees[0].get_depth()
    #
    #     self.oram = [None for i in range(depth+1)]
    #     # self.oram_map = [{} for i in range(depth+1)]
    #     self.oram_map = [{} for i in range(len(self.maintree.subtrees))]
    #     add_to = [0 for i in range(depth+1)]
    #
    #     for (ind, subtree) in enumerate(self.maintree.subtrees):
    #         node_block_list = self.node_map[ind]
    #         for node in node_block_list:
    #
    #             node_depth = subtree.get_depth(node)
    #
    #             #check if ORAM exists for this depth
    #             #NOTE: the *256 for block_count was a guess, might need to do some thinking to figure out a real number for that
    #             if self.oram[node_depth] == None:
    #                 current_file_name = self.storage_name + str(node_depth)
    #                 if os.path.exists(current_file_name):
    #                     os.remove(current_file_name)
    #                 # current = PathORAM.setup(self.storage_name + str(node_depth), block_size=self.block_sizes, block_count=self.maintree.total_nodes*256, storage_type='file')
    #                 block_count = len(self.maintree.subtrees) * 2**(node_depth-1)
    #                 block_size = self.block_sizes[node_depth]
    #                 print(block_size)
    #                 print(len(node_block_list[node]))
    #                 current = PathORAM.setup(self.storage_name + str(node_depth), block_size=block_size, block_count=block_count, storage_type='file')
    #                 self.oram[node_depth] = (current)
    #                 current.close()
    #                 f = PathORAM(self.storage_name + str(node_depth), current.stash, current.position_map, key=current.key, storage_type='file')
    #             else:
    #                 current = self.oram[node_depth]
    #                 f = PathORAM(self.storage_name + str(node_depth), current.stash, current.position_map, key=current.key, storage_type='file')
    #
    #             f.write_block(add_to[node_depth], node_block_list[node])
    #             if node in self.oram_map[ind]:
    #                 self.oram_map[ind][node].append(add_to[node_depth])
    #             else:
    #                 self.oram_map[ind][node] = [add_to[node_depth]]
    #             add_to[node_depth] += 1
    #
    #             # for block in node_block_list[node]:
    #             #     f.write_block(add_to[node_depth], block)
    #             #     if node in self.oram_map[ind]:
    #             #         self.oram_map[ind][node].append(add_to[node_depth])
    #             #     else:
    #             #         self.oram_map[ind][node] = [add_to[node_depth]]
    #             #     add_to[node_depth] += 1
    #             f.close()

    def retrieve_data(self, tree, depth, node):
        current_oram_map = self.oram_map[tree]
        # print(current_oram_map)
        current_oram = self.oram[depth-1]
        current_oram_file = PathORAM(self.storage_name + str(depth-1), current_oram.stash, current_oram.position_map, key=current_oram.key, storage_type='file')
        raw_data = [] 
        if node not in current_oram_map: 
            print("Value does not exist") #for testing
        else: 
            # in_map = current_oram_map[node]
            # for pos in in_map:
            #     raw_data.append(current_oram_file.read_block(pos))
            #
            # rebuilt_node = unpad(b''.join(raw_data), self.block_sizes[depth-1])
            pos = current_oram_map[node]
            raw_data = current_oram_file.read_block(pos)
            rebuilt_node = unpad(raw_data, self.block_sizes[depth - 1])
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
        # print(matching_subtrees)

        # create list of children nodes to visit
        for st in matching_subtrees:
            lst_children = self.maintree.subtrees[st].get_children(1) # root is always node 1
            for child in lst_children:
                queue.append((st, child.identifier))

        # print("Queue ")
        # print(queue)
        # print("oram map")
        # print(self.oram_map)

        while queue != []:
            current_node = queue.pop(0)
            tree, node = current_node[0], current_node[1]
            # print("current node")
            # print(current_node)
            current_item = hashes[tree]
            current_tree = self.subtrees[tree]

            original_node_data = self.retrieve_data(tree, current_level, node)
            # print(original_node_data)
            # print(current_level)
            # print(self.maintree.depth)
            # print(current_item)

            if current_level != self.maintree.depth and original_node_data.in_bloomfilter(current_item):
                lst_children = original_node_data.get_children()
                print("children")
                print(lst_children)
                # print("children = ")
                # print(lst_children)

                if lst_children != []:
                    for child in lst_children:
                        next_level_queue.append((tree, child))

            elif current_level == self.maintree.depth and LSH.compareLSH(original_node_data, current_item):
                print("leaf match")
                # print("tree = " + str(tree) + " - node = " + str(node))
                hashes.append(item)
                leaf_nodes.append(current_node)

            else:
                print("Houston, we have a problem.")
                # print("tree = " + str(tree) + " - node = " + str(node))


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
        self.oram_map = [{} for i in range(len(self.subtrees))]

        # print(len(self.subtrees))

        for st_id in range(len(self.subtrees)):
            st = self.subtrees[st_id]

            for node_id in range(st.root, st.num_nodes):
                if node_id == st.root:
                    self.root.append(node_id)
                else:
                    # serialize node data
                    current_node = st.get_node_data(node_id)
                    # print("current node ")
                    # print(current_node)
                    pickled_node = pickle.dumps(current_node)
                    depth = st.get_depth(node_id)

                    # if depth already encountered, add node data and check if size is larger
                    if len(self.block_sizes) >= depth:
                        nodes_map[depth-1].append(pickled_node)

                        if self.block_sizes[depth-1] < len(pickled_node) + 1:
                            self.block_sizes[depth-1] = len(pickled_node) + 1

                    # if depth never encountered, create it and add node data and size
                    else:
                        nodes_map.append([pickled_node])
                        self.block_sizes.append(len(pickled_node) + 1)

                    # update node to block mapping for client
                    self.oram_map[st_id][node_id] = len(nodes_map[depth - 1]) - 1

        return nodes_map

    def build_oram(self, nodes_map):
        self.oram = [None for i in range(self.maintree.subtrees[0].get_depth())]

        for (depth, serialized_nodes) in enumerate(nodes_map):
            block_count = len(self.maintree.subtrees) * 2 ** (depth + 1) # depth = 0 since array starts at 0 but real depth would be depth+1 if root level = depth 0 (since root ot in array)
            block_size = self.block_sizes[depth]

            file_name = self.storage_name + str(depth)
            if os.path.exists(file_name):
                os.remove(file_name)
            with PathORAM.setup(file_name, block_size, block_count, storage_type='file') as f:
                self.oram[depth] = f
                for (node_id, node) in enumerate(serialized_nodes):
                    # pad serialized node if needed
                    block = self.padding(node, depth)
                    f.write_block(node_id, block)
                    self.tmp_map.append(node_id)



    def apply(self, main_tree, block_size=256): 
        self.maintree = main_tree
        self.subtrees = main_tree.subtrees
        client_map = self.init_maps()
        self.build_oram(client_map)
        # self.create_map()
        # self.depth_oram()
