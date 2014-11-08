import os, sys
import multiprocessing
from multiprocessing.pool import ThreadPool

import requests


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def download_picture(ptuple):
    url, filename = ptuple
    if not os.path.isfile(filename):
        print "Downloading", filename
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        r = requests.get(url)
        if r.ok:
            with file(filename, 'w') as outfile:
                outfile.write(r.content)

def download_pictures(paramlist, chunksize=20, processes=5):
    grouped = chunks(paramlist, chunksize)
    pool = ThreadPool(processes=processes)
    count = 0
    total = len(paramlist) / chunksize
    if len(paramlist) % chunksize:
        total += 1
    for group in grouped:
        output = pool.map(download_picture, group)
        count += 1
        print "Group %d of %d processed." % (count, total)
        

