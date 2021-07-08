import csv, bloom, time, random, names, string

f = open('names6.txt', 'r')
mock_data = [line.rstrip('\n') for line in f]
f.close()

mock_data = mock_data[:10**4]
diff_branching = [2, 3, 5, 10]
diff_false_pos = [0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
max_elements = len(mock_data)
search_in_data = [mock_data[random.randrange(0,10**4)] for i in range(1000)]
print("search in data list made")

letters = string.ascii_lowercase
search_not_data = [] 
for i in range(1000):
    temp_name = ''.join(random.choice(letters) for i in range(10))
    while temp_name in mock_data or temp_name in search_not_data: 
        temp_name = names.get_first_name()
    search_not_data.append(temp_name)
print("search not data list made")


with open('tests6.csv', mode='w') as csv_file, open('traverse6.csv', mode='w') as trav_file: 
    field_names = ['branching_factor', 'false_positive_rate', 'max_elements', 'total storage', 'time']
    initial_test = csv.DictWriter(csv_file, fieldnames=field_names)
    initial_test.writeheader()

    traverse_field_names = ['branching_factor', 'false_positive_rate', 'max_elements', 'total storage', 'name', 'num_nodes_visited', 'nodes_visited', 'time', 'leaf_nodes_reached', 'nodes_per_depth']
    traverse_file = csv.DictWriter(trav_file, fieldnames=traverse_field_names)
    traverse_file.writeheader()

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
                start_time = time.time()
                nodes_visited, leaf_nodes, access_depth = t.search(p)
                end_time = time.time()
                traverse_file.writerow({'branching_factor': branch, 'false_positive_rate': pos, 'max_elements': max_elements, 'total storage': size, 'name': p, 'num_nodes_visited': len(nodes_visited), 'nodes_visited': nodes_visited, 'time': end_time-start_time, 'leaf_nodes_reached': leaf_nodes, 'nodes_per_depth': access_depth})

            print("branch {}, fpr {}".format(branch, pos))

