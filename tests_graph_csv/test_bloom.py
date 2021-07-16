import csv, bloom, test_data, time
from test_data import mock_data

diff_branching = [2, 3, 5, 10]
diff_false_pos = [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
max_elements = len(mock_data)
search_in_data = test_data.test_names
search_not_data = test_data.test_not_name


with open('tests2.csv', mode='w') as csv_file, open('traverse2.csv', mode='w') as trav_file, open('neg_trav2.csv', mode='w') as not_file: 
    #{'branching_factor', 'false_positive_rate', 'max_elements', 'total storage', 'time'}
    field_names = ['branching_factor', 'false_positive_rate', 'max_elements', 'total storage', 'time']
    initial_test = csv.DictWriter(csv_file, fieldnames=field_names)
    initial_test.writeheader()

    #{'branching_factor', 'false_positive_rate', 'max_elements', 'total storage', 'name', 'num_nodes_visited', 'nodes_visited'}
    traverse_field_names = ['branching_factor', 'false_positive_rate', 'max_elements', 'total storage', 'name', 'num_nodes_visited', 'nodes_visited', 'time', 'leaf_nodes_reached', 'nodes_per_depth']
    traverse_file = csv.DictWriter(trav_file, fieldnames=traverse_field_names)
    traverse_file.writeheader()

    neg_file = csv.DictWriter(not_file, fieldnames=traverse_field_names)
    neg_file.writeheader()

    for branch in diff_branching: 
        for pos in diff_false_pos: 
            t = bloom.bftree(branch, pos, max_elements)
            
            start_time = time.time()
            t.build_index(mock_data)
            end_time = time.time()
            
            size = bloom.find_size(t)
            initial_test.writerow({'branching_factor': branch, 'false_positive_rate': pos, 'max_elements': max_elements, 'total storage': size, 'time': end_time-start_time})

            for p in search_in_data: 
                start_time = time.time()
                nodes_visited, leaf_nodes, access_depth = t.search(p)
                end_time = time.time()

                traverse_file.writerow({'branching_factor': branch, 'false_positive_rate': pos, 'max_elements': max_elements, 'total storage': size, 'name': p, 'num_nodes_visited': len(nodes_visited), 'nodes_visited': nodes_visited, 'time': end_time-start_time, 'leaf_nodes_reached': leaf_nodes, 'nodes_per_depth': access_depth})

            for p in search_not_data:
                nodes_visited, leaf_nodes, access_depth = t.search(p)
                neg_file.writerow({'branching_factor': branch, 'false_positive_rate': pos, 'max_elements': max_elements, 'total storage': size, 'name': p, 'num_nodes_visited': len(nodes_visited), 'nodes_visited': nodes_visited, 'time': end_time-start_time, 'leaf_nodes_reached': leaf_nodes, 'nodes_per_depth': access_depth})

            print("branch {}, fpr {}".format(branch, pos))

