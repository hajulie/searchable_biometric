#bloom4, each tree is a lsh 

from bloom_filter2 import BloomFilter
from treelib import Node, Tree
import math, os, sys
import eLSH as eLSH_import
from LSH import LSH
import pickle
from Crypto.Util.Padding import pad, unpad

class node_data(object):
    def __init__(self, bloom_filter, children, left_max_lsh=None):
        self.bloom_filter = bloom_filter
        self.children = children
        self.max_lsh = None
        self.left_max_lsh = left_max_lsh

    def __reduce__(self):
        return self.__class__, (self.bloom_filter, self.children, self.left_max_lsh)
    
    def add_item(self, item):
        self.bloom_filter.add(str(item))

    def add_multiple(self, items):
        if items is None or len(items) == 0:
            return
        if type(items[0]) == list:
            for i in items:
                self.add_item(i) 
        else: 
            self.add_item(items)
    
    def add_child(self, child):
        # child is node identifier number
        self.children.append(child)
    
    def get_children(self):
        return self.children

    def in_bloomfilter(self, item): 
        str_item = str(item)
        return str_item in self.bloom_filter

    def add_children_lsh(self, lchild, rchild):
        if type(lchild) is list and type(rchild) is list:
            self.max_lsh = rchild
            self.left_max_lsh = lchild

        else:
            if type(lchild) is not node_data or type(rchild) is not node_data:
                raise TypeError()

            self.max_lsh = rchild.max_lsh
            self.left_max_lsh = lchild.max_lsh



    
    # def add_iris(self, iris):
    #     self.irises.append(iris)




class Iris(object): 
    def __init__(self, vector, identity): 
        self.vector = vector
        self.identity = identity

    def __repr__(self):
        return str(self.identity)
    
    def print_vector(self): 
        return str(self.iris)

# converts array of bits to iris object
def to_iris(str_data): 
    newiris = []
    for index, i in enumerate(str_data):
        if type(i) == list: 
            newiris.append(Iris(i, index))
        else: 
            newiris.append(i)
    return newiris
