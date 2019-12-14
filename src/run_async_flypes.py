#! /usr/bin/python2.7

import multiprocessing as mp
import os


def runAsyncFlypes(crNum, ordering):
    os.system("./main.py {} {} {}".format(crNum, ordering, mp.current_process()._identity[0]))


pool = mp.Pool(processes=mp.cpu_count())

for i in range(19536):
    pool.apply_async(runAsyncFlypes, args=(14, i + 1))

pool.close()
pool.join()
