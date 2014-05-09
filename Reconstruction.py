# encoding: utf-8
'''
Create on Apr 29, 2014

@summary: Extend longer sequential patterns from N-Grams

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>
'''

from lib.Utils import *
from lib.NGramSet import *
from collections import Counter, defaultdict
from lib.ProgressBar import *

class Reconstruction:

    def __init__(self, ngramset, l_max):
        self.ngramset = ngramset
        self.l_max = l_max

    def join(self, g1, g2, new_grams):
        '''
        @summary: join two grams
            - 如 {2 3 1} + {3 1 2} = {2 3 1 2}

        @param g1: (n-1)-gram
        @param g2: (n-1)-gram
        @param new_grams: n-gram结果集

        @return new_grams
        @rtype: list
        '''
        new_count = int(float(self.ngramset[g1] * self.ngramset[g2]) / self.ngramset[g2[:-1]])
        # 此处 Diff-FSPM 需要修改 1 为 min_sup
        if new_count >= 1:
            new_grams.append(g1 + g2[-1])
            self.ngramset[new_grams[-1]] = new_count 

    def create_prefix_set(self, grams):
        '''
        @summary: Creating hashmap to speed up computation ???
            - key: 前n-1个前缀项
            - value: 最后一个项

        @param grams: max_grams
        '''
        prefixes = defaultdict(set)

        for gram in self.ngramset.keys():
            prefixes[gram[:-1]].add(gram[-1])

        return prefixes

    def floor(self):
        '''
        @summary: 対ngram序列模式计数取整

        @note: ngramset继承于Counter(字典)
            - del: remove all assigned key
        '''
        for i in self.ngramset.keys():
            self.ngramset[i] = int(self.ngramset[i])
            if self.ngramset[i] <= 0:
                del self.ngramset[i]

    def extend(self):
        '''
        @summary: 连接操作
            - 马尔科夫假设: 长序列模式可以通过短序列模式链接来获得
            - Reconstruct longer grams from shorter ones using the Markov approach

        '''
        max_len = 1
        max_grams = []

        self.floor()

        # This loop is to select the longest grams in a single scanning of the ngramset
        # 统计长度最长的所有grams
        for i in self.ngramset.keys():
            if len(i) >= max_len:
                if len(i) > max_len:
                    max_grams = []
                    max_len = len(i)
                
                max_grams.append(i)

        # This loop is to join only the joinable longest grams
        # (we do it until there are no more grams that can be joined)

        print "Generating longer grams..."

        while len(max_grams) > 1 and len(max_grams[0]) < self.l_max:
            new_grams = []

            print "Num. of %d-grams: %d" % (len(max_grams[0]), len(max_grams))

            # Creating hashmap to speed up computation (at the cost of memory)
            prefixes = self.create_prefix_set(max_grams)

            pbar = MyProgressBar('Generating %d-grams' % (len(max_grams[0])+1), len(max_grams))

            for (i, g1) in enumerate(max_grams):
                k = g1[1:]
                if k in prefixes.keys():
                    for suffix in prefixes[k]:
                        self.join(g1, k + suffix, new_grams)

                pbar.update(i)

            pbar.finish()

            max_grams = new_grams
