#! /usr/bin/env python
# encoding: utf-8

''' 
Created on Apr 24, 2014

@summary: Diff-FSPM Algorithm
    - Usage: python Main.py
    - Input parameters: epsilon, l_opt, dataset, min_sup

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
import dp_conf as conf


def init():
    '''
    @summary: Initialization
    
    '''
    dplog.init_logger( conf.LOG_FILE )


def Diff_FSPM():
    '''
    Diff-FSPM 算法分为如下3个步骤：
        - 原始序列数据集局部转换
            - 获取最优序列长度 l_opt            ok
            - 截断原始序列数据集                ok
        - 层次遍历构建绕动闭前缀序列树
            - min_sup 约束剪枝
            - 闭等价关系 剪枝
            - 预测计数值 PK. 噪音计数值
        - 描述上是挖掘FSP树, 实际直接输出结果集
            
    @summary: Diff-FSPM algorithm
    '''
    dplog.info( " === Phase 1: Decomposing input sequence dataset to n-grams (%d<=n<=%d) Begin ===" % (1, conf.l_opt) )
    conf.l_opt = GetOptSeqLength(conf.dataset, conf.epsilon, mechanism="Exponential")
    ngram_set = NGramSet( int(conf.l_opt), N_max=int(conf.n_max) )
    ngram_set.load_dataset( conf.dataset, conf.dataset_ngrams % (conf.l_opt) )
    dplog.info( " === Phase 1: Decomposing input sequence dataset to n-grams (%d<=n<=%d) End ===" % (1, conf.l_opt) )

    dplog.info( " === Phase 2: Sanitizing n-grams to build noisy frequent sequential patterns Tree Begin ===" )
    ngram_set = Sanitizer.ngram( ngram_set, conf.n_max, conf.epsilon, conf.l_opt, conf.min_sup)
    ngram_set.dump( conf.dataset_noisy % (conf.l_opt, conf.epsilon))
    dplog.info( " === Phase 2: Sanitizing n-grams to build noisy frequent sequential patterns Tree End ===" )
    
    dplog.info( " === Phase 3: Synthetic frequent sequential patterns from santized n-grams Begin ===" )
    factory = Reconstruction( ngram_set, conf.min_sup )
    factory.extend()
    factory.ngramset.dump( conf.dataset_result % (conf.l_opt, conf.epsilon))
    dplog.info( " === Phase 3: Synthetic frequent sequential patterns from santized n-grams End ===" )


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

    dplog.debug("original sequence database : (%s)"%(conf.dataset))
    dplog.debug("differential privacy budget : (%s)"%(conf.epsilon))
    dplog.debug("minmum support value : (%s)"%(conf.min_sup))
    
    Diff_FSPM()

    logstr = "+"*8 + "     End Diff-FSPM Algorithm     " + "+"*8
    dplog.info("")
    dplog.info("+" * len(logstr))
    dplog.success(logstr)
    dplog.info("+" * len(logstr))
    dplog.info("")

    
if __name__ == "__main__":
    
    main()
