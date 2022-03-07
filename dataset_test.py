from b4_main_tree import main_tree
import random
import math
import time

def compute_tree_depth(b, nb_nodes):
    return math.floor(math.log(nb_nodes, b))

def build_rand_dataset(l, n, t):
    dataset = []
    queries = []

    for i in range(l):
        feature = [random.getrandbits(1) for i in range(n)]
        dataset.append(feature)

        query = dataset[i]
        for j in range(math.floor(n*t)):
            b = random.randint(0, n-1)
            query[b] = (query[b] + 1) % 2
        queries.append(query)

    return dataset, queries


def build_ND_dataset():
    dataset = []
    queries = []
    return dataset, queries

def build_synthetic_dataset():
    dataset = []
    queries = []
    return dataset, queries


def compute_sys_rates(tree, queries):
    tpr = 0
    fpr = 0

    leaves = tree.subtrees[0].tree.leaves()

    # run queries on whole dataset
    for i in range(len(queries)):
        true_pos = 0
        false_pos = 0
        res = tree.search(queries[i])

        print("query = " + str(i))
        print("result : (nodes_visited, leaf_nodes, returned_iris, access_depth)")
        print(res)

        if int(leaves[i].tag) in res[1]:
            true_pos = true_pos + 1
            if len(res[1]) > 1:
                false_pos = false_pos + len(res[1]) - 1
        elif len(res[1]) != 0:
            false_pos = false_pos + len(res[1])

        tpr = tpr + true_pos
        fpr = fpr + false_pos/len(leaves)

    tpr = tpr/len(queries)
    fpr = fpr/len(queries)

    return tpr, fpr


if __name__ == '__main__':

    l = 356 # dataset size
    k = 1000 # number of trees to build
    n = 1024 # vector size

    branching_factor = 2
    bf_fpr = 0.0001 # Bloom Filter FPR (same for every BFs for now)
    lsh_size = 12 # LSH output size
    lsh_r = 307
    lsh_c = 0.5 * (1024 / 307)

    # build & search using random dataset
    random_data, random_queries = build_rand_dataset(l, n, 0.3)
    random_tree = main_tree(branching_factor, bf_fpr, n, lsh_r, lsh_c, lsh_size, k)
    t_start = time.time()
    # TODO debug - fail to build tree for l = 5, 6, 9, 10, maybe other values I haven't tested)
    random_tree.build_index(random_data)
    t_end = time.time()



    # print(len(random_data))
    # print(len(random_queries))

    (rand_tpr, rand_fpr) = compute_sys_rates(random_tree, random_queries)
    print("Random dataset/queries : TPR = " + str(rand_tpr) + " - FPR = " + str(rand_fpr))
    print("build_index takes " + str(t_end - t_start) + " seconds.")

    # # build & search using ND dataset
    # ND_data, ND_queries = build_ND_dataset()
    # ND_tree = main_tree(branching_factor, bf_fpr, l)
    # ND_tree.build_index(ND_data)
    # compute_sys_rates(ND_tree, ND_queries)
    #
    # # build & search using synthetic dataset
    # synthetic_data, synthetic_queries = build_synthetic_dataset()
    # synthetic_tree = main_tree(branching_factor, bf_fpr, l)
    # synthetic_tree.build_index(synthetic_data)
    # compute_sys_rates(synthetic_tree)

