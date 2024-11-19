from Crypto.Util.Padding import pad, unpad
import pickle
import math, os, sys, time
# from memory_profiler import profile

import pyoram
from pyoram.oblivious_storage.tree.path_oram import PathORAM

from LSH import LSH
from b4_objs import node_data, Iris, to_iris

storage_name = "heap"
ext = ".bin"


class oblivious_ram(object):

    def __init__(self, files_dir="", total_accesses=5):
        self.files_dir = files_dir
        self.maintree = None
        self.subtrees = None
        self.block_size = 256
        self.node_map = None
        self.storage_name = storage_name
        self.oram_map = None
        self.oram = None
        self.oram_handles = None
        self.root = []
        self.leaf_nodes = None
        self.tmp_map = []
        self.total_accesses = total_accesses

        # for benchmarking purposes
        self.nb_oram_access = 0
        self.time_oram_access = 0
        self.time_root_search = 0

    def search_root_nodes(self, query):
        return self.maintree.search_root_nodes(query)

    def check_hash_to_iris(self, h):
        current_map = self.maintree.hash_to_iris
        LSH.sortLSH(h)
        try:
            iris = current_map[str(h)]
            return iris
        except KeyError:
            #This happens if you did a bad traversal and the iris isn't actually there
            #or if you end up at a dummy node
            #print(current_map)
            #print("Was not able to find a corresponding iris for " + str(search))
            return None

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
            block = self.padding(serialized_node[i * self.block_size: (i + 1) * self.block_size])
            blocks_list.append(block)

        return blocks_list

    def retrieve_data(self, tree, depth, node):
        current_oram_map = self.oram_map[tree]
        current_oram = self.oram[depth - 1]
        raw_data = []

        if node not in current_oram_map:
            print("Value does not exist")  # for testing
            print(current_oram_map)
        else:
            t_start = time.time()
            current_oram_file = self.oram_handles[depth-1]

            blocks_pos = current_oram_map[node]
            for pos in blocks_pos:
                raw_data.append(current_oram_file.read_block(pos))
            self.nb_oram_access += 1

            t_end = time.time()
            self.time_oram_access += t_end - t_start

            rebuilt_node = unpad(b''.join(raw_data), self.block_size)
            orig = pickle.loads(rebuilt_node)

            #
        # print("original type:" , type(orig) == list)
        return orig

        # if things in tree are node_data not actual nodes

    def search(self, item):
        queue = []
        next_level_queue = []
        current_level = 1  # hard coded for now
        accesses_made = 0
        nodes_visited = {x.identifier: [0] for x in self.maintree.subtrees}
        access_depth = {x.identifier: [0] for x in self.maintree.subtrees}

        for tree in access_depth:
            access_depth[tree] = {i: [] for i in range(self.maintree.depth + 1)}
            access_depth[tree][0] = [1]
        num_root_matches = 0
        self.oram_handles = {}

        for depth in range(self.maintree.depth):
            current_oram = self.oram[depth]
            self.oram_handles[depth]= PathORAM(self.files_dir + self.storage_name + str(depth), current_oram.stash,
                       current_oram.position_map, key=current_oram.key, storage_type='file')


        leaf_nodes = []
        hashes = []
        match_hashes = []

        if type(item) != Iris:
            item = to_iris([item])
        hashes = self.maintree.eLSH.hash(item[0].vector)

        # get matching root nodes
        t_start = time.time()
        matching_subtrees = self.maintree.search_root_nodes(item[0].vector)
        t_end = time.time()
        time_per_level = {i: [] for i in range(self.maintree.depth + 1)}
        self.time_root_search += t_end - t_start
        time_per_level[0].append( t_end - t_start)
        num_root_matches = len(matching_subtrees)

        # create list of children nodes to visit
        for st in matching_subtrees:
            queue.append((st , 1))

        rest = self.total_accesses - len(queue)
        if rest < 0:
            queue = queue[:self.total_accesses]
        else:
            queue += [(0, 2 ** current_level)] * rest
        # print(str(queue) + ", " + str(rest))
        assert (len(queue) == self.total_accesses)

        while queue != []:
            # print(queue)
            current_node = queue.pop(0)
            nodes_visited[current_node[0]].append(current_node[1])
            accesses_made += 1
            tree, node = current_node[0], current_node[1]
            # print(current_node)
            # print(type(current_node))
            current_item = hashes[tree]
            # print(current_item)
            access_depth[current_node[0]][current_level].append(current_node)
            t_start = time.time()
            original_node_data = self.retrieve_data(tree, current_level, node)
            time_per_level[current_level].append(time.time() - t_start)
            if original_node_data is None:
                print("Was unable to look up data " + str(tree) + ", " + str(current_level) + ", " + str(node))
                exit(1)

            if current_level != self.maintree.depth:
                (lchild, rchild) = original_node_data.get_children()
                if LSH.compareLSHstring(current_item, original_node_data.left_max_lsh):
                    next_level_queue.append((tree, lchild))
                else:
                    next_level_queue.append((tree, rchild))

            elif current_level == self.maintree.depth:
                if current_node not in leaf_nodes and not LSH.dummyLSH(original_node_data):
                    match_hashes.append(current_item)
                    leaf_nodes.append(current_node)
            # if num accesses == total accesses , break loop
            if accesses_made == self.total_accesses:
                queue = []

            if queue == [] and current_level < self.maintree.depth:
                accesses_made = 0
                current_level += 1
                rest = self.total_accesses - len(next_level_queue)
                if rest < 0:
                    next_level_queue = next_level_queue[:self.total_accesses]
                else:
                    next_level_queue += [(0, 2 ** current_level)] * rest
                assert (len(next_level_queue) == self.total_accesses)
                queue = next_level_queue
                next_level_queue = []

        # retrieve irises corresponding to returned leaf nodes
        irises = list()
        for i in match_hashes:
            returned_irises = self.check_hash_to_iris(i)
            if returned_irises is not None:
                irises+=returned_irises

        time_max = []
        for depth in time_per_level:
            if len(time_per_level[depth]) != 0:
                time_max.append(max(time_per_level[depth]))

        for depth in range(self.maintree.depth ):
            self.oram_handles[depth].close()

        return irises, leaf_nodes, nodes_visited, access_depth, num_root_matches, time_max

    def init_maps(self):
        nodes_map = []
        for st_id in range(len(self.subtrees)):
            st = self.subtrees[st_id]


            for node_id in range(st.root, st.num_nodes + 1):
                current_node = st.get_node_data(node_id)
                if node_id == st.root:
                    self.root.append(node_id)
                    root_copy = node_data(bloom_filter=None, children=current_node.get_children(),
                                          left_max_lsh=current_node.left_max_lsh)
                    current_node = root_copy
                if current_node is None:
                    raise ValueError("Cannot serialize empty node")
                    # default node that doesn't match anything
                if type(current_node) is node_data:
                    current_node.bloom_filter = None
                pickled_node = pickle.dumps(current_node)
                depth = st.get_depth(node_id)

                # if new depth, create corresponding array
                if len(nodes_map) < depth+1:
                    nodes_map.append([])
                blocks_list = self.create_blocks(pickled_node)
                for block in blocks_list:
                    nodes_map[depth -1].append((st_id, node_id, [block]))
        return nodes_map

    def build_oram(self, nodes_map):
        self.oram = [None for i in range(self.maintree.subtrees[0].get_depth()+1)]
        self.oram_map = [{} for i in range(len(self.subtrees))]
        self.oram_handles = {}

        for (depth, serialized_nodes) in enumerate(nodes_map):
            block_count = len(serialized_nodes)
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

            # self.oram_handles[depth] = PathORAM(self.files_dir + self.storage_name + str(depth ), self.oram[depth].stash,
            #                                    self.oram[depth].position_map, key=self.oram[depth].key, storage_type='file')

    def apply(self, main_tree, block_size=256):
        self.maintree = main_tree
        self.subtrees = main_tree.subtrees

        client_map = self.init_maps()
        self.build_oram(client_map)
