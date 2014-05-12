#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import string


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


def process_TP( fileTrue, fileNoise, top_k ):
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

def process_ARE( fileTrue, fileNoise, top_k ):
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


if __name__ == "__main__":

    top_k = string.atoi(sys.argv[1])

    fileTrue = "data/TRUE-msnbc-top_k_100.res"
    fileNoise = "data/NOISE-msnbc-top_k_100.res"
    fileTruncate = 'data/TRUNCATE-msnbc-top_k_100.res'

    '''
    模式本身内容可用性度量
    TOP-K : 200
      (1) TP : 107
      (2) FP : 93

    @notice 文章实验结果较高(>90%)
        可能原因
            - 与 K(20-100),E(0.1,1.0) 值有关系
            - 还是 count 与 occurrence 的区别
                - prefixspan 不记录一条记录中重复出现次数

    '''
    #process_TP( fileTrue, fileNoise, top_k )
    process_TP( fileTrue, fileTruncate, top_k )
    
    '''
    模式支持度计数可用性度量
    ARE : 0.993022488521

    @notice 结果接近于1
        - 主要归于 occurrence
    '''
    #process_ARE( fileTrue, fileNoise, top_k )
    process_ARE( fileTrue, fileTruncate, top_k )
