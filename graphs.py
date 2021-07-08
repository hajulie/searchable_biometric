import matplotlib.pyplot as plt
import numpy as np
import csv, statistics, copy
from test_data import *

colors = ['g', 'b', 'r', 'c']
diff_branching = [2, 3, 5, 10]
diff_false_pos = [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]

def build_tests(): #tests to get info of building the tree 
    axis = ['false_positive_rate', 'total_storage', 'time']
    branch_dicts = [{'false_positive_rate': [], 'total_storage': [], 'time': []} for i in range(len(diff_branching))] #[branch fact 2, 3, 5, 10]

    with open('tests.csv', 'r') as test_file: 
        lines = csv.reader(test_file, delimiter = ',')
        next(lines)

        for row in lines: 
            if int(row[0]) == 2: 
                ind = 0
            elif int(row[0]) == 3: 
                ind = 1
            elif int(row[0]) == 5:
                ind = 2
            elif int(row[0]) == 10:
                ind = 3
            else:
                continue
            branch_dicts[ind]['false_positive_rate'].append(float(row[1]))
            # branch_dicts[ind]['max_elements'].append(row[2])
            branch_dicts[ind]['total_storage'].append(float(row[3]))
            branch_dicts[ind]['time'].append(float(row[4]))

    # print(branch_dicts)

    for temp_x in range(len(axis)):
        x_axis = axis[temp_x]
        for temp_y in range(temp_x+1, len(axis)):
            y_axis = axis[temp_y] 
            if x_axis == y_axis:
                break
            elif x_axis == 'total_storage' and y_axis == 'time': 
                # plt.figure(figsize=(20,6))
                fig, ax = plt.subplots(figsize=(20,6))
                for b in range(len(diff_branching)): 
                    current_branchfactor = diff_branching[b]
                    current_dict = branch_dicts[b]
                    
                    ax.scatter(current_dict[x_axis], current_dict[y_axis], c=colors[b], label=str(current_branchfactor))

                    for i, txt in enumerate(current_dict['false_positive_rate']):
                        ax.annotate(txt, (current_dict[x_axis][i], current_dict[y_axis][i]))

                plt.xlabel(x_axis)
                plt.ylabel(y_axis)
                plt.title("{} vs {}".format(x_axis, y_axis))
                plt.legend(loc='upper left')
                plt.tight_layout()
                plt.savefig("test_graphs/{} vs {}".format(x_axis, y_axis))
                print("{} vs {} done".format(x_axis, y_axis))
            else: 
                plt.figure(figsize=(20,6))
                for b in range(len(diff_branching)): 
                    current_branchfactor = diff_branching[b]
                    current_dict = branch_dicts[b]
                    
                    plt.scatter(current_dict[x_axis], current_dict[y_axis], c=colors[b], label=str(current_branchfactor))
                
                plt.xlabel(x_axis)
                plt.ylabel(y_axis)
                # if y_axis == 'time':
                #     plt.gca().invert_yaxis()
                plt.title("{} vs {}".format(x_axis, y_axis))
                plt.legend(loc='upper left')
                plt.tight_layout()
                plt.savefig("test_graphs/{} vs {}".format(x_axis, y_axis))

                print("{} vs {} done".format(x_axis, y_axis))


#{'branching_factor': branch, 'false_positive_rate': pos, 'max_elements': max_elements, 'total storage': size, 'name': p, 'num_nodes_visited': len(nodes), 'nodes_visited': nodes, 'time': end_time-start_time}

in_tree = {'branching_factor':[], 'false_positive_rate':[], 'total storage': [], 'name': [], 'num_nodes_visited': [], 'nodes_visited': [], 'time': []}
out_tree = {'branching_factor':[], 'false_positive_rate':[], 'total storage': [], 'name': [], 'num_nodes_visited': [], 'nodes_visited': [], 'time': []}

