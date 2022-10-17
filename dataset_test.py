import sys

from b4_main_tree import main_tree
from b4_main_tree import build_db
from b4_oram import oblivious_ram
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
        error_bits = random.sample(range(n), math.floor(n * t))
        for b in error_bits:
            query[b] = (query[b] + 1) % 2

        queries.append(query)

    return dataset, queries


def build_ND_dataset():
    cwd = os.getcwd()
    dir_list = glob.glob(cwd + "//datasets//nd_dataset//*")
    nd_dataset = {}
    class_labels = {}
    i = 0
    for dir in dir_list:
        feat_list = glob.glob(dir + "//*")
        nd_dataset[i] = [read_fvector(x) for x in feat_list]
        class_labels[i] = dir
        i = i + 1

    nd_templates = [nd_dataset[x][0] for x in nd_dataset]
    nd_queries = [nd_dataset[x][1] for x in nd_dataset]

    return nd_templates, nd_queries


def build_synthetic_dataset(l, n, t):
    dataset = []
    queries = []
    labels = []
    ctr = 0

    cwd = os.getcwd()
    file_list = glob.glob(cwd + "//datasets//synthetic_dataset//*")
    for x in file_list:
        dataset.append(read_fvector(x))
        labels.append(x[len(x) - 9:])

        # create query with 30% errors
        query = read_fvector(x)
        # randomly sample t error bits to be inverted
        error_bits = random.sample(range(n), math.floor(n * t))
        for b in error_bits:
            query[b] = (query[b] + 1) % 2
        queries.append(query)

        ctr = ctr + 1
        if ctr > l:
            break

    return dataset, queries


# def build_mixed_dataset(data1, queries1, l1, data2, l2):
#     data = []
#     queries = []
#
#     # randomly pick l1 vectors and queries from dataset 1
#     chosen_ones = random.sample(range(len(data1)), l1)
#     for i in chosen_ones:
#         data.append(data1[i])
#         queries.append(queries1[i])
#
#     # randomly pick l2 vectors from dataset 2
#     chosen_ones = random.sample(range(len(data2)), l2)
#     for i in chosen_ones:
#         data.append(data2[i])
#
#     return data, queries


# only works if tree leaves order are not randomized !!!!

def compute_sys_rates(tree, queries, parallel):
    tpr = 0
    fpr = 0

    leaves = tree.subtrees[0].tree.leaves()
    true_pos = 0
    false_pos = []
    visited_nodes = []

    # run queries on whole dataset
    for i in range(len(queries)):
        # false_pos = 0

        leaves_match = tree.search(
            queries[i])  # parallel = False for now because parallel search is way slower than expected

        #print(leaves_match)
        if len(leaves_match) > 2:
            visited_nodes.append(len(leaves_match[2]))

        if i%10 == 0:
            print("query = " + str(i))
        #print("result : (returned_iris, leaf_nodes, nodes_visited, access_depth)")
        #print(leaves_match)

        # get rid of duplicates in results
        # res = list(set([item for sublist in leaves_match[1] for item in sublist]))
        res = list(set([item[1] for item in leaves_match[1]]))

        if int(leaves[i].tag) in res:
            true_pos = true_pos + 1
            if len(res) > 1:
                false_pos.append(len(res) - 1)
        elif len(res) != 0:
            false_pos.append(len(res))

        # fpr = fpr + false_pos/len(leaves)

    print("True positives = " + str(true_pos))
    print("False positives: " + str(false_pos))
    print("Nodes visited: " + str(visited_nodes))
    print("Avg #false positives per query = " + str(sum(false_pos) / len(queries)))
    print("Avg #visited nodes per query  = " + str(sum(visited_nodes) / len(queries)))

    tpr = true_pos / len(queries)
    fpr = sum(false_pos) / (len(leaves) * len(queries))

    return tpr, fpr


