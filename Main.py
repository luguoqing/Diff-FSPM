#! /usr/bin/env python
# encoding: utf-8

''' 
Created on Apr 24, 2014

@summary: Diff-FSPM Algorithm
    - Usage: python Main.py
    - Input parameters: epsilon, l_opt, dataset

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn> 

'''

import sys
sys.path.append( 'conf' )
sys.path.append( 'lib' )

import Sanitizer
from Reconstruction import *
from NGramSet import *
from GetOptLength import * 
from base.dp_log import dplog

import dp_conf

def init():
    '''
    @summary: Initialization
    
    '''
    dplog.init_logger( dp_conf.LOG_FILE )


def Diff_FSPM():
    '''
    @summary: Diff-FSPM algorithm

    '''
    dplog.debug("original sequence database : (%s)"%(dp_conf.dataset))
    dplog.debug("differential privacy budget : (%s)"%(dp_conf.epsilon))
    dplog.debug("minmum support value : (%s)"%(dp_conf.min_sup))
    
    dplog.info( " === Phase 1: Decomposing input sequence dataset to n-grams (%d<=n<=%d) Begin ===" % (1, dp_conf.l_opt) )
    
    dp_conf.l_opt = GetOptSeqLength(dp_conf.dataset, dp_conf.epsilon, mechanism="Exponential")
    ngram_set = NGramSet( int(dp_conf.l_opt), N_max=int(dp_conf.l_opt) )
    # ngram_set.load_dataset( dp_conf.dataset, dp_conf.dataset_truncate % (dp_conf.l_opt) )
    ngram_set.load_dataset( dp_conf.dataset, dp_conf.dataset_ngrams % (dp_conf.l_opt) )
    
    dplog.info( " === Phase 1: Decomposing input sequence dataset to n-grams (%d<=n<=%d) End ===" % (1, dp_conf.l_opt) )



def main():
    '''
    @summary: main entry

    '''
    
    init()
    
    logstr = "+"*8 + "    Start Diff-FSPM Algorithm    " + "+"*8
    dplog.info("")
    dplog.info("+" * len(logstr))
    dplog.info(logstr)
    dplog.info("+" * len(logstr))
    dplog.info("")

    Diff_FSPM()

    logstr = "+"*8 + "     End Diff-FSPM Algorithm     " + "+"*8
    dplog.info("")
    dplog.info("+" * len(logstr))
    dplog.success(logstr)
    dplog.info("+" * len(logstr))
    dplog.info("")


if __name__ == "__main__":
    
    main()
    
    '''
    file_id = "-noisy-n_max_" + str(n_max) + "-l_max_" + str(l_max) + "-eps_" + str(epsilon)

    print "\n=== Phase 1: Decomposing input dataset to n-grams (%d <= n <= %d)\n" % (1,n_max)
    ngram_set = NGramSet(int(l_max), n_max)
    ngram_set.load_dataset(dataset + ".dat", dataset + "-original-" + str(n_max) + "grams.dat")

    print "\n=== Phase 2: Sanitizing n-grams\n"
    ngram_set = Sanitizer.ngram(ngram_set, n_max, budget=epsilon, sensitivity=l_max) 
    ngram_set.dump(dataset + file_id + ".dat")

    #print "\n=== Phase 3: Synthetic sequential database generation from sanitized n-grams\n"
    factory = Reconstruction(ngram_set, l_max) 
    factory.extend()
    factory.ngramset.dump(dataset + file_id + "-extended.dat")

    # Generating dataset
    # factory.reconstruct(dataset + file_id + "-reconstructed.dat")
    '''
