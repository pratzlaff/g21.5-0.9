import pprint;
from glob import glob;
from braceexpand import braceexpand

def braced_glob(path):
    l = []
    for x in braceexpand(path):
        l.extend(glob(x))

    return l

pprint.pprint(braced_glob("/data/legs/rpete/flight/g21.5-0.9/srcflux/i_qe_N0013{,.20210701a}/*.flux"))

