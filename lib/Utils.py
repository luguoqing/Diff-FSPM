# -*- coding: utf-8 -*-

'''
Create on Apr 28, 2014

@summary: Utility functions

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

import math
import random as rnd
import numpy as np

def strToSeq(str, dec=0):
    '''
    @summary: 序列记录(list)转换为unicode
        - example: 
            - >>> strToSeq('234', dec=1)
            - >>> u'\x01\x02\x03'

    @param str: 序列记录(list)
    @param dec: 减数, default=1(即结束符self.TERM=self.alphabet_size)

    @return: str的unicode编码表示
    @rtype: unicode

    @note:
        - unichr(i) Return a Unicode string of one character with ordinal i

    '''
    return reduce(lambda x,y: x + y, map(lambda x: unichr(int(x)-dec), str)) 


def seqToStr(sequence, inc=0):
    '''
    @summary: unicode转换为字符串
        - example:
            - >>> seqToStr(u'\x01\x02\x03')
            - >>> '1 2 3'

    @param sequence: unicode序列串
    @param inc: 加数

    @return: unicode对应的字符从
    @rtype: str

    @note: 
        - ord(x)   return ASCII integer of a one-character string

    '''
    return " ".join(map(lambda x: str(ord(x)+inc), sequence))


def KL_div(p, q):
    s = 0
    for i in range(len(p)):
        if p[i] > 0:
            s += p[i] * math.log(float(p[i]) / q[i])
    return s

def sanitize(hist):
    return map(lambda x: max(1, x), hist)

def l2norm(values):
    '''
    @summary: 计算某一数值
        - example:
            - >>> values = [10,2,3,4,5]
            - >>> l2norm( values )
            - >>> sqrt(64) (=10+2^2+9+16+25)

    @param values: 待计算列表

    @return: 平方根
    @rtype: float

    '''
    return math.sqrt(reduce(lambda x,y: x + abs(y)**2, values))


def is_int(s):
    '''
    @summary: Determine whether s is an integer 
    
    @param s: parameter to be judge

    @return: True or False
    @rtype: boolean

    '''
    try:
        int(s)
        return True
    except ValueError:
        return False


def laplace(p_lambda):
    '''
    @summary: Generate Laplace Variable

    @param p_lambda: scale parameter

    @return: Laplace variable
    @rtype: float

    '''
    return np.random.laplace(0, p_lambda, 1)[0]


def normalize(vec):
    s = sum(vec)
    return  vec if s <= 0 else map((lambda x: x/float(s)), vec)

def stat_dist(d1, d2):
    return sum( (abs(d1[i] - d2[i]) for i in range(len(d1))) )
