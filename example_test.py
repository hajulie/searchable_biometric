import b4_main_tree
from b4_oram import *
from b4_main_tree import build_db


"""
An example of a test on a random dataset 
"""

if __name__ == '__main__':
    import random

    # n = 100
    branching_factor = 2
    fpr = 0.0001 
    temp_l = 2

    try_nums = [2] #tries multiple size dbs 

    for ind, n in enumerate(try_nums):
        print("\n---------- TEST %i ----------" % n) 
        print('\n-- size of database = %i --' %n )
        try_data = ([[random.getrandbits(1) for i in range(1024)] for i in range(n)])

        t, data = build_db(branching_factor, fpr, try_data, l = temp_l) # builds the database 
        print("t \n  ", t)
        print("data \n  ", data)

        print("tree built")
        print("sub trees:" , t.subtrees )
        
        try_search = random.randint(0,n-1)
        attempt = try_data[try_search]
        
        print("\n- Search for Iris %i, No noise - \n" % try_search) # searching with no noise 
        s = t.search(attempt)
        
        print("All nodes visited:", s[0])
        print("Matched leaf nodes:", s[1])
        print("Matched Irises:", s[2])

        #TEST WITH NOISE 
        noise = 0.10
        num_positions = math.ceil(1024*noise)
        change_index = random.sample(range(1024), num_positions)
        print("\n - Search for Iris %i, %f Noise - \n" % (try_search, noise))

        noise_search = try_data[try_search]
        for ind in change_index: 
            if noise_search[ind] == 1: 
                noise_search[ind] = 0
            else: 
                noise_search[ind] = 1
        
        s = t.search(noise_search)
        print("All nodes visited:", s[0])
        print("Matched leaf nodes:", s[1])
        print("Matched Irises:", s[2])

    print("\n --------------- TEST ORAM --------------- \n")

    storage_t = apply_storage_layer(t, oram=2)    


