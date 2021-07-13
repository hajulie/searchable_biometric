from LSH import LSH
from eLSH import eLSH
from math import isclose


def compareELSH(s, hx, hy):
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

    print('SUCCESS')

def test_elsh(n, r, c, s, l):
    print('eLSH test ...')

    x = [0] * n
    x[245] = 1
    x[721] = 1

    y = [0] * n
    y[245] = 1
    y[721] = 1
    y[1000] = 1

    z = [1] * n

    elsh = eLSH(LSH, n, r, c, s, l)
    hx = elsh.hash(x)
    hy = elsh.hash(y)
    hz = elsh.hash(z)

    # compare elsh for x and y (should "match" ...)
    match = False
    (match, i) = compareELSH(s, hx, hy)
    assert(match)
    assert(hx[i] == hy[i])

    # compare elsh for x and z (should not "match" ...)
    (match, i) = compareELSH(s, hx, hz)
    assert(not match)

    print("p1' = " + str(elsh.getTAR()))
    print("p2' = " + str(elsh.getFAR()))

    print('SUCCESS')


if __name__ == '__main__':
    n = 1024
    r = 307
    c = 0.5 * n / r
    s = 12
    l = 1000

    test_lsh(n, r, c)
    test_elsh(n, r, c, s, l)

