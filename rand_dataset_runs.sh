# ND dataset
python3 dataset_test.py --dataset=nd --oram_constant_accesses=37 --nb_trees=850 --lsh_size=18 --same_t=.3 --oram=1 > nd356.txt

## random dataset
python3 dataset_test.py --oram_constant_accesses=13 --nb_trees=630 --lsh_size=15 --dataset_size=356 --same_t=.3 --oram=1 > rand356.txt
python3 dataset_test.py --oram_constant_accesses=8 --nb_trees=850 --lsh_size=18 --dataset_size=1000 --nb_queries=500 --same_t=.3 --oram=1 > rand1000.txt
python3 dataset_test.py --parallel=0 --oram_constant_accesses=11 --nb_trees=1000 --lsh_size=19 --dataset_size=2500 --nb_queries=500 --same_t=.3 --oram=1 > rand2500.txt
python3 dataset_test.py --parallel=0 --oram_constant_accesses=12 --nb_trees=1200 --lsh_size=20 --dataset_size=5000 --nb_queries=500 --same_t=.3 --oram=1 > rand5000.txt
#python3 dataset_test.py --parallel=0 --oram_constant_accesses=30 --nb_trees=189875 --lsh_size=31 --dataset_size=10000 --same_t=.3 --oram=1 > rand10000.txt

# synthetic dataset
python3 dataset_test.py --dataset=synth --oram_constant_accesses=26 --nb_trees=850 --lsh_size=18 --same_t=.3 --oram=1 > synth356.txt
python3 dataset_test.py --dataset=synth --oram_constant_accesses=47 --nb_trees=1000 --lsh_size=19 --dataset_size=1000 --nb_queries=500 --same_t=.3 --oram=1 > synth1000.txt
python3 dataset_test.py --parallel=0 --dataset=synth --oram_constant_accesses=56 --nb_trees=1200 --lsh_size=21 --dataset_size=2500 --nb_queries=100 --same_t=.3 --oram=1 > synth2500.txt
python3 dataset_test.py --parallel=0 --dataset=synth --oram_constant_accesses=72 --nb_trees=1300 --lsh_size=22 --dataset_size=5000 --nb_queries=10 --same_t=.3 --oram=1 > synth5000.txt
#python3 dataset_test.py --parallel=0 --dataset=synth --oram_constant_accesses=30 --nb_trees=189875 --lsh_size=31 --dataset_size=10000 --same_t=.3 --oram=1 > synth10000.txt

