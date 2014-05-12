#! /usr/bin/env python
# -*- coding: utf-8 -*-

import string

def process( fileInput, fileOutput, top_k ):
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
    output.write( "File : %s\n" % (fileOutput) )
    output.write( "\nTotal lines : %s\n\n" % (top_k) )
    for i in range( min(top_k,len(sort_items))):
        # print "%s : %s" % (sort_items[i][0], str(sort_items[i][1]))
        output.write( "%s : %s\n" % (sort_items[i][0], str(sort_items[i][1]) ) )
    
    output.close()


if __name__ == "__main__":
    top_k = 100
    
    fileInput = "data/msnbc-min_sup_10000.res"
    fileOutput = "data/TRUE-msnbc-top_k_%d.res" % (top_k)
    process( fileInput, fileOutput, top_k )

    fileInput = "data/msnbc-noisy-n_max_5-l_max_20-eps_1-extended.dat"
    fileOutput = "data/NOISE-msnbc-top_k_%d.res" % (top_k)
    process( fileInput, fileOutput, top_k )

    fileInput = 'data/msnbc-min_sup_10000-truncate.res'
    fileOutput = 'data/TRUNCATE-msnbc-top_k_%d.res' % (top_k)
    process( fileInput, fileOutput, top_k)
