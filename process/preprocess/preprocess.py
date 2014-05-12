#! /usr/bin/env python
# -*- coding: utf-8 -*-

def preprocess( fileName, fileOutput ):
    
    count = 0
    dic = {}
    output = open( fileOutput, 'w+' )

    for line in open( fileName, 'r' ):
        line = line.strip().split(' ')
        count += 1

        if not dic.has_key( str(len(line)) ):
            dic[str(len(line))] = 1 
        else:
            dic[str(len(line))] += 1
    
    # sorted 排序字典返回列表 []
    # 但 dict([]) 强制转换列表, 返回字典key随意分布, 破坏降序
    sortlist = sorted( dic.iteritems(), key=lambda d:int(d[0]) )

    #for (key, value) in dic.items():
        # print "%s : " % key, value
        #output.write( '%s\t%s\n' % (key, str(value)))

    for item in sortlist:
        output.write( '%s\t%s\n' % (str(item[0]), str(item[1]) ))
    output.write( 'Total lines : ' + str(count) + '\n' )

    output.close()


def test():
    dic = {'a':31, 'bc':5, 'c':3, 'asd':4, 'aa':74, 'd':0}
    sortlist= sorted(dic.iteritems(), key=lambda d:d[0])
    print sortlist
    print dict(sortlist)


if __name__ == '__main__':
    
    # fileName = 'msnbc.seq'
    # fileOutput = 'msnbs.res'

    fileName = 'pumsb_star.dat'
    fileOutput = 'pumsb_star.res'

    preprocess( fileName, fileOutput )
