from b4_main_tree import main_tree
import os, glob, numpy
import random
import math
import time
import argparse




def compare_vectors(v1, v2):
    for i in range(len(v1)):
        if v1[i] != v2[i]:
            return False
    return True

def read_fvector(filePath):
    with open(filePath) as f:
        for line in f.readlines():
            temp_str = numpy.fromstring(line, sep=",")
            return [int(x) for x in temp_str]

def compute_tree_depth(b, nb_nodes):
    return math.floor(math.log(nb_nodes, b))

def build_rand_dataset(l, n, t):
    dataset = []
    queries = []

    for i in range(l):
        feature = [random.getrandbits(1) for i in range(n)]
        dataset.append(feature)
        query = dataset[i][:]

        # randomly sample t error bits to be inverted
        error_bits = random.sample(range(n), math.floor(n*t))
        for b in error_bits:
            query[b] = (query[b] + 1) % 2

        queries.append(query)

    return dataset, queries

def build_ND_dataset():
    cwd = os.getcwd()
    dir_list = glob.glob(cwd + "//datasets//nd_dataset//*")
    nd_dataset={}
    class_labels={}
    i=0
    for dir in dir_list:
        feat_list = glob.glob(dir+"//*")
        nd_dataset[i] = [read_fvector(x) for x in feat_list]
        class_labels[i] = dir
        i = i+1

    nd_templates = [nd_dataset[x][0] for x in nd_dataset]
    nd_queries = [nd_dataset[x][1] for x in nd_dataset]

    return nd_templates, nd_queries

def build_synthetic_dataset():
    dataset = []
    labels = []

    cwd = os.getcwd()
    file_list = glob.glob(cwd + "//datasets//synthetic_dataset//*")
    for x in file_list:
        dataset.append(read_fvector(x))
        labels.append(x[len(x)-9:])

    return dataset

def build_mixed_dataset(data1, queries1, l1, data2, l2):
    data = []
    queries = []

    # randomly pick l1 vectors and queries from dataset 1
    chosen_ones = random.sample(range(len(data1)), l1)
    for i in chosen_ones:
        data.append(data1[i])
        queries.append(queries1[i])

    # randomly pick l2 vectors from dataset 2
    chosen_ones = random.sample(range(len(data2)), l2)
    for i in chosen_ones:
        data.append(data2[i])

    return data, queries


def compute_sys_rates(tree, queries):
    tpr = 0
    fpr = 0

    leaves = tree.subtrees[0].tree.leaves()
    true_pos = 0

    # run queries on whole dataset
    for i in range(len(queries)):

        false_pos = 0
        res = tree.search(queries[i])

        print("query = " + str(i))
        print("result : (nodes_visited, leaf_nodes, returned_iris, access_depth)")
        print(res)

        if int(leaves[i].tag) in res[1]:
            true_pos = true_pos + 1
            tpr = tpr + 1
            if len(res[1]) > 1:
                false_pos = false_pos + len(res[1]) - 1
        elif len(res[1]) != 0:
            false_pos = false_pos + len(res[1])

        fpr = fpr + false_pos/len(leaves)

    print("# true positives = " + str(true_pos))
    print("# false positives = " + str(false_pos))

    tpr = tpr/len(queries)
    fpr = fpr/len(queries)

    return tpr, fpr


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', help="Dataset to test.", type=str, default='rand')
    parser.add_argument('--nb_trees', help="Number of trees to build.", type=int, default=4000)
    parser.add_argument('--lsh_size', help="LSH output size.", type=int, default=20)
    args = parser.parse_args()

    l = 356 # dataset size
    k = args.nb_trees # number of trees to build
    n = 1024 # vector size

    branching_factor = 2
    bf_fpr = 0.0001 # Bloom Filter FPR (same for every BFs for now)
    lsh_size = args.lsh_size # LSH output size
    lsh_r = 307
    lsh_c = 0.5 * (1024 / 307)

    # build & search using random dataset
    if args.dataset == "rand" or args.dataset == "all":
        random_data, random_queries = build_rand_dataset(l, n, 0.3)

        random_tree = main_tree(branching_factor, bf_fpr, n, lsh_r, lsh_c, lsh_size, k)
        t_start = time.time()
        random_tree.build_index(random_data)
        t_end = time.time()

        (rand_tpr, rand_fpr) = compute_sys_rates(random_tree, random_queries)
        print("Random dataset/queries : TPR = " + str(rand_tpr) + " - FPR = " + str(rand_fpr))
        print("Random dataset/queries : build_index takes " + str(t_end - t_start) + " seconds.")

    # build & search using ND dataset
    if args.dataset == "nd" or args.dataset == "all":
        ND_data, ND_queries = build_ND_dataset()
        ND_tree = main_tree(branching_factor, bf_fpr, l)
        t_start = time.time()
        ND_tree.build_index(ND_data)
        t_end = time.time()

        (ND_tpr, ND_fpr) = compute_sys_rates(ND_tree, ND_queries)
        print("ND 0405 dataset/queries : TPR = " + str(ND_tpr) + " - FPR = " + str(ND_fpr))
        print("ND 0405 dataset/queries : build_index takes " + str(t_end - t_start) + " seconds.")

    # build & search with mix of ND and synthetic dataset (150/206) and queries from ND (150)
    if args.dataset == "synth" or args.dataset == "all":
        # retrieve both synthetic and ND datasets
        synthetic_data = build_synthetic_dataset()
        ND_data, ND_queries = build_ND_dataset()

        # build mixed dataset and corresponding queries
        mixed_data, mixed_queries = build_mixed_dataset(ND_data, ND_queries, 20, synthetic_data, 336)

        mixed_tree = main_tree(branching_factor, bf_fpr, l)
        t_start = time.time()
        mixed_tree.build_index(mixed_data)
        t_end = time.time()
        (mixed_tpr, mixed_fpr) = compute_sys_rates(mixed_tree, mixed_queries)
        print("Mixed synthetic & ND dataset/queries : TPR = " + str(mixed_tpr) + " - FPR = " + str(mixed_fpr))
        print("Mixed synthetic & ND dataset/queries : build_index takes " + str(t_end - t_start) + " seconds.")

