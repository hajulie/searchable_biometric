import pickle

# Extended LSH implementation based on bit sampling LSH for Hamming distance.
class eLSH:

    def __init__(self, lsh, n, r, c, s, l):
        self.lsh = lsh
        self.n = n
        self.r = r
        self.c = c
        self.s = s
        self.l = l
        self.hashes = [None] * self.l

        # randomly sample hashes
        for i in range(self.l):
            self.hashes[i] = [0] * self.s
            for j in range(self.s):
                self.hashes[i][j] = self.lsh.sampleRandomLSH(n, r, c)

    def hash(self, x):
        res = []
        for i in range(self.l):
            gi = [0] * self.s
            for j in range(self.s):
                gi[j] = self.hashes[i][j].hash(x)
            res.append(gi)

        return res

    def getTAR(self):
        return 1 - pow(1 - pow(1 - (self.r / self.n), self.s), self.l)

    def getFAR(self):
        return 1 - pow(1 - pow(1 - (self.c * self.r / self.n), self.s), self.l)

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(pickled_elsh):
        return pickle.loads(pickled_elsh)
