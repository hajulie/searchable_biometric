import sys

import scipy

from b4_main_tree import main_tree
from b4_main_tree import build_db
from b4_oram import oblivious_ram
import os, glob, numpy
import random
import math
import time
import argparse

from scipy import stats
import matplotlib.pyplot as plt


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


def sample_errors(vector_size):
    mean_same = 0.21
    stdev_same = 0.056

    # compute n using degrees of freedom formula
    n = (mean_same * (1 - mean_same)) / (stdev_same ** 2)
    p = mean_same
    # print("p = " + str(p) + " and n = " + str(math.ceil(n)))

    error_fraction = scipy.stats.binom.rvs(math.ceil(n), p) / n
    # print(error_fraction)
    nb_errors = round(vector_size * error_fraction)
    return nb_errors, round(error_fraction, 3)


def build_rand_dataset(l, n, t, show_hist = False):
    dataset = []
    queries = []
    errors_table = []

    for i in range(l):
        feature = [random.getrandbits(1) for i in range(n)]
        dataset.append(feature)
        query = dataset[i][:]  # need to be careful to copy value ! (keep the [:] !!)

        # sample errors from distribution
        nb_errors, fraction = sample_errors(n)
        # print("Errors from normal distribution : " + str(nb_errors))
        errors_table.append(nb_errors)
        # randomly sample error bits to be inverted
        error_bits = random.sample(range(n), nb_errors)
        for b in error_bits:
            query[b] = (query[b] + 1) % 2

        queries.append(query)

    if show_hist == 1:
        build_show_histogram(dataset, queries)
    #print(errors_table)
    # plt.plot(errors_table)

    return dataset, queries


def build_ND_dataset(show_hist = False):
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

    if show_hist == 1:
        build_show_histogram(nd_templates, nd_queries)
    return nd_templates, nd_queries[:100]


def build_synthetic_dataset(l, n, t, show_hist= False):
    dataset = []
    queries = []
    labels = []
    errors_table = []
    ctr = 0

    cwd = os.getcwd()
    file_list = glob.glob(cwd + "//datasets//synthetic_dataset//*")

    for x in file_list:
        dataset.append(read_fvector(x))
        labels.append(x[len(x) - 9:])

        # create query with 30% errors
        query = read_fvector(x)

        # sample errors from distribution
        nb_errors, fraction = sample_errors(n)
        # print("Errors from normal distribution : " + str(nb_errors))
        errors_table.append(nb_errors)
        # randomly sample error bits to be inverted
        error_bits = random.sample(range(n), nb_errors)
        for b in error_bits:
            query[b] = (query[b] + 1) % 2
        queries.append(query)

        ctr = ctr + 1
        if ctr == l:
            break

    if show_hist == 1:
        build_show_histogram(dataset, queries)
    print(str(errors_table))
    return dataset, queries


