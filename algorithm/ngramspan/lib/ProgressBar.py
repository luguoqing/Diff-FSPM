# -*- coding: utf-8 -*-

'''
Create on Apr 28, 2014

@summary: 控制台进度条组件
    - Home: http://code.google.com/p/python-progressbar/

@author: Lu Guoqing <guoqing@nfs.iscas.ac.cn>

'''

from progressbar import Bar, ETA, Percentage, ProgressBar

class MyProgressBar:

    def __init__(self, label, maxv):
        widgets = [label + ' ', Percentage(), ' ', Bar(), ' ', ETA()]
        self.pbar = ProgressBar(widgets=widgets, maxval=maxv).start()

    def update(self, num):
        self.pbar.update(num)

    def finish(self):
        self.pbar.finish()

