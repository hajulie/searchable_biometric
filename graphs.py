import matplotlib.pyplot as plt
import csv

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

    for row in lines: 
        if row[0] == 'branching_factor':
            continue
        
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

print(branch_dicts)

for temp_x in range(len(axis)):
    x_axis = axis[temp_x]
    for temp_y in range(temp_x+1, len(axis)):
        y_axis = axis[temp_y] 
        if x_axis == y_axis:
            break
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