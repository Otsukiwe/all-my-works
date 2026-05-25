import time
import csv
import statistics
from algorithms import *
from data_gen import *

REPEATS = 7

def measure(func, *args):
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

def run_benchmarks():
    results = {}

    results['constant'] = [(n, measure(constant_access, random_array(n))) for n in SIZES]
    results['binary_search'] = [(n, measure(binary_search, sorted_array(n), n // 2)) for n in SIZES]
    results['linear_search'] = [(n, measure(linear_search, random_array(n), -1)) for n in SIZES]
    results['array_sum'] = [(n, measure(array_sum, random_array(n))) for n in SIZES]

    results['merge_sort_random'] = [(n, measure(merge_sort, random_array(n))) for n in SIZES]
    results['merge_sort_sorted'] = [(n, measure(merge_sort, sorted_array(n))) for n in SIZES]
    results['merge_sort_reverse'] = [(n, measure(merge_sort, reverse_array(n))) for n in SIZES]

    from data_gen import BUBBLE_SIZES
    sizes_bubble = BUBBLE_SIZES
    results['bubble_sort_random'] = [(n, measure(bubble_sort, random_array(n))) for n in sizes_bubble]
    results['bubble_sort_sorted'] = [(n, measure(bubble_sort, sorted_array(n))) for n in sizes_bubble]
    results['bubble_sort_reverse'] = [(n, measure(bubble_sort, reverse_array(n))) for n in sizes_bubble]

    results['matrix_multiply'] = [(n, measure(matrix_multiply, random_matrix(n), random_matrix(n))) for n in MATRIX_SIZES]

    results['fib'] = [(n, measure(fib_recursive, n)) for n in FIB_SIZES]

    with open('results.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['algorithm', 'n', 'time'])
        for algo, data in results.items():
            for n, t in data:
                w.writerow([algo, n, t])

    return results
