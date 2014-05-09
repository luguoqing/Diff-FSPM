# -*- coding: utf-8 -*-

'''
Create on Apr 28, 2014

@summary: 拉普拉斯噪音机制

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

from Utils import *
from Histogram import *

def LaplaceMechanism(hist, scale_p):
    #print "\n>>>>>>"
    #print map(lambda x: x, hist.bins) 
    #print ">>>>>>\n"
    
    return Histogram(map(lambda x: x + Utils.laplace(scale_p), hist.bins))
