import numpy as np

np.random.seed(42)

SIZES = [100, 15000, 50000, 100000]
BUBBLE_SIZES = [100, 300, 500, 800, 1200, 2000]
MATRIX_SIZES = [5, 10, 20, 40, 60, 80, 100]
FIB_SIZES = list(range(5, 31))

def random_array(n):
    return list(np.random.randint(0, n * 10, n))

def sorted_array(n):
    return list(range(n))

def reverse_array(n):
    return list(range(n, 0, -1))

def random_matrix(n):
    return [[int(x) for x in row] for row in np.random.randint(0, 10, (n, n))]