# only works if tree leaves order are not randomized !!!!
def compute_sys_rates(tree, queries, parallel, oram):
    tpr = 0
    fpr = 0

    good_traversals = []
    bad_traversals = []

    leaves = tree.subtrees[0].tree.leaves()
    true_pos = 0
    false_pos = []
    visited_nodes = []
    nb_matching_roots = []

    # run queries on whole dataset
    for i in range(len(queries)):
        (returned_iris_list, leaf_nodes, nodes_visited, access_depth, num_root_matches) = tree.search(
            queries[i])  # parallel = False for now because parallel search is way slower than expected

        visited_nodes.append(sum(1 for x in nodes_visited for y in nodes_visited[x]))
        nb_matching_roots.append(num_root_matches)
        res = [item[1] for item in leaf_nodes]

        no_dup_res = list(set(returned_iris_list))
        found_iris = 0
        for iris in no_dup_res:
            if iris.identity == i:
                found_iris = 1
                true_pos = true_pos + 1

                if len(no_dup_res) > 1:
                    false_pos.append(len(no_dup_res) - 1)
                else:
                    false_pos.append(0)

        if found_iris == 0:
            false_pos.append(len(no_dup_res))

        # compute number of good & bad traversals (not ignoring duplicates)
        tmp_good_traversals = 0
        tmp_bad_traversals = 0
        for iris in returned_iris_list:
            if iris.identity == i:
                tmp_good_traversals += 1
        tmp_bad_traversals = num_root_matches - tmp_good_traversals
        good_traversals.append(tmp_good_traversals)
        bad_traversals.append(tmp_bad_traversals)

        if 0 == i % 10 and i > 0:
            print("Query number " + str(i + 1) + " of " + str(len(queries)))
            print("True Positive Rate = " + str(true_pos / (i + 1)))
            print("Avg false positives per query = " + str(sum(false_pos) / (i + 1)))
            print("Avg visited nodes per query  = " + str(sum(visited_nodes) / (i + 1)))
            print("Max root matches in a query = " + str(max(nb_matching_roots)))
            print("Avg root matches in a query = " + str(sum(nb_matching_roots) / (i + 1)))
            print("Good traversals = " + str(sum(good_traversals) / (i + 1)))
            print("Bad traversals = " + str(sum(bad_traversals) / (i + 1)))

            if oram:
                print("#ORAM accesses per query = " + str(tree.nb_oram_access / (i + 1)))
                print("Avg time ORAM node lookup = " + str((tree.time_oram_access / tree.nb_oram_access)))
                print("Avg time root search = " + str(tree.time_root_search / (i + 1)))

    print("True Positive Rate = " + str(true_pos / len(queries)))
    print("Avg false positives per query = " + str(sum(false_pos) / len(queries)))
    print("Avg visited nodes per query  = " + str(sum(visited_nodes) / len(queries)))
    print("Max root matches in a query = " + str(max(nb_matching_roots)))
    print("Avg root matches in a query = " + str(sum(nb_matching_roots) / len(queries)))
    # print("Good traversals = " + str(good_traversals))
    # print("Bad traversals = " + str(bad_traversals))
    print("Avg good traversals = " + str(sum(good_traversals) / len(queries)))
    print("Max good traversals = " + str(max(good_traversals)))
    print("Avg bad traversals = " + str(sum(bad_traversals) / len(queries)))
    print("Max bad traversals = " + str(max(bad_traversals)))

    if oram:
        print("#ORAM accesses per query = " + str(tree.nb_oram_access / len(queries)))
        print("Avg time ORAM node lookup = " + str((tree.time_oram_access / tree.nb_oram_access)))
        print("Avg time root search = " + str(tree.time_root_search / len(queries)))

    tpr = true_pos / len(queries)
    fpr = sum(false_pos) / (len(leaves) * len(queries))

    return tpr, fpr, nb_matching_roots


def plot_matching_roots(root_matches):
    dist = stats.binom
    bounds = [(0, 10), (0, 10)]
    res = stats.fit(dist, root_matches, bounds)
    print(res.params)

    res.plot()
    plt.show()


def hamming_dist(sample1, sample2):
    dist = 0
    if len(sample1) != len(sample2):
        raise ValueError

    for i in range(0, len(sample1)):
        if sample1[i] != sample2[i]:
            dist+=1/len(sample1)
    return dist

def build_show_histogram(data, queries):
    blueDistances=[]
    redDistances=[]
    for i in range(0, len(data)):
        for j in range(0, len(data)):
            if i != j:
                blueDistances.append(hamming_dist(data[i], data[j]))

        if len(queries) > i and len(queries[i]) > 0:
            if type(queries[i][0]) is int:
                diff_query = queries[i]
                redDistances.append(hamming_dist(data[i], diff_query))
            else:
                for diff_query in queries[i]:
                    redDistances.append(hamming_dist(data[i], diff_query))
        #     print(type(diff_queries))

    redWeights = [1/len(redDistances) for i in range(0, len(redDistances))]
    blueWeights = [1/len(blueDistances) for i in range(0, len(blueDistances))]
    if len(blueDistances) > 0:
        plt.hist(blueDistances, density=True, bins=41, histtype='stepfilled', weights= blueWeights,
                 color='b', alpha=0.7, label='Same')

    if len(redDistances) > 0:
        plt.hist(redDistances, density=True, bins=41, histtype='stepfilled', weights = redWeights,
                 color='r', label='Different')

    if len(blueDistances) >0 or len(redDistances) > 0:
        plt.show()

#    plt.hist(redComparisons, normed=True, bins=120, histtype='stepfilled', color='r', label='Different')
# plt.show()

def size_oram_files():
    total_file_size = 0
    for file in glob.glob("heap*"):
        total_file_size += os.stat(file).st_size
    return total_file_size


