#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
@summary: Experimental Evaluation
    - transform 'min_sup FSPM' to 'top_k FSPM'
    - use evaluation scheme 'tp/fp' and 'ARE' to compare true with noise results

@note: Whole project's input & output
    - Input:  'min_sup FSPM' results ( true or noise )
    - Output:
        - [top_k]    'top_k FSPM' results
        - [utility]  measure results

'''

import sys
import string
import getopt


def TopK( fileInput, fileOutput, top_k ):
    '''
    获得top-k频繁序列模式
        1. 対满足min_sup结果集按照计数值降序排序
        2. 过滤掉长度小于1的频繁序列
        3. 输出top-k频繁序列

    @summary: top-k frequent sequential patterns

    @param fileInput: 满足min_sup结果集
    @param fileOutput: 满足top-k结果集

    '''
    seq_sup_dic = {}
    output = open( fileOutput, "w+" )

    for line in open( fileInput, "r" ):
        line = line.strip().split(":")
        
        itemset = line[0].strip().split(" ")
        
        # 过滤掉长度小于1的频繁序列
        if ( len(itemset) <= 1 ):
            continue

        seq_sup_dic[" ".join(itemset)] = string.atof( line[1].strip() )
    
    # 対满足min_sup结果集按照计数值降序排序
    sort_items = sorted( seq_sup_dic.iteritems(), key=lambda d:d[1], reverse=True )
    
    # 输出top-k频繁序列
    # output.write( "File : %s\n" % (fileOutput) )
    # output.write( "\nTotal lines : %s\n\n" % (top_k) )
    for i in range( min(top_k,len(sort_items))):
        output.write( "%s : %s\n" % (sort_items[i][0], str(sort_items[i][1]) ) )
    
    output.close()


def getSeqDict( fileTrue, fileNoise, top_k ):
    
    True_seq_dic = {}
    Noise_seq_dic = {}

    for line in open( fileTrue, "r" ):
        line = line.strip().split(":") 
        True_seq_dic[line[0].strip()] = string.atof( line[1].strip() )

        if len(True_seq_dic) == top_k:
            break;

    for line in open( fileNoise, "r" ):
        line = line.strip().split(":")
        Noise_seq_dic[line[0].strip()] = string.atof( line[1].strip() )

        if len(Noise_seq_dic) == top_k:
            break;

    return True_seq_dic, Noise_seq_dic


def utilityTP( fileTrue, fileNoise, top_k ):
    '''
    频繁序列模式的可用性度量 -- 模式本身内容
        - TP: 纳真值 (True Positive)
        - FP: 纳伪值 (False Positive)
    
    对比True和Noise结果对应Top-K频繁序列模式
    字符串匹配操作为主

    @summary: 模式本身内容可用性度量

    @param fileTrue: 真实top-k频繁序列模式集文件
    @param fileNoise: 满足差分隐私的top-k频繁序列模式集文件

    '''
    True_seq_dic, Noise_seq_dic = getSeqDict( fileTrue, fileNoise, top_k )

    TP = 0
    FP = 0

    for key in Noise_seq_dic:
        if True_seq_dic.has_key(key):
            TP += 1
        else:
            FP += 1

    print "\n 模式本身内容可用性度量"
    print " TOP-K : %d" % (top_k)
    print "   (1) TP : %d" % (TP)
    print "   (2) FP : %d" % (FP)
    print


def utilityARE( fileTrue, fileNoise, top_k ):
    '''
    频繁序列模式的可用性度量 -- 支持度计数
        - ARE: 平均相对误差
            - ARE=0: 完全相同
            - ARE=1: 完全不同(此处理解不对,可能>1,不是完全不同,存在极端值情况)
    
    对比True和Noise结果对应Top-K频繁序列模式
        1. 字符串匹配, 分段设置Noise中序列模式计数
        2. 带入ARE公式求解结果

    @summary: 模式支持度计数可用性度量

    @param fileTrue: 真实top-k频繁序列模式集文件
    @param fileNoise: 满足差分隐私的top-k频繁序列模式集文件

    '''
    True_seq_dic, Noise_seq_dic = getSeqDict( fileTrue, fileNoise, top_k )
    
    ARE = 0.0
    
    for key in True_seq_dic:
        if Noise_seq_dic.has_key(key):
            ratio = abs(Noise_seq_dic[key]-True_seq_dic[key]) / True_seq_dic[key]
            ARE += ratio
        else:
            ARE += 1.0

    ARE = ARE / top_k
    
    print " 模式支持度计数可用性度量"
    print " ARE : %s\n" % (str(ARE))


def Usage():
    print
    print " Usage: python utility.py [arguments] "
    print
    print " Arguments:"
    print "     -f, --inputfile     Set inputfile (min_sup FSPM)"
    print "     -k, --topk          Set top_k (default 200)"
    print "     -n, --nmax          Set n_max (default 5)"
    print "     -l, --lmax          Set l_max (default 20)"
    print "     -e, --epsilon       Set epsilon (default 1.0)"
    print "     -h, --help          help information"
    print


def main():
    
    # Input parameters
    top_k = 100
    n_max = 5
    l_max = 20
    epsilon = 1.0
    
    truefileInput = 'data/msnbc-min_sup_10000-n_max_20-l_max_20.res'
    #truefileInput = 'data/msnbc-min_sup_10000-n_max_32-l_max_14795.res'
    noisefileInput = 'data/msnbc-noisy-n_max_%d-l_max_%d-eps_%.1f-extended.dat'

    try:
        opts, args = getopt.getopt( sys.argv[1:], 'f:k:n:l:e:h', ['inputfile=', 'topk=', 'nmax=', 'lmax=', 'epsilon=', 'help'] )

        for opt, value in opts:
            if opt in ("-k", "--topk"):
                top_k = int(value)
            elif opt in ('-n', '--nmax'):
                n_max = int(value)
            elif opt in ('-l', '--lmax'):
                l_max = int(value)
            elif opt in ('-e', '--epsilon'):
                epsilon = float(value)
            elif opt in ("-h", "--help"):
                Usage()
                sys.exit(1)
        
    except getopt.GetoptError:
        Usage()
        sys.exit(1)
    
    fileOutput = 'data/%s-msnbc-top_k_%d.res'

    TopK( truefileInput, fileOutput%("true", top_k), top_k )
    TopK( noisefileInput%(n_max, l_max, epsilon), fileOutput%("noise", top_k), top_k )
    
    utilityTP( fileOutput%("true", top_k), fileOutput%("noise", top_k), top_k )
    utilityARE( fileOutput%("true", top_k), fileOutput%("noise", top_k), top_k )


if __name__ == "__main__":
    main()