if __name__ == '__main__':
    print(sys.version)

    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', help="Use parallelization.", type=int, default=1)
    parser.add_argument('--oram', help="Use ORAM.", type=int, default=1)
    parser.add_argument('--oram_dir', help="Directory fo ORAM files storage.", type=str, default="")
    parser.add_argument('--dataset', help="Dataset to test.", type=str, default='rand')
    parser.add_argument('--dataset_size', help="Size of dataset to test.", type=int, default=356)
    parser.add_argument('--nb_trees', help="Number of trees to build.", type=int, default=4000)
    parser.add_argument('--lsh_size', help="LSH output size.", type=int, default=20)
    parser.add_argument('--oram_constant_accesses', help="Constant Number of Accesses for ORAM traversal.", type=int, default=100)
    parser.add_argument('--same_t', help="Avg distance between vectors from same class.", type=float, default=0.3)
    parser.add_argument('--diff_t', help="Avg distance between vectors from different class.", type=float, default=0.4)
    args = parser.parse_args()

    parallel = bool(args.parallel)
    oram = bool(args.oram)

    l = args.dataset_size  # dataset size
    k = args.nb_trees  # number of trees to build
    n = 1024  # vector size
    t = args.same_t
    accesses = args.oram_constant_accesses

    branching_factor = 2
    bf_fpr = 0.0001  # Bloom Filter FPR (same for every BFs for now)
    lsh_size = args.lsh_size  # LSH output size
    lsh_r = math.floor(t * n)
    lsh_c = args.diff_t * (n / lsh_r)

    # build & search using random dataset
    if args.dataset == "rand" or args.dataset == "all":
        # lsh_size=5
        k = args.nb_trees

        # t=0
        # oram = False

        t_start = time.time()
        random_data, random_queries = build_rand_dataset(l, n, t)
        t_end = time.time()
        t_dataset = t_end - t_start

        t_start = time.time()
        random_tree, data = build_db(branching_factor, bf_fpr, random_data, n, lsh_r, lsh_c, lsh_size, k, parallel)
        print("total nodes = " + str(random_tree.total_nodes))
        t_end = time.time()
        t_tree = t_end - t_start

        # print("Root nodes lists:")
        # print(random_tree.search_root_nodes(random_queries))

        t_start = time.time()
        if oram:
            print("Building ORAM...")
            storage_t = oblivious_ram(files_dir=args.oram_dir, total_accesses=accesses)
            print("ORAM created, now putting tree in it...")
            storage_t.apply(random_tree)
            print("ORAM finished.")
            random_tree = storage_t
        t_end = time.time()
        t_oram = t_end - t_start

        t_start = time.time()
        (rand_tpr, rand_fpr) = compute_sys_rates(random_tree, random_queries, parallel)
        t_end = time.time()
        t_search = t_end - t_start

        print("Random dataset/queries : Size dataset = " + str(len(random_data)) + " - size queries = " + str(
            len(random_queries)))
        print("Random dataset/queries : TPR = " + str(rand_tpr))
        print("Random dataset/queries : FPR = " + str(rand_fpr))
        print("Random dataset/queries : build_dataset takes " + str(t_dataset) + " seconds.")
        print("Random dataset/queries : build_index takes " + str(t_tree) + " seconds.")
        print("Random dataset/queries : ORAM setup takes " + str(t_oram) + " seconds.")
        print("Random dataset/queries : search takes " + str(t_search) + " seconds.")

    # build & search using ND dataset
    if args.dataset == "nd" or args.dataset == "all":
        t_start = time.time()
        ND_data, ND_queries = build_ND_dataset()
        t_end = time.time()
        t_dataset = t_end - t_start

        t_start = time.time()
        ND_tree, data = build_db(branching_factor, bf_fpr, ND_data, n, lsh_r, lsh_c, lsh_size, k)
        print("total nodes = " + str(ND_tree.total_nodes))
        t_end = time.time()
        t_tree = t_end - t_start
        t_start = time.time()

        # print("Root nodes lists:")
        # print(ND_tree.search_root_nodes(ND_queries[0]))
        # for q in synthetic_queries:
        #     print(synth_tree.search_root_nodes(q))

        t_start = time.time()
        if oram:
            storage_t = oblivious_ram(files_dir=args.oram_dir, total_accesses=accesses)
            storage_t.apply(ND_tree)
            ND_tree = storage_t
        t_end = time.time()
        t_oram = t_end - t_start

        t_start = time.time()
        (ND_tpr, ND_fpr) = compute_sys_rates(ND_tree, ND_queries, parallel)
        t_end = time.time()
        t_search = t_end - t_start

        print("ND 0405 dataset/queries : Size dataset = " + str(len(ND_data)) + " - size queries = " + str(
            len(ND_queries)))
        print("ND 0405 dataset/queries : TPR = " + str(ND_tpr))
        print("ND 0405 dataset/queries : FPR = " + str(ND_fpr))
        print("ND 0405 dataset/queries : build_dataset takes " + str(t_dataset) + " seconds.")
        print("ND 0405 dataset/queries : build_index takes " + str(t_tree) + " seconds.")
        print("ND 0405 dataset/queries : ORAM setup takes " + str(t_oram) + " seconds.")
        print("ND 0405 dataset/queries : search takes " + str(t_search) + " seconds.")

    # build & search using synthetic dataset
    if args.dataset == "synth" or args.dataset == "all":

        t_start = time.time()
        synthetic_data, synthetic_queries = build_synthetic_dataset(l, n, t)
        t_end = time.time()
        t_dataset = t_end - t_start

        t_start = time.time()
        synth_tree, data = build_db(branching_factor, bf_fpr, synthetic_data, n, lsh_r, lsh_c, lsh_size, k, parallel)
        print("total nodes = " + str(synth_tree.total_nodes))
        t_end = time.time()
        t_tree = t_end - t_start

        t_start = time.time()
        if oram:
            storage_t = oblivious_ram(files_dir=args.oram_dir, total_accesses=accesses)
            storage_t.apply(synth_tree)
            synth_tree = storage_t
        t_end = time.time()
        t_oram = t_end - t_start

        t_start = time.time()
        (mixed_tpr, mixed_fpr) = compute_sys_rates(synth_tree, synthetic_queries, parallel)
        t_end = time.time()
        t_search = t_end - t_start

        print("Synthetic dataset/queries : Size dataset = " + str(len(synthetic_data)) + " - size queries = " + str(
            len(synthetic_queries)))
        print("Synthetic dataset/queries : TPR = " + str(mixed_tpr))
        print("Synthetic dataset/queries : FPR = " + str(mixed_fpr))
        print("Synthetic dataset/queries : build_dataset takes " + str(t_dataset) + " seconds.")
        print("Synthetic dataset/queries : build_index takes " + str(t_tree) + " seconds.")
        print("Synthetic dataset/queries : ORAM setup takes " + str(t_oram) + " seconds.")
        print("Synthetic dataset/queries : search takes " + str(t_search) + " seconds.")
