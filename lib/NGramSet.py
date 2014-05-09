# -*- coding: utf-8 -*-

'''
Create on Apr 28, 2014

@summary: Truncate Original Sequence Database
    - sequence parsing
    - stores and writes the n-gram set to file. 

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

import os
import ngram
from collections import Counter
from functools import cmp_to_key

from Utils import *
from ProgressBar import *
from base.dp_log import dplog

def compare_grams(x, y):
    '''
    @summary: give the definition of grams compare
        - short grams prior
        - little grams prior
    '''
    if len(x) == len(y):
        return cmp(x, y)

    return len(x) - len(y)


class NGramSet(Counter):
    '''
    @summary: 继承于Counter(字典)

    '''
    def __init__(self, max_len, N_max = 5):
        '''
        @summary: NGramSet Constructor

        @param max_len: 最优序列长度
        @param N_max: CCS2012 对应最大n-gram

        '''
        Counter.__init__(self)
        
        self.N_max = N_max
        self.max_len = max_len
        
        self.alphabet_size = 0    # 记录项总数
        self.all_record_num = 0   # 记录数据集中记录总数
        self.TERM = 0             # 序列结束符

        # self.lines = []

    
    def load_dataset(self, in_file, dump_file):
        '''
        @summary: 截断原始序列数据集

        @param in_file: 原始序列数据集文件
        @param dump_file: 截断归约表示文件

        '''
        if not os.path.isfile(dump_file):
            dplog.debug( "File (%s) does not exist!"%(dump_file) )
            dplog.debug( "Creating File (%s)" % (dump_file) )
            
            self.parse_sequences(in_file)
            self.dump(dump_file)
        
        else:
            self.load_dump(dump_file)
            

    def load_dump(self, filename):
        '''
        @summary: 写结果到目标文件 

        @param filename: write-file name

        '''
        file = open(filename)

        ngram_num = int(file.readline().strip())    # 已存在目标文件第一行为ngrams总数
        #self.alphabet_size = int(file.readline().strip())

        dplog.debug( "ngrams total : %d" % (ngram_num) )
        dplog.debug( "Loading ngrams file (%s, l_opt=%d)..." % (filename, self.N_max) )

        pbar = MyProgressBar('Loading dump', ngram_num)

        for (line_num, line) in enumerate(file):

            # 区别 str.partition & str.split
            # line = 'lu:123:qin'
            # 1. line.partition(':')    >>> ('lu', ':', '123:qin')
            # 2. line.split(':')        >>> ['lu', '123', 'qin']
            parts = line.strip().partition(':')
            tokens = parts[0].strip().split()
            self[strToSeq(tokens, dec=1)] = float(parts[2].strip()) 
            
            max_item = max(map(int, tokens)) - 1
            if self.alphabet_size < max_item:
                self.alphabet_size = max_item

            pbar.update(line_num + 1)

        pbar.finish()
        
        self.TERM = self.alphabet_size 

        dplog.debug( "Alphabet size : %d" % (self.alphabet_size) )

    
    def parse_sequences(self, filename):
        '''
        @summary: truncate sequences
            - 最优序列长度 l_opt 截断原始序列数据集
            - Counter.update & ngram.NGram 保存所有n_max-gram序列模式和支持度计数

        @param filename: sequential database

        @return: 原始序列数据集对应的n_max-gram和计数
        @rtype: Counter

        @note: assume that locations are numbered from 1 .. max

        '''
        dplog.info( " === Phase 1.2: Truncating Sequence file (%s, l_opt=%d) ===" % ( filename, self.max_len) )
        
        file = open(filename)

        self.all_record_num = 0
        lines = []

        # First check the alphabet
        for line in file:
            if line.startswith('#') or line.startswith('//') or line.startswith('%'):
                continue
            
            # self.lines.append(line.strip().split()[:self.max_len])
            lines.append( line.strip().split()[:self.max_len] )
            
            ''' 
            max_item: the max-value item in one max_len sequence
            
            需要有前提: 项集编号从1开始，且连续到max
            >>> map(int, '234')
            [2, 3, 4]
            
            '''
            max_item = max(map(int, lines[-1]))

            if self.alphabet_size < max_item:
                self.alphabet_size = max_item

            self.all_record_num += 1

        # be the end point
        self.TERM = self.alphabet_size
        dplog.debug( "Alphabet size : %s" % (str(self.alphabet_size)) )
        dplog.debug( "Termination code : %s" % (str(self.TERM)) )
        dplog.debug( "Number of sequences : (%s)" % (self.all_record_num) )

        pbar = MyProgressBar('Parsing', self.all_record_num + 1)
        
        # 下面这几行涉及 NGram 操作
        for (record, line) in enumerate(lines):
            ''' 
            >>> strToSeq('234', dec=1)
            u'\x01\x02\x03'
            
            >>> line = '123'
            >>> self.TERM = 3
            u'\x00\x01\x02\x03'

            '''
            # 序列记录添加结束符 self.TERM
            seq = strToSeq(line, dec=1) + unichr(self.TERM)
            for i in range(1, self.N_max+1):
                '''
                (N=i) defines N-gram
                
                Example:
                >>> G = ngram.NGram(N=3)
                >>> a = G.ngrams([u'\x01', u'\x02', u'\x03', u'\x04', u'\x05'])
                >>> print list(a)
                [[u'\x01', u'\x02', u'\x03'], [u'\x02', u'\x03', u'\x04'], [u'\x03', u'\x04', u'\x05']]
                    
                '''
                G = ngram.NGram(N=i)
                
                # Counter every gram from 1...N_max(包含结束符)
                self.update(G.ngrams(seq))

            pbar.update(record + 1)
        pbar.finish()

        file.close()


    def dump(self, filename):
        
        dplog.info( "Creating ngram file (%s, N=%d)..." % (filename, self.N_max) )

        file = open(filename, 'w')
        
        #file.write( 'ngrams : ' + str(len(self)) + '\n' )  # len(self)表示所有ngrams总数
        file.write( str(len(self)) + '\n' )
        #file.write( 'alphabet_size : ' + str(self.alphabet_size) + '\n' )
        
        pbar = MyProgressBar('Dumping', len(self))

        i = 0
        for gram in sorted(self.keys(), key=cmp_to_key(compare_grams)):
            # NOTE: ord(x)+1 should be in order to remain compatible with the input format
            file.write("%s : %f\n" % (" ".join(map(lambda x: str(ord(x)+1), gram)),self[gram]))
            # file.write( "%s : %f\n" % ((seqToStr(gram, inc=1), self[gram])) )
            i += 1
            pbar.update(i)

        pbar.finish()

        '''
        pbar = MyProgressBar('Dumping', len(self.lines))
        i = 0
        for line in self.lines:
            file.write( "%s\n" % (" ".join(line)) )
            i += 1
            pbar.update(i)
        pbar.finish()
        '''

        file.close()

        
if __name__ == "__main__":

    ngram_set = NGramSet(max_len=3)
    ngram_set.load_dataset("testdata/test.dat", "testdata/res.dat")
