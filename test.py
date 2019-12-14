#! /usr/bin/python2.7

import multiprocessing as mp
import numpy as np
from time import time

# prepare data
np.random.RandomState(100)
arr = np.random.randint(0, 10, size=[4000000, 5])
data = arr.tolist()


def howmany_within_range(row, minimum, maximum):
    """Returns how many numbers lie within `maximum` and `minimum` in a given `row`"""
    count = 0
    for n in row:
        if minimum <= n <= maximum:
            count = count + 1
    return count


start = time()

results = []
for row in data:
    results.append(howmany_within_range(row, minimum=4, maximum=8))

end = time()

# just print the last 10 (there's actually 200000)
print(results[:10])
print(end - start)

""" This is slower than the normal approach """
# # init a pool
# # this will take care of parallelizing stuff
# pool = mp.Pool(mp.cpu_count())
#
# start = time()
#
# # this takes forever...
# # apply the function to the inputs (row, 4, 8) just like above but this time in parallel
# results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for row in data]
#
# end = time()
#
# # always close your stuff
# pool.close()
#
# print(results[:10])
# print(end - start)

""" This is also slower than the normal approach """
# # redefine, with only 1 mandatory argument.
# def howmany_within_range_rowonly(row, minimum=4, maximum=8):
#     count = 0
#     for n in row:
#         if minimum <= n <= maximum:
#             count = count + 1
#     return count
#
#
# pool = mp.Pool(mp.cpu_count())
#
# start = time()
#
# # map only uses iterables
# results = pool.map(howmany_within_range_rowonly, [row for row in data])
#
# end = time()
#
# pool.close()
#
# print(results[:10])
# print(end - start)

pool = mp.Pool(mp.cpu_count())

results = []


# Step 1: Redefine, to accept `i`, the iteration number
def howmany_within_range2(i, row, minimum, maximum):
    """Returns how many numbers lie within `maximum` and `minimum` in a given `row`"""
    count = 0
    for n in row:
        if minimum <= n <= maximum:
            count = count + 1
    return i, count


# Step 2: Define callback function to collect the output in `results`
def collect_result(result):
    global results
    results.append(result)


start = time()

# Step 3: Use loop to parallelize
for i, row in enumerate(data):
    pool.apply_async(howmany_within_range2, args=(i, row, 4, 8), callback=collect_result)

# Step 4: Close Pool and let all the processes complete
pool.close()
pool.join()  # postpones the execution of next line of code until all processes in the queue are done.

end = time()

print(end - start)

# Step 5: Sort results [OPTIONAL]
results.sort(key=lambda x: x[0])
results_final = [r for i, r in results]

print(results_final[:10])