if __name__ == '__main__':
    print(sys.version)

    parser = argparse.ArgumentParser()
    parser.add_argument('--parallel', help="Use parallelization.", type=int, default=1)
    parser.add_argument('--oram', help="Use ORAM.", type=int, default=1)
    parser.add_argument('--oram_dir', help="Directory fo ORAM files storage.", type=str, default="")
    parser.add_argument('--dataset', help="Dataset to test.", type=str, default='rand')
    parser.add_argument('--dataset_size', help="Size of dataset to test.", type=int, default=356)
    parser.add_argument('--nb_trees', help="Number of trees to build.", type=int, default=630)
    parser.add_argument('--lsh_size', help="LSH output size.", type=int, default=15)
    parser.add_argument('--root_bf_fp', help="LSH output size.", type=float, default=.0001)
    parser.add_argument('--internal_bf_fp', help="LSH output size.", type=float, default=.1)
    parser.add_argument('--show_histogram', help="Show histogram for tested dataset.", type=int, default=0)
    parser.add_argument('--oram_constant_accesses', help="Constant Number of Accesses for ORAM traversal.", type=int,
                        default=100)
    parser.add_argument('--same_t', help="Avg distance between vectors from same class.", type=float, default=0.3)
    parser.add_argument('--diff_t', help="Avg distance between vectors from different class.", type=float, default=0.4)
    args = parser.parse_args()

    parallel = bool(args.parallel)
    oram = bool(args.oram)
    show_hist = bool(args.show_histogram)

    l = args.dataset_size  # dataset size
    k = args.nb_trees  # number of trees to build
    n = 1024  # vector size
    t = args.same_t
    accesses = args.oram_constant_accesses

    branching_factor = 2
    root_bf_fpr = args.root_bf_fp
    internal_bf_fpr = args.internal_bf_fp
    lsh_size = args.lsh_size  # LSH output size
    lsh_r = math.floor(t * n)
    lsh_c = args.diff_t * (n / lsh_r)
    for file in glob.glob("heap*"):
        os.remove(file)

    # build & search using random dataset
    if args.dataset == "rand" or args.dataset == "all":

        t_start = time.time()
        random_data, random_queries = build_rand_dataset(l, n, t, show_hist=show_hist)
        t_end = time.time()
        t_dataset = t_end - t_start

        t_start = time.time()
        random_tree, data = build_db(branching_factor, root_bf_fpr, internal_bf_fpr, random_data, n, lsh_r, lsh_c,
                                     lsh_size, k, parallel)
        print("total nodes = " + str(random_tree.total_nodes))
        t_end = time.time()
        t_tree = t_end - t_start

        t_start = time.time()
        if oram:
            print("Building ORAM...")
            storage_t = oblivious_ram(files_dir=args.oram_dir, total_accesses=accesses)
            print("ORAM created, now putting tree in it...")
            storage_t.apply(random_tree)
            print("ORAM finished.")
            print("Size of files " + str(size_oram_files()))
            random_tree = storage_t
        t_end = time.time()
        t_oram = t_end - t_start

        t_start = time.time()
        (rand_tpr, rand_fpr, root_matches) = compute_sys_rates(random_tree, random_queries, parallel, oram)
        t_end = time.time()
        t_search = t_end - t_start

        print("Random dataset/queries : Size dataset = " + str(len(random_data)) + " - size queries = " + str(
            len(random_queries)))
        print("Random dataset/queries : TPR = " + str(rand_tpr))
        print("Random dataset/queries : FPR = " + str(rand_fpr))
        print("Random dataset/queries : build_dataset takes " + str(t_dataset) + " seconds.")
        print("Random dataset/queries : build_index takes " + str(t_tree) + " seconds.")
        if oram:
            print("Random dataset/queries : ORAM setup takes " + str(t_oram) + " seconds.")
        print("Random dataset/queries : search takes " + str(t_search) + " seconds.")
        print("Random dataset/queries : avg number of root matches " + str(sum(root_matches) / len(root_matches)))

        # plot number of matching root nodes + binomial fit
        # plot_matching_roots(root_matches)

    # build & search using ND dataset
    if args.dataset == "nd" or args.dataset == "all":
        t_start = time.time()
        ND_data, ND_queries = build_ND_dataset(show_hist=show_hist)
        t_end = time.time()
        t_dataset = t_end - t_start

        t_start = time.time()
        ND_tree, data = build_db(branching_factor, root_bf_fpr, internal_bf_fpr, ND_data, n, lsh_r, lsh_c, lsh_size, k)
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
        (ND_tpr, ND_fpr, root_matches) = compute_sys_rates(ND_tree, ND_queries, parallel, oram)
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
        synthetic_data, synthetic_queries = build_synthetic_dataset(l, n, t, show_hist=show_hist)
        t_end = time.time()
        t_dataset = t_end - t_start

        t_start = time.time()
        synth_tree, data = build_db(branching_factor, root_bf_fpr, internal_bf_fpr, synthetic_data, n, lsh_r, lsh_c,
                                    lsh_size, k, parallel)
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
        (mixed_tpr, mixed_fpr, root_matches) = compute_sys_rates(synth_tree, synthetic_queries, parallel, oram)
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
