def constant_access(arr, index=0):
    """Time: O(1), Space: O(1)"""
    return arr[index]

def binary_search(arr, target):
    """Time: O(log n), Space: O(1)"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def linear_search(arr, target):
    """Time: O(n), Space: O(1)"""
    for i, v in enumerate(arr):
        if v == target:
            return i
    return -1

def array_sum(arr):
    """Time: O(n), Space: O(1)"""
    s = 0
    for v in arr:
        s += v
    return s

def merge_sort(arr):
    """Time: O(n log n), Space: O(n)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def bubble_sort(arr):
    """Time: O(n^2), Space: O(1)"""
    a = arr[:]
    n = len(a)
    for i in range(n):
        for j in range(0, n - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
    return a

def insertion_sort(arr):
    """Time: O(n^2), Space: O(1)"""
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a

def matrix_multiply(A, B):
    """Time: O(n^3), Space: O(n^2)"""
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C

def fib_recursive(n):
    """Time: O(2^n), Space: O(n)"""
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)
