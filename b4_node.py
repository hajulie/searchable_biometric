#bloom4, each tree is a lsh 

from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as eLSH_import
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad

import pyoram
from pyoram.util.misc import MemorySize
from pyoram.oblivious_storage.tree.path_oram import PathORAM

class node(object): 
    def __init__(self, bloom_filter):
        self.bloom_filter = bloom_filter
        self.items = [] 
    
    def add_item(self, item): 
        self.bloom_filter.add(str(item))
        self.items.append(item)

    def add_multiple(self, items): 
        print("add mul items:", items)
        if type(items[0]) == list:
            for i in items:
                print("add:", i)
                self.add_item(i) 
        else: 
            print("add:", items)
            self.add_item(items)

    def in_bloomfilter(self, item): 
        str_item = str(item)
        print("in bf item:", item)
        print("node items:", self.items)
        print("tf:", str_item in self.bloom_filter)
        return str_item in self.bloom_filter