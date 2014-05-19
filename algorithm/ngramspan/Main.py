''' 
Usage: python Main.py

Input parameters:
epsilon, n_max, l_max, dataset

'''

import sys
import getopt
from lib.NGramSet import *


def Usage():
    print 
    print " Usage: python Main.py [arguments]" 
    print "        where [arguments]... is a list of zero or more optional arguments"
    print
    print " Arguments:"
    print "   -n, --nmax        Set n_max (default 5)"
    print "   -l, --lmax        Set l_max (default 20)"
    print "   -d, --dataset     Set dataset (default data/msnbc)"
    print "   -s, --minsup      Set min_sup (default 10,000)"
    print


if __name__ == "__main__":
    '''
    If min_sup = 10000, then n_max = 32, l_max = 14795

    n_max = 32, because sequence lengths between 33-14795 sum is 9813 < 10000

    '''
    # Input parameters
    n_max = 5
    l_max = 20
    dataset = "data/msnbc"
    min_sup = 10000

    try:
        opts, args = getopt.getopt( sys.argv[1:], 'n:l:d:s:h', ['nmax=', 'lmax=', 'dataset=', 'minsup=', 'help'])

        for opt, value in opts:
            if opt in ("-n", "--nmax"):
                n_max = int(value)
            elif opt in ("-l", "--lmax"):
                l_max = int(value)
            elif opt in ("-d", "--dataset"):
                dataset = "data/" + value
            elif opt in ("-s", "--minsup"):
                min_sup = int(value)
            elif opt in ("-h", "--help"):
                Usage()
                sys.exit(1)

    except getopt.GetoptError:
        # print "\n getopt Error!\n"
        Usage()
        sys.exit(1)

    print "\n*** Dataset: ", dataset 
    print "*** n_max: ", n_max
    print "*** l_max: ", l_max
    print "*** min_sup: ", min_sup

    print "\n=== Phase: Decomposing input dataset to n-grams (%d <= n <= %d)\n" % (1,n_max)
    ngram_set = NGramSet(l_max, n_max, min_sup)
    ngram_set.load_dataset(dataset + ".dat", dataset + "-original-" + str(n_max) + "grams.dat")
