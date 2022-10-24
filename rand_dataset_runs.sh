python3 dataset_test.py --oram_constant_accesses=30 --nb_trees=630 --lsh_size=15 --dataset_size=500 --same_t=.3 --oram=1 > rand500.txt
python3 dataset_test.py --oram_constant_accesses=30 --nb_trees=1290 --lsh_size=17 --dataset_size=1000 --same_t=.3 --oram=1 > rand1000.txt
python3 dataset_test.py --oram_constant_accesses=30 --nb_trees=7665 --lsh_size=22 --dataset_size=1000 --same_t=.3 --oram=1 > rand5000.txt
python3 dataset_test.py --oram_constant_accesses=30 --nb_trees=22340 --lsh_size=24 --dataset_size=10000 --same_t=.3 --oram=1 > rand10000.txt
python3 dataset_test.py --oram_constant_accesses=30 --nb_trees=189875 --lsh_size=31 --dataset_size=100000 --same_t=.3 --oram=1 > rand100000.txt
