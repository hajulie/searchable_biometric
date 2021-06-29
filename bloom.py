from bloom_filter import BloomFilter
from treelib import Node, Tree
import math

branching_factor = 2
error_rate_value = 0.01
max_elements_value = 8

#based on an existing list of data 

def global_vars(branching_f, error_rate, max_elem):
    global branching_factor, error_rate_value, max_elements_value
    branching_factor = branching_f
    error_rate_value = error_rate
    max_elements_value = max_elem

class bftree(object):
    def __init__(self, branching_f, error_rate, max_elements):
        self.branching_factor = branching_f
        self.error_rate = error_rate
        self.max_elem = max_elem
        self.tree = None

    #creates a new bloom filter with elements from actual_elements
    def new_filter(self, num_expected_elements, actual_elements=None): 
        temp = BloomFilter(max_elements=self.max_elem, error_rate=self.error_rate)
        if actual_elements != None: 
            for i in actual_elements:
                temp.add(i)
        return temp

    #build the tree 
    def build_index(self, elements): 
        self.tree = Tree()
        current_node = 1 
        num_elements = len(elements)        

        #build root 
        bfilter_root = new_bf(num_elements, elements)
        self.tree.create_node("root", current_node, data=bfilter_root)

        level = 0 #levels will increase as tree goes down 
        tree_depth = math.ceil(num_elements/branching_factor) #calculate depth of tree
        while level != tree_depth: 
            level += 1
            nodes_in_level = self.branching_factor**level
            items_in_filter = self.branching_factor**(tree_depth-level)
            for num_node in range(nodes_in_level): 
                current_node += 1
                parent_node = current_node//self.branching_factor
                elements_in_filter = elements[num_node*items_in_filter:(num_node*items_in_filter)+items_in_filter]
                if elements_in_filter == []:
                    self.tree.create_node(current_node, None, data= None, parent=parent_node)
                else: 
                    bf = new_bf(items_in_filter, elements_in_filter)
                    self.tree.create_node(current_node, elements_in_filter, data=bf, parent=parent_node)
        return tree

    #search for item 
    def search(self, item):
        root_bf = self.tree["root"].data
        depth = self.tree.depth()
        if item in root_bf: 
            current_level = 0 
            parent = 1 
            while current_level != depth: 
                current_level += 1
                for i in range(self.branching_factor): 
                    current_node = parent*self.branching_factor + i
                    if current_node < self.max_elem: 
                        if item in self.tree[current_node].data: 
                            print(current_node)
                            parent=current_node
                            break
                    else: 
                        break
        else: 
            return False
        return True
                    




class bfilter(object): 
    def __init__(self, bloom_filter): 
        self.bloom_filter = bloom_filter

def new_bf(expected_elements, stuff=None): 
    temp = BloomFilter(max_elements= expected_elements, error_rate= error_rate_value)
    if stuff != None: 
        for i in stuff:
            temp.add(i)
    return temp

def build_index(elements): 
    tree = Tree() 
    current_node = 1
    
    bfilter_root = new_bf(len(elements), elements)
    tree.create_node("root", current_node, data=bfilter_root) #root node 
    
    level = 0
    tree_depth = math.ceil(len(elements)/2)
    while level != tree_depth:
        level += 1
        nodes_in_level = branching_factor**(level)
        items_in_filter = branching_factor**(tree_depth-level)
        for num_node in range(nodes_in_level): 
            current_node += 1
            elements_to_add = elements[num_node*items_in_filter:(num_node*items_in_filter)+items_in_filter]
            if elements_to_add == []: 
                tree.create_node(current_node, current_node, data=None, parent=current_node//branching_factor)    
            else: 
                bf = new_bf(items_in_filter, elements_to_add)
                tree.create_node(current_node, current_node, data=bf, parent=current_node//branching_factor)

    return tree

def search(tree, item): 
    bf = tree[1].data 
    depth = tree.depth()
    if item in bf: 
        current_level = 0 
        parent = 1
        while current_level != depth: 
            current_level += 1
            for i in range(branching_factor):
                current_node = parent*branching_factor+i
                if current_node < depth*branching_factor:
                    if item in tree[current_node].data: 
                        print(parent*branching_factor)
                        parent=parent*branching_factor
                else: 
                    break
    else: 
        return False
    return True




t = build_index(['John', 'Jane', 'Smith', 'Doe', 'Abe'])
t.show()
r = t.get_node(4)
print(r)
print(r.data.num_bits_m) #this is how to get the bits of the filter from the bloom filter object 
# print(search(t, 'Abe'))
# print(search(t, 'Jen'))
