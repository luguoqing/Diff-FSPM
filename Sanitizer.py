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
from conf import dp_conf as conf


def ngram(ngrams_set, n_max, budget, sensitivity, min_sup):
    '''
    @summary: Sanitizing n-grams

    @param ngrams_set: NGramSet对象
    @param n_max: n_max-grams
    @param budget: differential privacy budget
    @param sensitivity: equal to l_opt
    @param min_sup: occurrence threshold

    '''
    budget = float(budget)
    min_sup = int(min_sup)
    
    # Uniform privacy budget
    epsilon = budget / n_max

    # Loading the set of all ngrams
    tree = NGramTree(ngrams_set)

    # create the root, always release the root
    root = tree.getRoot()
    root.left_level = n_max
    root.eps = budget / root.left_level
    root.laplace(sensitivity / root.eps)
    root.releaseAll()
    root.histogram[root.size-1] = 0     # have no empty sequences

    for (gram, node) in tree.iternodes():
        # We do not process levels beyond n_max
        if node.level > n_max:
            break

        # Python 短路语法
        # True or True and not True 仅仅表示 (true) or (True and False) 而不是 (True or True) and (False)
        if tree.isRoot(node) or tree.isParentReleased(node) and node.left_level != None:
            markovian_neighbor = tree.getReleasedMarkovianParent(node)

            for i in range(node.size):
                # release the leaves: left_level is 1 (and do not do thresholding)
                if node.left_level <= 1 or min_sup < node.histogram[i]:
                    node.released[i] = True
                    
                    # do not expand the end symbol
                    if node.left_level > 1 and i < node.size - 1:
                        child = tree.getChild(node, i)

                        '''
                        child_markovian_neighbor = tree.getReleasedMarkovianParent(child)
                        p_max = markovian_neighbor.histogram.normalize().max()
    
                        if p_max == 1:
                            child.left_level = n_max - node.level
                        else:
                            child.left_level = int(min(n_max - node.level, ceil(log(theta / node.histogram[i], p_max)))) 
                       
                        '''
                        child.left_level = n_max - node.level
                        import pdb
                        pdb.set_trace()
                        child.eps = (budget - sum(map(lambda x: x.eps if x.noised[i] else 0, tree.getAllParents(child)))) / child.left_level
                        dplog.debug( "child node information -> left_level: %d, eps: %f" % (child.left_level, child.eps) )
                        child.laplace(sensitivity / child.eps)
                        
                        # 在此添加连接操作获得预测计数值, 与拉普拉斯噪音计数值比较
                        # (1) 保证扰动计数的高可用性; (2) 节约隐私预算.
                        # 疑惑点: child.laplace 获得的是扩展项(孩子结点)的噪音计数值
                        
                        # 错误点: 该操作修改 tree.ngram_set, 而构建 child 结点对应的 Histogram 来自于 ngram_set
                        # tree.ngram_set 记录序列模式的真实支持度计数
                        # tree.createNGramSet()
                        base_grams = createBaseNGramSet( tree )

                        if child.level >= 3:
                            parent_gram = tree.idToGram( child.parent_id )
                            for i in range(tree.size):
                                str = strToSeq( reversed(parent_gram) ) + unichr(i)
                                real = float(ngrams_set[str])
                                noise = float(child.histogram[i])
                                
                                # 当前的问题: 
                                # 1. predict 计算需要三个 noise 值, 如何 getCount 是个问题？
                                # 2. 若使用 predict, eps的计算也是个问题？
                                g1 = base_grams[str[:-1]]
                                g2 = base_grams[str[1:]]
                                k = base_grams[str[1:-1]]
                                if g1 > 0 and g2 > 0 and k > 0: 
                                    predict = float( g1 * g2 / k )
                                    
                                    if math.fabs(predict-real) < math.fabs(noise-real):
                                        dplog.debug( "gram: [%s] select predict value %f, real %f, noise %f" % (seqToStr(str, inc=1), predict, real, noise) )
                                        child.histogram[i] = predict 
                                        child.noised[i] = False
            
            if not node.hasReleasedItem() or tree.isRoot(node):
                continue

            # 上面是构建探索树并添加噪音的过程, 下面是一致性强制约束的过程
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

    return tree.createNGramSet(min_sup)


def createBaseNGramSet( tree ):
    '''
    @summary: "同构" NGramTree.createNGramSet 方法
        - 保证不修改 tree.ngram_set
        - 用于连接操作的基础 grams

    @param tree: 当前划分 FSP 树

    @return: base_grams
    @rtype: {}

    '''
    base_grams = {}

    for (id, node) in tree.nodes.iteritems():
        for i in range(tree.size):
            base_grams[ strToSeq(list(reversed(tree.idToGram(node.parent_id))) + [i]) ] = node.histogram[i]

    return base_grams
