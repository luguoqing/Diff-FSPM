# -*- coding: utf-8 -*-

'''
Create on May 8, 2014

@summary: 指数机制

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

from random import random
import math

from base.dp_log import dplog


def ExponentialMechanism( sequences, fraction, epsilon ):
    '''
    @brief 指数机制获取最优序列长度

    @param sortlist: 序列数据集记录长度真实分布
    @param fraction: 经验值, 默认0.85
    @param epsilon: 隐私预算

    @return: 最优序列长度l_opt
    @rtype: int

    '''
    target = len( sequences ) * fraction

    sequences.sort()
    
    dplog.info( "sort sequences length: %d" % (len(sequences)) )
    dplog.info( "sequences head median tail : %d\t%d\t%d" % (sequences[0], sequences[int(target)-1], sequences[-1]) )

    previous = 0 
    counter = 0
    l_opt = 0.0
    tally = 0.0
    
    fraction = fraction - 0.05
    counter =  int( len(sequences)*fraction - 1 )
    previous = sequences[counter]
    sequences = sequences[counter+1:]

    # a custom aggregator that reservoir samples from the sorted list
    for value in sequences:
        counter += 1
        
        # python 没有三元运算符
        # sample = (random() > tally / (tally + (value-previous))*math.exp(-epsilon*abs(target-counter))) ? (value-previous)*random() + previous : sample
        # dplog.info( "exponential tally : %f %f" % (tally, (value-previous)*math.exp(-epsilon*abs(target-counter))) )
        # dplog.info( "value : %d\tprevious : %d\ttarget: %d\tcounter : %d" % (value, previous, target, counter) )
        if math.fabs( tally + (value-previous)*math.exp(-epsilon*abs(target-counter)) -0.0 ) <= 1E-1000:
            continue
        else:    
            l_opt = ((value-previous)*random() + previous) if (random() > tally / (tally + (value-previous)*math.exp(-epsilon*abs(target-counter)))) else l_opt
        tally = tally + (value-previous)*math.exp(-epsilon*abs(target-counter)) 
        previous = value
    
    return l_opt


if __name__ == "__main__":
    # sequences = [1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6, 7, 8, 10]
    sequences = [3, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    fraction = 0.5
    epsilon = 1
    
    l_opt = ExponentialMechanism( sequences, fraction, epsilon )

    print "\nThe Optimal sequence length : %f\n" % (l_opt)
