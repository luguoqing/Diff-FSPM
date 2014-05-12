# -*- coding: utf-8 -*-

'''
Create On Apr 29, 2014

@summary: Exploration Tree class

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

import math
from bitarray import bitarray
from collections import Counter

from Utils import *
from Histogram import *
from LaplaceMechanism import *


class Node:

    def __init__(self, start_id, size, parent_id, histogram, level = None):
        '''
        @summary: Node Constructor

        @param start_id: Root结点为0
        @param size: 项总数(包含&)
        @param parent_id: Root结点为-1
        @param histogram: 对应可能孩子结点？
        @param level: 树层数, Root为1

        '''
        self.start_id = start_id
        self.histogram = histogram
       
        # 记录父结点 
        self.parent_id = parent_id
        self.childrens = np.array([None] * size)
        
        # 标记是否已发布 - children
        # bitarray 用以初始化 0/1
        self.released = bitarray([False] * size)
        self.size = size
        self.level = level
        self.left_level = None
        self.eps = None

    def laplace(self, b):
        self.histogram = LaplaceMechanism(self.histogram, b)

    def releaseAll(self):
        self.released = bitarray([True] * self.size)

    def hasReleasedItem(self):
        '''
        @summary: 判断Item是否存在发布  ？？？

        @return: True when any bit(存在) in "released" is True.
        @retype: boolean

        '''
        return self.released.any() 

    def areAllItemsReleased(self):
        '''
        @summary: 判断是否完全发布  ？？？

        @return: True when all bits in "released" are True.
        @rtype: boolean

        '''
        return self.released.all()

    def __repr__(self):
        '''
        @summary: 与反引号操作符(``)相同, 以字符串的方式获取对象的内容/类型/数值属性等信息

        @note 区别内建函数str(), 得到的字符串可读性好(被print调用)
            - x.__repr__ <=> repr(x)
            - eval(repr(object)) == object

        @ Return: the canonical string representation of the object
        @rtype: str
        '''
        return self.histogram.__repr__()

    def __len__(self):
        return len(self.histogram)

class NGramTree:

    def __init__(self, ngram_set):
        '''
        @summary: NGramTree Constructor

        @param ngram_set: NGramSet object

        @note:
            - self.size: with the end symbol
            - self.nodes: 树结点集合, self.nodes[0]是Root结点
            - self.start_id: ???
            - self.levels: ???

        '''
        self.nodes = {}
        
        self.size = ngram_set.alphabet_size + 1
        self.ngram_set = ngram_set
        self.start_id = 0 #?
        self.levels = None


    def __len__(self):
        return len(self.nodes)


    def isRoot(self, node):
        return node == self.nodes[0]


    def getRoot(self):
        '''
        @summary: create the Root Node

        @return: self.nodes[0]
        @rtype: Node

        '''
        if not 0 in self.nodes:
            bins = np.zeros(self.size)
            
            # termination is always 0
            for i in range(self.size - 1):
                # default all 1-grams count
                bins[i] = self.ngram_set[unichr(i)]             
            
            self.nodes[0] = Node(0, self.size, -1, Histogram(bins), 1)
            self.start_id += self.size

        return self.nodes[0]


    def idToGram(self, parent_id):
        '''
        @summary: 根据某一层结点编号获得其表示的序列模式前缀
            - Example: 设编号从Root=-1开始, 第3层第一个结点扩展编号为20,21,22,23
                - 对应序列模式为: 2 1 1(反续, 即1->1->2)
                - 返回结果有待处理(1) 逆序 (2) 编号0-3而真实为1-3,&

        @param parent_id: 父结点编号, Root=-1

        @return: sequential pattern Prefix
        @rtype: list

        '''
        gram = []
        while parent_id != -1:
            gram.append(parent_id % self.size)
            start_id = (parent_id / self.size) * self.size
            parent_id = self.nodes[start_id].parent_id
        return gram


    def iternodes(self):
        '''
        @summary: 获得所有可迭代的 n-grams

        @return: (n-gram, nodes)
            - nodes对应的序列模式: n-gram + nodes
        @rtype: generator

        @note: i += self.size 什么意思？？

        '''
        i = 0
        gram = []
        while i in self.nodes:
            yield (self.idToGram(self.nodes[i].parent_id), self.nodes[i])
            i += self.size


    def getMarkovianParentByGram(self, gram):
        if len(gram) == 1:
            return self.getRoot()
        else:
            node = None
            while node == None and len(gram) > 0:
                gram.pop()
                try:
                    node = self.getNodeByGram(gram)
                # If a children is set to None we jump to the next markovian
                # neighbor (we got Typerror or KeyError)
                except KeyError as exception:
                    if exception.args[0] == None:
                        node = None
                    else:
                        raise exception
                except TypeError as exception:
                    node = None
            return node

    def getMarkovianParent(self, node):
        return self.getMarkovianParentByGram(self.idToGram(node.parent_id))

    def getParentCount(self, node):
        return self.getCountById(node.parent_id)

    def getReleasedMarkovianParent(self, node):
        if node.parent_id == -1:
            return node

        released = False
        #id = node.parent_id % self.size
        while not released:
            node = self.getMarkovianParent(node)
            released = node.hasReleasedItem()
            #released = node.released[id]

        return node

    # Calling this function also expands the tree
    def getChild(self, node, id):
        '''

        @note: getRoot中 self.start_id += self.size = 4
        '''
        if node.childrens[id] == None:
            parent_id = node.start_id + id
            histogram = self.getOriginalHistogram(parent_id)
            
            self.nodes[self.start_id] = Node(self.start_id, self.size, parent_id, histogram, node.level + 1)
            node.childrens[id] = self.start_id  
            self.start_id += self.size

        return self.nodes[node.childrens[id]]

    def getOriginalHistogram(self, parent_id):
        '''
        @summary: 获得NGramSet真实支持度计数

        @param parent_id: node对应parent id
        
        @return: Histogram(bins)
        @rtype: Histogram

        '''
        parent_gram = self.idToGram(parent_id)
        bins = np.zeros(self.size)
        # Fetching real counts from NGramSet
        for i in range(self.size):
            str = strToSeq(reversed(parent_gram)) + unichr(i)
            bins[i] = self.ngram_set[str]

        return Histogram(bins)


    def getOriginalHistogramByNode(self, node):
        return self.getOriginalHistogram(node.parent_id)

    def isParentReleased(self, node):
        '''
        @summary: 判断父节点是否已发布

        @param node: 待划分结点

        @return: True or False
        @rtype: boolean

        @note: ???
            - 每个结点维护一个 released?
            - FSP树仅标记 start_id 结点, 进而偏移找到 size 范围内的结点 released
                - 但Root结点是 self.nodes[0].released 标记 1-grams released
        '''
        start_id = (node.parent_id / self.size) * self.size
        return self.nodes[start_id].released[node.parent_id % self.size]

    def createRoot(self):
        self.getRoot()

    def createNGramSet(self):
        # naive 
        self.ngram_set.clear()
        for (id, node) in self.nodes.iteritems():
            if node.hasReleasedItem():
                for i in range(self.size):
                    self.ngram_set[strToSeq(list(reversed(self.idToGram(node.parent_id))) + [i])] = node.histogram[i]

        return self.ngram_set

    def getAllParents(self, node):
        '''
        @summary: 返回所在路径父结点集合
            - 统计分割链已消耗隐私预算之和

        @param node: 待划分结点

        @return: parents
        @rtype: list
        '''
        parent_id = node.parent_id
        parents = []
        while parent_id != -1:
            start_id = (parent_id / self.size) * self.size
            parents.append(self.nodes[start_id])
            parent_id = self.nodes[start_id].parent_id

        return parents

    def getProbById(self, id):
        start_id = (id / self.size) * self.size
        return self.nodes[start_id].histogram.normalize()[id % self.size]

    def getCountById(self, id):
        start_id = (id / self.size) * self.size
        return self.nodes[start_id].histogram[id % self.size]

    def gramToId(self, gram):
        start_id = 0
        gram_cpy = list(gram)
        while len(gram_cpy) > 1:
            item = gram_cpy.pop()
            start_id = self.nodes[start_id].childrens[item] 
        
        return start_id + gram_cpy.pop() if gram_cpy else start_id

    def getNodeGram(self, node):
        return self.idToGram(node.parent_id)

    def getNodeByGram(self, gram):
        return self.getNodeById(self.gramToId(gram))

    def getNodeById(self, id):
        start_id = (id / self.size) * self.size
        return self.nodes[self.nodes[start_id].childrens[id % self.size]]

    def getProbByGram(self, gram): 
        return self.getProbById(self.gramToId(gram))

    def getCountByGram(self, gram): 
        return self.getCountById(self.gramToId(gram))

