import argparse
import math
import csv

# l = #records, b = branching factor
def compute_tree_depth(l, b):
    return math.floor(math.log((b-1)*l, b))

# n = input size and s = output size of (r ,cr, tpr, fpr)-sensitive hash family.
def compute_lsh_rates(n, s, r, c):
    tpr = pow(1 - r/n, s)
    fpr = pow(1 - (c*r)/n, s)
    return tpr, fpr

# k = # trees, lsh_tpr = LSH true positive rate, lsh_fpr = LSH false positive rate
def compute_system_rates(k, lsh_tpr, lsh_fpr):
    tpr = 1 - pow(1 - lsh_tpr, k)
    fpr = 1 - pow(1 - lsh_fpr, k)
    return tpr, fpr

# l = # records, k = # trees, b = branching factor, lsh_tpr = LSH true positive rate, lsh_fpr = LSH false positive rate
# bf_fpr = Bloom Filter false positive rate
def compute_number_nodes_visited(l, k, b, lsh_tpr, lsh_fpr, bf_fpr):
    depth = compute_tree_depth(l, b)

    # reminders:
    # - match in BF => all children are visited
    # - if BF FPR is low enough, proba that visited children also match becomes negligible so ignore cascading BF false matches
    # - always only 1 LSH match per tree (TP or FP)

    # root node is always visited
    nb_nodes = k

    # following expectations are for  single tree
    # expected number of node when no LSH match = #children * Pr[BF false match]
    nb_nodes_bf_fp = b * bf_fpr
    # print("Expected number nodes visited due to BF False Positive = " + str(nb_nodes_bf_fp))

    # expected number of nodes for LSH True/False match:
    # number of BF nodes in path to LSH matched leaf = depth
    # for each of those nodes, number of children to always visit  = branching factor
    # for visited BF nodes not in leaf path, probability of visiting children = bf_fpr
    nb_nodes_lsh_tpr = lsh_tpr * (depth * b + (depth - 1) * (b - 1) * b * bf_fpr)
    # print("Expected number nodes visited due to LSH True Positive = " + str(nb_nodes_lsh_tpr))

    nb_nodes_lsh_fpr = lsh_fpr * (depth * b + (depth - 1) * (b - 1) * b * bf_fpr)
    # print("Expected number nodes visited due to LSH False Positive = " + str(nb_nodes_lsh_fpr))

    # multiply by #trees to get overall expectation
    nb_nodes += k * (nb_nodes_bf_fp + nb_nodes_lsh_tpr + nb_nodes_lsh_fpr)
    return nb_nodes

# l = # records, k = # trees, b = branching factor, s = LSH output size
def nb_nodes_visited_per_level(l, k, b, s):
    return


def sys_params_to_csv(l, b,  n, r, c, bf_fpr, desired_tpr, desired_fpr):
    filename = 'tree_params_csv.csv'
    with open(filename, 'w+') as f:
        # create the csv writer
        writer = csv.writer(f)

        for s in range(10, 50, 2):
            for k in range(1000, 50000, 1000):
                (lsh_tpr, lsh_fpr) = compute_lsh_rates(n, s, r, c)
                (sys_tpr, sys_fpr) = compute_system_rates(k, lsh_tpr, lsh_fpr)

                # if rates not good enough, discard
                if sys_tpr > desired_tpr and sys_fpr < desired_fpr:
                    nb_nodes = math.floor(compute_number_nodes_visited(l, k, b, lsh_tpr, lsh_fpr, bf_fpr))
                    row = (s, k, sys_tpr, sys_fpr, nb_nodes)

                    # write a row to the csv file
                    writer.writerow(row)

    return filename

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # retrieve script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_file', help="Output file name", type=str, default='params_script.csv')
    parser.add_argument('--db_size', help="Number of records stored in the database", type=int, default=1000000)
    parser.add_argument('--sys_tpr', help="Desired system True Positive Rate (TPR)", type=float, default=0.95)
    parser.add_argument('--sys_fpr', help="Desired system False Positive Rate (FPR)", type=float, default=0.01)
    parser.add_argument('--bf_fpr', help="Bloom Filter FPR", type=float, default=0.0001)
    parser.add_argument('--branch', help="Branching factor", type=int, default=2)
    args = parser.parse_args()

    db_size = args.db_size
    branch_factor = args.branch
    desired_tpr = args.sys_tpr
    desired_fpr = args.sys_fpr
    bf_fpr = args.bf_fpr  # bloom filter fpr, default = 10^-4
    k = 10000

    print("Estimated tree depth = " + str(compute_tree_depth(db_size, branch_factor)))

    n = 1024
    t = 0.3
    r = t*n
    c = 1.7
    lsh_size = 21

    print("r = " + str(r) + ", cr = " + str(c*r))

    (lsh_tpr, lsh_fpr) = compute_lsh_rates(n, lsh_size, r, c)
    print("LSH TPR = " + str(lsh_tpr))
    print("LSH FPR = " + str(lsh_fpr))

    # (sys_tpr, sys_fpr) = compute_system_rates(k, lsh_tpr, lsh_fpr)
    # print("SYSTEM TPR = " + str(sys_tpr))
    # print("SYSTEM FPR = " + str(sys_fpr))
    # print("# False positive matches = " + str(k*lsh_fpr))

    # nb_nodes = compute_number_nodes_visited(db_size, k, branch_factor, lsh_tpr, lsh_fpr, bf_fpr)
    # print("Total number of nodes visited = " + str(nb_nodes))
    # print("k log n = " + str(k * math.log2(db_size)))

    filename = sys_params_to_csv(db_size, branch_factor, n, r, c, bf_fpr, desired_tpr, desired_fpr)
