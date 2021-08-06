import secrets
import pickle

# Bit sampling LSH for the Hamming distance
class LSH:

    def __init__(self, n, r, c, i):
        self.i = i
        self.n = n
        self.r = r
        self.c = c

    def hash(self, x):
        # print(self.i, print(x))
        return self.i, x[self.i]

    def getTAR(self):
        return 1 - (self.r / self.n)

    def getFAR(self):
        return 1 - (self.c * self.r / self.n)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(pickled_lsh):
        return pickle.loads(pickled_lsh)

    @staticmethod
    def sampleRandomLSH(n, r, c):
        i = secrets.choice(list(range(n)))
        return LSH(n, r, c, i)

