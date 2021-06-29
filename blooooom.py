from bloom_filter import BloomFilter

data = ['John', 'Jane', 'Smith', 'Doe']

branching_factor = 2

bfilter = BloomFilter(max_elements=4, error_rate=0.01)

#level 3 
level3 = [] 
for i in data: 
    bfilter = BloomFilter(max_elements=4, error_rate=0.01)
    bfilter.add(i)
    level3.append(bfilter)

level2 = [] 
for i in range(0,len(data),2):
    bfilter = BloomFilter(max_elements=4, error_rate=0.01)
    bfilter.add(data[i]), bfilter.add(data[i+1])
    level2.append(bfilter)

level1 = BloomFilter(max_elements=4, error_rate=0.01)
for i in data: 
    level1.add(i)

print(level1, level2, level3)

print('John' in level1)
print('Jen' in level1)