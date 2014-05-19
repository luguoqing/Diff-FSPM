# -*- coding: utf-8 -*-

'''
Create on Apr 28, 2014

@summary: Utility functions

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

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
