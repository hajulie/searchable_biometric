import matplotlib.pyplot as plt
import csv
from test_data import *

colors = ['g', 'b', 'r', 'c']
diff_branching = [2, 3, 5, 10]
diff_false_pos = [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
axis = ['false_positive_rate', 'total_storage', 'time']

branch_dicts = [{'false_positive_rate': [], 'total_storage': [], 'time': []}, \
    {'false_positive_rate': [], 'total_storage': [], 'time': []}, \
        {'false_positive_rate': [], 'total_storage': [], 'time': []}, \
            {'false_positive_rate': [], 'total_storage': [], 'time': []}] #[branch fact 2, 3, 5, 10]

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

in_tree = [{'branching_factor':[] , 'false_positive_rate':[], 'total storage': [], 'name': [], 'num_nodes_visited': [], 'nodes_visited': [], 'time': []} for i in range(50)]
out_tree = [{'branching_factor':[], 'false_positive_rate':[], 'total storage': [], 'name': [], 'num_nodes_visited': [], 'nodes_visited': [], 'time': []} for i in range(50)]



with open('traverse.csv', 'r') as traverse_file:
    lines = csv.reader(traverse_file, delimiter=',')
    next(lines)

    for row in lines: 
        branching_factor, false_pr, tot_storage = float(row[0]), float(row[1]), float(row[3])
        current_name, num_nodes_visit = row[4], float(row[5])
        nodes_visit, time = row[6], float(row[7])

        if current_name in test_names: 
            ind = test_names.index(current_name)

            in_tree[ind]['branching_factor'].append(branching_factor)
            in_tree[ind]['false_positive_rate'].append(false_pr)
            in_tree[ind]['name'].append(current_name)
            in_tree[ind]['total storage'].append(tot_storage)
            in_tree[ind]['num_nodes_visited'].append(num_nodes_visit)
            in_tree[ind]['time'].append(time)
            
        else: 
            ind = test_not_name.index(current_name)

            out_tree[ind]['branching_factor'].append(branching_factor)
            out_tree[ind]['false_positive_rate'].append(false_pr)
            out_tree[ind]['name'].append(current_name)
            out_tree[ind]['total storage'].append(tot_storage)
            out_tree[ind]['num_nodes_visited'].append(num_nodes_visit)
            out_tree[ind]['time'].append(time)

ya = ['num_nodes_visited']
xa = ['time']

# print(in_tree, out_tree)

def list_colors(lst):
    cols = [] 
    for i in lst: 
        j = diff_branching.index(i)
        cols.append(colors[j])
    return cols

for temp_x in range(len(xa)): 
    x_axis = xa[temp_x]
    for temp_y in range(len(ya)):
        y_axis = ya[temp_y]

        for n in range(len(test_names)): 
            current_name = test_names[n]
            current_dict = in_tree[n]
            cs = list_colors(current_dict['branching_factor'])

            fig, ax = plt.subplots(figsize=(20,6))
            ax.scatter(current_dict[x_axis], current_dict[y_axis], c=cs)

            for i, txt in enumerate(current_dict['false_positive_rate']): 
                ax.annotate(txt, (current_dict[x_axis][i], current_dict[y_axis][i]))

            plt.xlabel(x_axis), plt.ylabel(y_axis)
            plt.title("in_{}".format(current_name))
            plt.legend(colors, diff_branching, loc='upper left')
            plt.tight_layout()
            plt.savefig("test_names_in/in_{}".format(current_name))
            print("in {}".format(current_name))

for temp_x in range(len(xa)): 
    x_axis = xa[temp_x]
    for temp_y in range(len(ya)):
        y_axis = ya[temp_y]

        for b in range(len(test_not_name)): 
            current_name = test_not_name[b]
            current_dict = out_tree[b]
            cs = list_colors(current_dict['branching_factor'])

            fig, ax = plt.subplots(figsize=(20,6))
            ax.scatter(current_dict[x_axis], current_dict[y_axis], c=cs)

            for i, txt in enumerate(current_dict['false_positive_rate']): 
                ax.annotate(txt, (current_dict[x_axis][i], current_dict[y_axis][i]))

            plt.xlabel(x_axis), plt.ylabel(y_axis)
            plt.title("{}".format(current_name))
            plt.legend(colors, diff_branching, loc='upper left')
            plt.tight_layout()
            plt.savefig("test_names_out/{}".format(current_name))
            print("out {}".format(current_name))