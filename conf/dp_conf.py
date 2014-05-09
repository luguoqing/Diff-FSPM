# encoding: utf-8

'''
Created on Apr 24, 2014

@summary: configuration file
@author: luguoqing <guoqing@nfs.iscas.ac.cn>

'''

#--------------------------------#
# Input parameters
#--------------------------------#

# input files directory
input_dir = "data/input/"

# original sequence database name
dataset_name = "msnbc"

# original sequence database
dataset = input_dir + dataset_name + ".dat"

# differential privacy budget
epsilon = 0.1

# minmum support value
min_sup = 10

# sequence length
l_opt = 3


#--------------------------------#
# Log configuration 
#--------------------------------#

# normal log file directory
LOG_FILE = "log/dp_fspm.log"

# sensitive log file directory
LOG_FILE_WF = "log/dp_fspm.log.wf"

# log level
LOG_LEVEL = "DEBUG"


#--------------------------------#
# Output files configuration 
#--------------------------------#

# output files directory
output_dir = "data/output/"

# truncated sequence database
# dataset_truncate = output_dir + dataset_name + "-truncate-l_opt_%d"%(l_opt) + ".res"
dataset_truncate = output_dir + dataset_name + "-truncate-l_opt_%d.res"

# n-grams decomposed file
dataset_ngrams = output_dir + dataset_name + "-original-%d_grams.res"

#--------------------------------#
# TruncateSeqDB configuration
#--------------------------------#

# empirical ratio value
RATIO_VALUE = 0.95
