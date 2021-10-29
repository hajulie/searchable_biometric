import pickle
import secrets

from bloom_filter2 import BloomFilter

from LSH import LSH
from eLSH import eLSH
from bloom import bftree
# from other import try_data


def sample_rand_vector(n):
    vector = [0] * n
    for i in range(n):
        vector[i] = secrets.choice([0, 1])
    return vector


def add_errors(vector, nb_errors):
    # check number of errors is not greater than vector size
    assert (nb_errors <= len(vector))

    modified_vector = [0] * len(vector)
    # copy vector in modified_vector
    for i in range(len(vector)):
        modified_vector[i] = vector[i]

    # randomly flip nb_errors bits
    for j in range(nb_errors):
        i = secrets.choice(range(len(vector)))
        modified_vector[i] = 1 - vector[i]
    return modified_vector


def compareELSH(s, l, hx, hy):
    for i in range(l):
        matches = 0
        for j in range(s):
            if hx[i][j] == hy[i][j]:
                matches += 1
            else:
                matches = 0
                break
        if matches == s:
            return True, i
    return False, -1


def compareBF(bf, query_elsh):
    match = False
    for h in query_elsh:
        if pickle.dumps(h) in bf:
            match = True
            break
    return match


def test_lsh(n, r, c):
    print('LSH test ...')

    x = [0] * n
    x[245] = 1
    x[721] = 1

    lsh_245 = LSH(n, r, c, 245)
    lsh_246 = LSH(n, r, c, 246)
    lsh_721 = LSH(n, r, c, 721)

    assert(lsh_245.hash(x) == (245, 1))
    assert(lsh_246.hash(x) == (246, 0))
    assert(lsh_721.hash(x) == (721, 1))

    print("p1 = " + str(lsh_245.getTAR()))
    print("p2 = " + str(lsh_245.getFAR()))

    # test LSH serialization
    pickled_lsh = LSH.deserialize(lsh_245.serialize())
    assert (pickled_lsh.hash(x) == (245, 1))

    print('SUCCESS')


def test_elsh(n, r, c, s, l):
    print('eLSH test ...')

    x = sample_rand_vector(n)
    x_50 = add_errors(x, 50)
    x_307 = add_errors(x, 307)
    x_600 = add_errors(x, 600)

    elsh = eLSH(LSH, n, r, c, s, l)
    hx = elsh.hash(x)
    print("test jh:", (hx[0]))
    hx_50 = elsh.hash(x_50)
    hx_307 = elsh.hash(x_307)
    hx_600 = elsh.hash(x_600)

    # compare elsh for 50 errors (should "match" ...)
    match = False
    (match, i) = compareELSH(s, l, hx, hx_50)
    assert (match)
    assert (hx[i] == hx_50[i])

    # compare elsh for 307 errors (should "match" ...)
    (match, i) = compareELSH(s, l, hx, hx_307)
    assert (match)

    # compare elsh for 600 errors (should not "match" most of the time...)
    (match, i) = compareELSH(s, l, hx, hx_600)
    assert (not match)

    print("p1' = " + str(elsh.getTAR()))
    print("p2' = " + str(elsh.getFAR()))

    # test eLSH serialization
    pickled_elsh = eLSH.deserialize(elsh.serialize())
    h1 = pickled_elsh.hash(x)
    assert (h1 == hx)

    print('SUCCESS')


def test_bf(n, r, c, s, l):
    print("Test Bloom filters ...")
    elsh = eLSH(LSH, n, r, c, s, l)
    bf0 = BloomFilter(8, 0.01)

    try_data_hashes = list()
    for record in try_data:
        hash = elsh.hash(record)
        try_data_hashes.append(hash)
        for h in hash:
            bf0.add(pickle.dumps(h))

    print("Test with no errors ...")
    hash4 = elsh.hash(try_data[4])
    match = compareBF(bf0, hash4)
    assert match

    print("Test with 307 errors ...")
    hash4_307 = elsh.hash(add_errors(try_data[4], 307))
    match = compareBF(bf0, hash4_307)
    assert match

    print("Test with too many errors ...")
    hash4_fail = elsh.hash(add_errors(try_data[4], 800))
    # check if elsh comparison is correct
    matches = list()
    for j in range(len(try_data_hashes)):
        (match, i) = compareELSH(s, l, try_data_hashes[j], hash4_fail)
        if match:
            matches.append(j)
    print("Matches = " + str(matches))
    assert (len(matches) == 0)
    print("No matches using elsh values ...")
    # check if BF is correct
    match = compareBF(bf0, hash4_fail)
    assert not match
    print("No matches using BF (SUCCESS)")




def test_bftree(n, r, c, s, l):
    t = bftree(2, 0.01, 8)
    try_data.append([0]*n)
    t.build_index(try_data)
    t.tree.show()

    attempt = add_errors(try_data[4], 1000)
    print(t.search([attempt]))


if __name__ == '__main__':
    n = 1024
    r = 307
    c = 0.5 * n / r
    s = 15
    l = 2000

    test_lsh(n, r, c)
    test_elsh(n, r, c, s, l)
    # test_bf(n, r, c, s, l)
    # test_bftree(n, r, c, s, l)
