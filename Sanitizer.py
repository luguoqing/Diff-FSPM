# -*- coding: utf-8 -*-

'''
Created on Apr 30, 2014

@summary: Sanitizing n-grams

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn> 

'''

from math import *
import numpy as np
from itertools import *
from bitarray import bitarray

from lib.NGramTree import *
from lib.NGramSet import *
from lib.Utils import *


def ngram(ngrams_set, n_max, budget, sensitivity):
    '''
    @summary: Sanitizing n-grams

    @param ngrams_set: NGramSet对象
    @param n_max: n_max-grams
    @param budget: differential privacy budget
    @param sensitivity: equal to l_opt

    '''
    budget = float(budget)

    # Loading the set of all ngrams
    tree = NGramTree(ngrams_set)

    # create the root
    root = tree.getRoot()

    # always release the root
    root.left_level = n_max
    root.eps = budget / root.left_level
    root.laplace(sensitivity / root.eps)
    root.releaseAll()
    
    # have no empty sequences
    root.histogram[root.size-1] = 0

    for (gram, node) in tree.iternodes():
        # We do not process levels beyond n_max
        if node.level > n_max:
            break
        # Python 短路语法
        # True or True and not True 仅仅表示 (true) or (True and False) 而不是 (True or True) and (False)
        if tree.isRoot(node) or tree.isParentReleased(node) and node.left_level != None:
            # Computing threshold /theta
            # here tree.size = alphabet_size + 1, with the end symbol
            # but paper 4.3.3 give the threshold without the end symbol
            theta = sensitivity * log(tree.size/2.0) / node.eps
            markovian_neighbor = tree.getReleasedMarkovianParent(node)
            print "Markovian parent:", markovian_neighbor, "Gram:", tree.getNodeGram(markovian_neighbor)

            for i in range(node.size):
                ## To Rui: we release the leaves: left_level is 1 (and do not do thresholding)
                if node.left_level <= 1 or theta < node.histogram[i]:
                    #if theta < node.histogram[i]:
                    node.released[i] = True
                    
                    # we do not expand the end symbol
                    if node.left_level > 1 and i < node.size - 1:
                        child = tree.getChild(node, i)
                        child_markovian_neighbor = tree.getReleasedMarkovianParent(child)
                        p_max = markovian_neighbor.histogram.normalize().max()
    
                        # print "i", i, "h", node.histogram[i], "t", theta, "p", p_max
                        # 计算 left_level 用以自适应隐私预算分配
                        # 通过 p_max 参数作为分割条件，那 p_max=1 代表？
                        # p_max = 1，首先对数运算无法计算；同时概率为1则h为多大都不会影响
                        if p_max == 1:
                            child.left_level = n_max - node.level
                        else:
                            child.left_level = int(min(n_max - node.level, ceil(log(theta / node.histogram[i], p_max)))) 
                        
                        # 计算自适应隐私预算分配，其中
                        # 1.) sum 操作是计算该结点所有父节点消耗的隐私预算和
                        # 2.) child.left_level 表示公式中的分母部分，不是代表距离 n_max 还有多远
                        child.eps = (budget - sum(map(lambda x: x.eps, tree.getAllParents(child)))) / child.left_level
                        child.laplace(sensitivity / child.eps)
            
            if not node.hasReleasedItem() or tree.isRoot(node):
                continue

            # 上面是构建探索树并添加噪音的过程
            # 下面是一致性强制约束的过程？

            # Now, we normalize the whole histogram based on the noisy counts computed before If there are unreleased bins.
            # Approximate them based on Markov propert.
            # A Note: root is generally a bad markovian approximation.
            # Finally, we recompute the noisy count using this normalized histogram and the count of the parent node. 
            # This step results in better utility and provides consistency.

            ### Approximating the non-released bins
            parent_count = tree.getParentCount(node)

            norm_hist = node.histogram.normalize()
            released_items = list(compress(norm_hist, node.released))

            # Approximation
            released_sum = sum(list(compress(node.histogram, node.released)), 0.0)
            released_markov_sum = sum(list(compress(markovian_neighbor.histogram, node.released)), 0.0)

            # Markov neighbor is not unigrams, so Markov neighbor is a good approximator
            if markovian_neighbor.level > 1:
                for i in range(node.size):
                    if not node.released[i]:
                        if released_markov_sum == 0:
                            node.histogram[i] = 0
                        else:
                            node.histogram[i] = released_sum * (markovian_neighbor.histogram[i] / released_markov_sum)

            # Markov neighbor is unigrams (which is a bad approximator), so
            # we uniformly divide the left probability mass among non-released items
            elif released_sum <= parent_count:
                for i in range(node.size):
                    if not node.released[i]:
                        node.histogram[i] = (parent_count - released_sum) / (len(norm_hist) - len(released_items)) 

            else:
                for i in range(node.size):
                    if not node.released[i]:
                        node.histogram[i] = 0


            # Renormalize the histogram to make it consistent
            node.histogram = node.histogram.normalize() * parent_count 

    return tree.createNGramSet()

