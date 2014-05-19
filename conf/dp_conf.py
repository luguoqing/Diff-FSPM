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
epsilon = 1.0

# minmum support value
min_sup = 10000

# sequence length
l_opt = 20 

# ngrams length
n_max = 5

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

# n-grams decomposed file
dataset_ngrams = output_dir + dataset_name + "-original-%d_grams.res"

# noisy file representing FSP-tree
dataset_noisy = output_dir + dataset_name + "-noisy-l_opt_%d-epsilon_%.1f.res"

# extended noisy file, also the FSPM results file
dataset_extend = output_dir + dataset_name + "-noisy-l_opt_%d-epsilon_%.1f-extended.res"
dataset_result = output_dir + dataset_name + "-noisy-l_opt_%d-epsilon_%.1f-extended.res"


#--------------------------------#
# TruncateSeqDB configuration
#--------------------------------#

# empirical ratio value
RATIO_VALUE = 0.96