def traverse_test():
    with open('traverse.csv', 'r') as traverse_file:
        lines = csv.reader(traverse_file, delimiter=',')
        next(lines)

        for row in lines: 
            branching_factor, false_pr, tot_storage = float(row[0]), float(row[1]), float(row[3])
            current_name, num_nodes_visit = row[4], float(row[5])
            nodes_visit, time = row[6], float(row[7])

            if current_name in test_names: 
                ind = test_names.index(current_name)

                in_tree['branching_factor'].append(branching_factor)
                in_tree['false_positive_rate'].append(false_pr)
                in_tree['name'].append(current_name)
                in_tree['total storage'].append(tot_storage)
                in_tree['num_nodes_visited'].append(num_nodes_visit)
                in_tree['time'].append(time)
                
            else: 
                ind = test_not_name.index(current_name)

                out_tree['branching_factor'].append(branching_factor)
                out_tree['false_positive_rate'].append(false_pr)
                out_tree['name'].append(current_name)
                out_tree['total storage'].append(tot_storage)
                out_tree['num_nodes_visited'].append(num_nodes_visit)
                out_tree['time'].append(time)


    x_axis = 'num_nodes_visited'
    y_axis = 'time'

    for fp in range(len(diff_false_pos)): 
        label_count = [0, 0, 0, 0]
        fig, ax = plt.subplots(figsize=(20,6))
        current_fp = diff_false_pos[fp]
        
        for i in range(len(out_tree['false_positive_rate'])): 
            if out_tree['false_positive_rate'][i] == current_fp:
                current_bf = diff_branching.index(in_tree['branching_factor'][i])
                
                if label_count[current_bf] == 0:
                    label_count[current_bf] += 1
                    ax.scatter(in_tree['num_nodes_visited'][i], in_tree['time'][i], c=colors[current_bf], label=diff_branching[current_bf])
                else:
                    ax.scatter(in_tree['num_nodes_visited'][i], in_tree['time'][i], c=colors[current_bf])
        
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.legend(loc='upper left')
        plt.title("num_nodes visited and time for {}".format(current_fp))
        plt.tight_layout()
        plt.savefig("test_names_in/fpr_{}".format(fp))
        print("fpr {} done".format(current_fp))

    for fp in range(len(diff_false_pos)): 
        label_count = [0, 0, 0, 0]
        fig, ax = plt.subplots(figsize=(20,6))  
        current_fp = diff_false_pos[fp]
        for i in range(len(out_tree['false_positive_rate'])): 
            if out_tree['false_positive_rate'][i] == current_fp:
                current_bf = diff_branching.index(in_tree['branching_factor'][i])
                
                if label_count[current_bf] == 0: 
                    label_count[current_bf] += 1
                    ax.scatter(out_tree['num_nodes_visited'][i], out_tree['time'][i], c=colors[current_bf], label=diff_branching[current_bf])
                else: 
                    ax.scatter(out_tree['num_nodes_visited'][i], out_tree['time'][i], c=colors[current_bf])
        
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.legend(loc='upper left')
        plt.title("num_nodes visited and time for {}".format(current_fp))
        plt.tight_layout()
        plt.savefig("test_names_out/fpr_{}".format(str(fp)))
        print("fpr {} done".format(current_fp))


in_tree = {'branching_factor':[], 'false_positive_rate':[], 'total storage': [], 'name': [], 'num_nodes_visited': [], 'nodes_visited': [], 'time': []}
out_tree = {'branching_factor':[], 'false_positive_rate':[], 'total storage': [], 'name': [], 'num_nodes_visited': [], 'nodes_visited': [], 'time': []}

def trav_test_bar(): #traversal test for bar graph 
    temp = {}
    str_fpr = [str(f) for f in diff_false_pos] 
    for f in str_fpr: 
        if f not in temp:
            temp[f] = []

    info = {}
    not_info = {}
    labels = [str(b) for b in diff_branching] #string of diff branching 
    for b in labels:
        if b not in info:
            info[b] = copy.deepcopy(temp)
        if b not in not_info:
            info[b] = copy.deepcopy(temp)

    with open('traverse.csv', 'r') as traverse_file:
        lines = csv.reader(traverse_file, delimiter=',')
        next(lines)

        for row in lines: 
            branching_factor, false_pr, tot_storage = (row[0]), (row[1]), float(row[3])
            current_name, num_nodes_visit = row[4], float(row[5])
            nodes_visit, time = row[6], float(row[7])

            info[branching_factor][false_pr].append(num_nodes_visit)

            # else: 
            #     not_info[branching_factor][false_pr].append(nodes_visit)

    avg_per_fpr = [ [0 for i in range(len(diff_branching))] for i in range(len(diff_false_pos))]
    for b in labels: 
        dct = info[b] 
        for f in str_fpr: 
            ind_f = str_fpr.index(f)
            ind_b = labels.index(b)
            avg = statistics.mean(dct[f])
            avg_per_fpr[ind_f][ind_b] = avg
        
    print(avg_per_fpr)
    
    #graphing
    x = np.arange(len(labels))
    width = 0.1
    # small_width = small_width

    fig, ax = plt.subplots(figsize=(30,6))
    count = 0
    for block in [-5, -3, -1, 1, 3, 5]: 
        temp = ax.bar(x + block*(width/2), avg_per_fpr[count], width, label=str_fpr[count])
        ax.bar_label(temp, padding=3)        
        count += 1

    ax.set_ylabel('Avg number of nodes visited')
    ax.set_title('Branching factors')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()

    plt.savefig("avg_nodes.png")

