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

    @staticmethod
    def sortLSH(hash):
        hash.sort(key=lambda x: x[0])

    @staticmethod
    def compareLSHstring(hash1, hash2):
        return str(hash1) <= str(hash2)

    @staticmethod
    def dummyLSH(hash1):
        for p1, b1 in hash1:
            return b1 == 2

    @staticmethod
    def compareLSH(hash1, hash2):
        bits_match = 0
        for p1, b1 in hash1:
            for p2, b2 in hash2:
                if p1 == p2 and b1 != b2:
                    return False
                elif p1 == p2 and b1 == b2:
                    bits_match = bits_match + 1
                    break

        if bits_match == len(hash1):
            return True
        else:
            return False
