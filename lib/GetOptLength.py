# -*- coding: utf-8 -*-

'''
Create on Apr 28, 2014

@summary: 获得最优序列长度 l_opt

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''
import sys
sys.path.append( ".." )
from conf.dp_conf import RATIO_VALUE

from base.dp_log import dplog
from Utils import *
from ExponentialMechanism import *


def EstimateDistribution( filename, epsilon, noise ):
    '''
    @summary: 拉普拉斯噪音扰动序列长度计数

    @param filename: Sequence DB
    @param epsilon: privacy budget
    @param noise: use Laplace Mechanism or not

    @return: noisySeqLengthRatioList
    @rtype: list

    '''
    dplog.info( "Get l_opt from file (%s)..." % (filename) )

    file = open(filename)
    total = 0
    dic = {}
    sequences = []

    for line in file:
        if line.startswith('#') or line.startswith('//') or line.startswith('%'):
            continue
        
        line = line.strip().split(' ')
        total += 1
        sequences.append( len(line) )

        if not dic.has_key( len(line) ):
            dic[ len(line) ] = 1
        else:
            dic[ len(line) ] += 1

    sortlist = sorted( dic.iteritems(), key=lambda k:k[0] )
    NoisySeqLengthList = []

    if str(noise) == 'True':
        # dplog.debug( '=== before Laplace Mechanism ===' )
        # dplog.debug( 'sortlist:\n %s' % (str(sortlist)) )

        # 避免出现负数
        NoisySeqLengthList = map(lambda x: (x[0],max(0,0,x[1] + laplace(1/float(epsilon)))), sortlist )
        
        dplog.debug( '=== Laplace Mechanism ===' )
        dplog.debug( 'epsilon: (%f)' % (epsilon) )
        dplog.debug( 'scale parameter: (%f)' % (1/float(epsilon)) )
        # dplog.debug( '=== after Laplace Mechanism ===')
        # dplog.debug( 'Noisy-sortlist :\n%s' % (str(NoisySeqLengthList)) )

        NoisySeqLengthRatioList = map(lambda x: (x[0], x[1] / float(total)), NoisySeqLengthList )
        # dplog.debug( 'Noisy-sortlist-Ratio :\n%s' % (str(NoisySeqLengthRatioList)) )

        return NoisySeqLengthRatioList

    elif str(noise) == 'False':
        return sequences

    file.close()


def GetOptSeqLength( filename, epsilon, mechanism="Exponential" ):
    '''
    @summary: 获得最优序列长度

    @param filename: Sequence DB
    @param epsilon: privacy budget
    @param mechanism: which noise mechanism
        - Laplace Mechanism
        - Exponential Mechanism ( default )
    
    @return: l_opt
    @rtype: int

    '''
    dplog.info( " === Phase 1.1: GetOptSequenceLength Begin ===" )
    
    if mechanism == "Laplace":
        seqLengthList = EstimateDistribution( filename, epsilon, "True" )
        total = 0.0
        # 默认l_opt取最大序列长度, 避免扰动比率和<RATIO_VALUE
        l_opt = seqLengthList[-1][0] 

        for item in seqLengthList:
            total += item[1]

            if total >= RATIO_VALUE:
                l_opt = item[0]
                break
    
    elif mechanism == "Exponential":
        seqLengthList = EstimateDistribution( filename, 0.0, "False" )    
        l_opt = ExponentialMechanism( seqLengthList, RATIO_VALUE, epsilon )

    dplog.debug( "Empirical ratio value is : (%s)" % (str(RATIO_VALUE)) )
    dplog.info( "l_opt = %d" % (math.ceil(l_opt)) )
    dplog.info( " === Phase 1.1: GetOptSequenceLength End ===" )

    return math.ceil(l_opt)


if __name__ == '__main__':

    import getopt
    
    try:
        # opts 包含元组(tuple)的列表, 如[('-e','1.0')] 
        # args 列表, 包含没有'-'和'--'的参数
        opts, args = getopt.getopt( sys.argv[1:], 'f:e:m', ['filename=', 'espilon='])
        
        if ( len(opts) == 0 ) and ( len(args) == 0 ):
            print "no parameters!"
            sys.exit(1)

        epsilon = 1.0
        mechanism = 'Exponential'

        for opt,value in opts:
            if opt in ('-f', '--filename'):
                filename = value
            elif opt in ('-e', '--epsilon'):
                epsilon = value
            elif opt in ('-m'):
                mechanism = 'Laplace'

    except getopt.GetoptError:
        print "getopt Error!"
        sys.exit(1)

    l_opt = GetOptSeqLength( filename, epsilon, mechanism )
    print "l_opt = %d" % (math.ceil(l_opt))
