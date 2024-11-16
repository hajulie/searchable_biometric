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

# s = LSH output size, k = # trees, lsh_tpr = LSH true positive rate, lsh_fpr = LSH false positive rate
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
def nb_nodes_visited_per_level(l, k, b, lsh_tpr, lsh_fpr):
    depth = compute_tree_depth(l, b)
    nodes = []
    # root nodes are always visited
    nodes.append(k)

    for j in range(1, depth):
        # nodes visited if True/False LSH match (previous nodes is unique)
        lsh_nodes = (lsh_tpr + lsh_fpr) * b
        # nodes visited if False BF match (previous nodes are on path node's siblings)
        bf_nodes = (b - 1) * bf_fpr * b
        nodes.append(math.ceil(k * (lsh_nodes + bf_nodes)))
    return nodes

def expected_number_root_matches(l, k, db_size, lsh_tpr, lsh_fpr, bf_fpr):
    tp_matches = k * lsh_tpr
    fp_matches = k * lsh_fpr *db_size# ignoring BF FPR for now
    return tp_matches, fp_matches

def number_oram_accesses(l, k, nb_root_matches, oram_param):
    # with ea = with early abort, wo ea = without early abort
    accesses_with_ea = (nb_root_matches * math.log10(l) + k) * oram_param
    accesses_wo_ea = k * math.log10(l) * oram_param
    return accesses_wo_ea, accesses_with_ea

def sys_params_to_csv(l, b,  n, db_size, lsh_tpr, lsh_fpr, bf_fpr, desired_tpr, desired_fpr, desired_max_k):
    filename = 'tree_params_csv.csv'

    with open(filename, 'w+') as f:
        # create the csv writer
        writer = csv.writer(f)

        for s in range(1, 100, 1):
            lsh_tpr_s = pow(lsh_tpr, s)
            lsh_fpr_s = pow(lsh_fpr, s)
            min_trees = desired_max_k
            max_trees = 0
            tp_matches = 0
            fp_matches = 0

            for k in range(5, desired_max_k+10, 1):
                # (lsh_tpr_s, lsh_fpr_s) = compute_lsh_rates(n, s, r, c)
                (sys_tpr, sys_fpr) = compute_system_rates(k, lsh_tpr_s, lsh_fpr_s)
                # if rates not good enough, discard
                if sys_tpr > desired_tpr and sys_fpr < desired_fpr:
                    nodes_per_level = nb_nodes_visited_per_level(l, k, b, lsh_tpr_s, lsh_fpr_s)
                    nb_nodes = math.ceil(compute_number_nodes_visited(l, k, b, lsh_tpr_s, lsh_fpr_s, bf_fpr))
                    row = (s, k, sys_tpr, sys_fpr, nb_nodes, nodes_per_level)



                    # write a row to the csv file
                    # writer.writerow(row)
                    if (k < min_trees):
                        min_trees = k
                        tmp_min_tpr = sys_tpr
                        tmp_min_fpr = sys_fpr
                        tp_matches, fp_matches = expected_number_root_matches(l, k, db_size, lsh_tpr_s, lsh_fpr_s, bf_fpr)

                    if (k > max_trees):
                        max_trees = k
                        tmp_max_tpr = sys_tpr
                        tmp_max_fpr = sys_fpr


            if min_trees < desired_max_k and max_trees > 0:
                row = ("Overall", s, min_trees, round(tmp_min_tpr, 3), round(tmp_min_fpr, 6), max_trees,
                       round(tmp_max_tpr, 3), round(tmp_max_fpr, 4), round(tp_matches,3), round(fp_matches,3))
                writer.writerow(row)
                print(row)
                #exit(0)

    return filename



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # retrieve script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_file', help="Output file name", type=str, default='params_script.csv')
    parser.add_argument('--db_size', help="Number of records stored in the database", type=int, default=1000000)
    parser.add_argument('--n', help="Feature vectors size in bits", type=int, default=1024)
    parser.add_argument('--sys_tpr', help="Desired system True Positive Rate (TPR)", type=float, default=0.95)
    parser.add_argument('--sys_fpr', help="Desired system False Positive Rate (FPR)", type=float, default=0.01)
    parser.add_argument('--bf_fpr', help="Bloom Filter FPR", type=float, default=0.0001)
    # parser.add_argument('--lsh_r', help="LSH r param", type=float, default=0.3)
    # parser.add_argument('--lsh_c', help="LSH c param", type=float, default=1.7)
    parser.add_argument('--lsh_tpr', help="LSH TPR", type=float, default=0.70)
    parser.add_argument('--lsh_fpr', help="LSH FPR", type=float, default=0.5)
    parser.add_argument('--branch', help="Branching factor", type=int, default=2)
    args = parser.parse_args()

    db_size = args.db_size
    n = args.n
    branch_factor = args.branch
    desired_tpr = args.sys_tpr
    desired_fpr = args.sys_fpr
    bf_fpr = args.bf_fpr  # bloom filter fpr, default = 10^-4
    lsh_tpr = args.lsh_tpr
    lsh_fpr = args.lsh_fpr
    desired_max_k = 1000000

    print("Estimated tree depth = " + str(compute_tree_depth(db_size, branch_factor)))

    filename = sys_params_to_csv(db_size, branch_factor, n, db_size, lsh_tpr, lsh_fpr, bf_fpr, desired_tpr, desired_fpr, desired_max_k)
