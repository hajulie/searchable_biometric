import secrets

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

    def sampleRandomLSH(n, r, c):
        i = secrets.choice(list(range(n - 1)))
        return LSH(n, r, c, i)