def graph6():
    #branching_factor,false_positive_rate,max_elements,total storage,name,num_nodes_visited,nodes_visited,time,leaf_nodes_reached,nodes_per_depth
    branching_factor = []
    fpr = [] #false positive rate 
    storage = []
    name = []
    num_nodes_visited = []
    nodes_visit = []
    time_arr = [] 
    leaf_node = []
    node_per_depth = [] #total per depth 
    with open('traverse.csv', 'r') as traverse_file:
        lines = csv.reader(traverse_file, delimiter=',')
        next(lines)

        for row in lines: 
            branch, false_pos, max_elem, tot_stor = float(row[0]), float(row[1]), float(row[2]), float(row[3])
            num_visit, track_nodes, time = float(row[4]), row[5], float(row[6])
            leaf, node_depth = row[7], row[8]

            branching_factor.append(branch)
            fpr.append(false_pos)
            storage.append(tot_stor)
            num_nodes_visited.append(num_visit)
            nodes_visit.append(len(track_nodes))
            time_arr.append(time)
            leaf_node.append(leaf)
            
            

    
def graph_file2(): #make graphs for []2.csv, 
    arr_branching_factor = []
    arr_fpr = []
    arr_max_elem = []
    arr_total_storage = []
    arr_name = []
    arr_num_nodes_visited = []
    arr_nodes_visit = []
    arr_time = []
    arr_leaf_nodes_reached = []
    arr_nodes_depth = []
    with open('traverse2.csv', 'r') as trav: 
        lines = csv.reader(trav, delimiter=',')
        next(lines)

        for row in lines: 
            #branching_factor,false_positive_rate,max_elements,total storage,name,num_nodes_visited,nodes_visited,time,leaf_nodes_reached,nodes_per_depth
            arr_branching_factor.append(float(row[0]))
            arr_fpr.append(float(row[1]))
            arr_max_elem.append(float(row[2]))
            arr_total_storage.append(float(row[3]))
            arr_name.append((row[4]))
            arr_num_nodes_visited.append(float(row[5]))
            arr_nodes_visit.append(row[6])
            arr_time.append(float(row[7]))
            arr_leaf_nodes_reached.append(row[8])
            arr_nodes_depth.append(row[9])

    narr_branching_factor = []
    narr_fpr = []
    narr_max_elem = []
    narr_total_storage = []
    narr_name = []
    narr_num_nodes_visited = []
    narr_nodes_visit = []
    narr_time = []
    narr_leaf_nodes_reached = []
    narr_nodes_depth = []
    with open('neg_trav2.csv', 'r') as neg: 
        lines = csv.reader(trav, delimiter=',')
        next(lines)

        for row in lines: 
            #branching_factor,false_positive_rate,max_elements,total storage,name,num_nodes_visited,nodes_visited,time,leaf_nodes_reached,nodes_per_depth
            narr_branching_factor.append(float(row[0]))
            narr_fpr.append(float(row[1]))
            narr_max_elem.append(float(row[2]))
            narr_total_storage.append(float(row[3]))
            narr_name.append((row[4]))
            narr_num_nodes_visited.append(float(row[5]))
            narr_nodes_visit.append(row[6])
            narr_time.append(float(row[7]))
            narr_leaf_nodes_reached.append(row[8])
            narr_nodes_depth.append(row[9])

