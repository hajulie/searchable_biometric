#bloom4, each tree is a lsh 

from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as eLSH_import
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad

# import concurrent.futures
# from pathos.multiprocessing import ProcessingPool as Pool, cpu_count
import multiprocessing as mp
from joblib import Parallel, delayed

import pyoram
from pyoram.util.misc import MemorySize
from pyoram.oblivious_storage.tree.path_oram import PathORAM

from b4_node import node
from b4_subtree import subtree
from b4_iris import iris

# storage_name = "heap.bin"

class main_tree(object): 

    def __init__(self, branching_factor, error_rate, n=1024, r=307, c=0.5*(1024/307), s=12, l=1000): 
        self.branching_factor = branching_factor
        self.error_rate = error_rate
        self.max_elem = None

        self.depth = None
        self.root = branching_factor - 1

        self.eLSH = None
        self.n = n
        self.r = r
        self.c = c
        self.s = s #samples s bits l times 
        self.l = l
        self.lsh = None
        self.hash = [ [] for i in range(l) ] #lsh output 

        # self.subtrees = [None for i in range(l)] #keeps track of subtrees
        self.subtrees = []
        self.hash_to_iris = {}

        self.total_nodes = 0 

    #compute eLSH and returns the list of length l

    def compute_eLSH_one(self, element):
        output = self.eLSH.hash(element) #length of l 

        for index, h in enumerate(output):
            self.hash[index] += [h] 
            if str(h) in self.hash_to_iris:
                self.hash_to_iris[str(h)] += [element]
            else: 
                self.hash_to_iris[str(h)] = [element]
        return output

    def compute_eLSH(self, elements): #computes the mapping from hash to iris 
        for i in elements: 
            self.compute_eLSH_one(i)

    #creates a new node: bloom filter with elements from actual_elements
    def new_node(self, num_expected_elements, actual_elements=None): 
        bf = BloomFilter(max_elements=(self.l*num_expected_elements), error_rate=self.error_rate)
        n = node(bf)
        return n

    #TREE SPECIFIC FUNCS
    def build_index(self, elements, parallel=False):
        num_elements = len(elements)
        level = 0 #levels increase going down 

        self.eLSH = eLSH_import.eLSH(LSH, self.n, self.r, self.c, self.s, self.l)
        self.lsh = self.eLSH.hashes
        self.compute_eLSH(elements)

        if parallel:
            self.subtrees = Parallel(n_jobs=2 * mp.cpu_count())(delayed(subtree.create_subtree)(self.branching_factor, self.error_rate, h, elements)
                                           for h in self.lsh)

            # lsh_list_dividers = []
            # for p in range(processes):
            #     start = math.ceil(p * self.l / processes)
            #     end = math.ceil((p + 1) * self.l / processes)
            #     lsh_list_dividers.append((start, end))
            #
            # # for (s, t) in lsh_list_dividers:
            # #     st_list, nodes = subtree.create_subtree(self.branching_factor, self.error_rate, self.lsh[s:t], elements)
            # #     self.subtrees += st_list
            # #     self.total_nodes += nodes
            #
            # with Pool(processes) as p:
            #     with concurrent.futures.ProcessPoolExecutor(processes) as executor:
            #         future_list = {executor.submit(subtree.create_subtree, self.branching_factor, self.error_rate, self.lsh[start:end], elements)
            #                        for (start, end) in lsh_list_dividers
            #                         }
            #
            #         for future in concurrent.futures.as_completed(future_list):
            #             res = future.result()
            #
            #             if res is not None:
            #                 self.subtrees += res[0]
            #                 self.total_nodes += res[1]

        else:
            for h in self.lsh:
                st = subtree.create_subtree(self.branching_factor, self.error_rate, h, elements)
                self.subtrees.append(st)
                self.total_nodes += st.num_nodes

        # print(self.subtrees) #print subtrees
        # for i in self.subtrees: 
            # print("subtree:", i)
            # print("show", i.tree)

        # print("Number of subtrees = " + str(len(self.subtrees)))

    # TODO parallelize subtree search
    def search(self, item, parallel=False):
        nodes_visited = [] 
        leaf_nodes = [] 
        returned_iris = [] 
        access_depth = [] #nodes accessed per depth

        if parallel:
            res = Parallel(n_jobs=mp.cpu_count(), prefer="threads")(delayed(subtree.search_subtree)(st, item)
                for st in self.subtrees)

            for st_res in res:
                nodes_visited += st_res[0]
                leaf_nodes += st_res[1]
                access_depth += st_res[2]

            # print(results)
            # cpus = mp.cpu_count()
            #
            # subtrees_dividers = []
            # for p in range(cpus):
            #     start = math.ceil(p * self.l / cpus)
            #     end = math.ceil((p + 1) * self.l / cpus)
            #     subtrees_dividers.append((start, end))
            #
            # results = Parallel(n_jobs=2 * cpus)(delayed(subtree.search_subtree)(self.subtrees[start:end], item)
            #                                               for (start, end) in subtrees_dividers)

            # for (s, t) in subtrees_dividers:
            #     st_nodes, st_leaves, st_depth = subtree.search_subtree(self.subtrees[s:t], item)
            #     nodes_visited += st_nodes
            #     leaf_nodes += st_leaves
            #     access_depth += st_depth

            # with Pool(processes) as p:
            #     with concurrent.futures.ProcessPoolExecutor(processes) as executor:
            #         future_list = {executor.submit(subtree.search_subtree, self.subtrees[start:end], item)
            #                        for (start, end) in subtrees_dividers
            #                        }
            #
            #         for future in concurrent.futures.as_completed(future_list):
            #             res = future.result()
            #
            #             if res is not None:
            #                 nodes_visited += res[0]
            #                 leaf_nodes += res[1]
            #                 access_depth += res[2]

        else:
            # nodes_visited, leaf_nodes, access_depth = subtree.search_subtree(self.subtrees, item)
            for st in self.subtrees:
                st_nodes, st_leaf, st_access = subtree.search_subtree(st, item)
                nodes_visited += st_nodes
                leaf_nodes += st_leaf
                access_depth += access_depth

        return nodes_visited, leaf_nodes, returned_iris, access_depth

if __name__ == '__main__':
    #small test 
    import random

    # n = 100
    fpr = 0.0001 
    temp_l = 2

    try_nums = [2]

    for n in try_nums: 
        # print('\n--- size of database = %i ---' %n )
        try_data = ([[random.getrandbits(1) for i in range(1024)] for i in range(n)])

        # temp1 = iris(try_data[0])
        # print((temp1))


        t = main_tree(2, fpr, l = temp_l)
        t.build_index(try_data)
        # print("tree built")
        # t.tree.show()
        child = random.randint(0,n-1)
        attempt = try_data[child]
        p_child = child
        # print("Depth of tree: ", t.tree.depth())
        # print("Search for leaf %i" % p_child)
        s = t.search(attempt)
        # print("All nodes visited:", s[0])
        # print("Matched leaf nodes:", s[1])
        # print("Nodes matched at each level:", s[2])
        
        match = 0 
        non = 0
        for i in s[3]: 
            for r in i: 
                if r == attempt: 
                    match += 1
                else: 
                    non += 1 

        # print("Matches:", match)
        # print("Non Matches:", non)

