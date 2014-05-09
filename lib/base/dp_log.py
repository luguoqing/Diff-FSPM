#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Apr 24, 2014

@summary: 统一日志对象

@note:
    - debug:    调试信息
    - info:     程序执行关键节点的信息
    - success:  重要的成功信息
    - warning:  任务有错，可以恢复或忽略
    - diagnose: 出错诊断信息
    - error:    任务出错中断（程序含多个任务）
    - critical: 整个程序出错中断

    - info以上的日志必须是规整的，可以用来进行信息提取和统计
    - 屏幕输出 info以上级别的日志
    - 日志文件输出 所有级别的日志
    - wf日志文件输出warning以上级别的日志

@author: luguoqing <guoqing@nfs.iscas.ac.cn>

'''

import os
import sys
import traceback
import logging
import inspect

#type = sys.getdefaultencoding()
#print "中国".decode('utf-8').encode(type)

# ========= 初始化logging ==========
SUCCESS = 25    # 高于INFO, 小于WARNING
DIAGNOSE = 35   # 高于WARNING, 小于ERROR
def init_logging():
    # 增加一个SUCCESS层级
    logging.addLevelName(SUCCESS, "SUCCESS")

    # 增加一个DIAGNOSE层级
    logging.addLevelName(DIAGNOSE, "DIAGNOSE")

# 调用全局初始化函数
init_logging()
# ========= （end）初始化logging ==========


# ========= 全局函数 =========
def update_nest_level(kwargs):
    '''
    @summary: 更新kwargs中的nest_level，如果存在就+1，如果不存在就置为1
    
    '''
    if "nest_level" in kwargs:
        kwargs["nest_level"] += 1
    else:
        kwargs["nest_level"] = 1
# ========= (end)全局函数 =========


class _dplog(object):
    def __init__(self, logger_name="dplog", tag_name=""):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.tag_name = tag_name

        # 其他成员
        self.sh = None
        self.fmt_sh = None
        self.logpath = None

        # 设置总的logger level
        self.logger.setLevel(logging.DEBUG)

    def set_tag_name(self, tag_name):
        self.tag_name = tag_name

    # -------- 屏幕日志设置 --------
    def init_stream_handler(self):
        # 判断是否重复init
        for h in self.logger.handlers:
            if isinstance(h, logging.StreamHandler):
                #self.warning("Logger %s already has stream handler, ignore this one", self.logger_name)
                self.debug("Logger %s already has stream handler, ignore this one", self.logger_name)
                return


        # 屏幕输出info级别以上的日志
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)

        # 屏幕输出日志格式
        self.fmt_sh = logging.Formatter("[\033[1;%(colorcode)sm%(levelname)-8s\033[0m %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        sh.setFormatter(self.fmt_sh)

        # 将handler加入logger
        self.logger.addHandler(sh)

        # 保存屏幕输出的句柄，后续可以更改
        self.sh = sh

    def set_no_color(self):
        '''
        @summary: 不在屏幕上输出有颜色的日志
        
        '''
        self.fmt_sh = logging.Formatter("[%(levelname)-8s %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        self.sh.setFormatter(self.fmt_sh)

    def set_sh_debug(self):
        '''
        @summary: 屏幕输出debug日志
        
        '''
        self.sh.setLevel(logging.DEBUG)
    # -------- （end）屏幕日志设置 --------

    def set_sh_warning(self):
        '''
        @summary: 屏幕输出warningfatal日志
        
        '''
        self.sh.setLevel(logging.WARNING)
    # -------- （end）屏幕日志设置 --------
    # -------- 文件日志设置 --------
    def init_logger(self, logpath, mode="w", force=False):
        '''
        @summary: 初始化文件日志处理器
        
        @param mode: 'w' for overwrite, 'a' for append
        @param force: 为False时以第一次为准，忽略后续init；为True时以最后一次为准，覆盖之前的init
        
        '''
        # 判断是否重复init
        fhs = [fh for fh in self.logger.handlers if isinstance(fh, logging.FileHandler)]
        if fhs:
            # 已经有file handler了
            if force:
                # 强制更新
                map(self.logger.removeHandler, fhs)
            else:
                # 以第一次为准
                self.warning("Logger %s already has file handler\nIgnore this one: %s\nReserve old one: %s", self.logger_name, logpath, self.logpath)
                return


        # 创建日志目录
        logdir = os.path.dirname(logpath)
        if logdir:
            from dp_system import dpsystem     # 避免循环import，因此放在函数内import
            cmd = "mkdir -p " + logdir
            dpsystem(cmd)

        # 日志文件输出所有级别的日志
        fh = logging.FileHandler(logpath, mode)
        fh.setLevel(logging.DEBUG)

        # 文件输出日志格式
        fmt_fh = logging.Formatter("[%(levelname)-8s %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        fh.setFormatter(fmt_fh)

        # 将handler加入logger
        self.logger.addHandler(fh)

        # wf日志文件输出warning级别以上的日志
        fh_wf = logging.FileHandler(logpath+".wf", mode)
        fh_wf.setLevel(logging.WARNING)

        # 文件输出日志格式
        fmt_fh_wf = logging.Formatter("[%(levelname)-8s %(asctime)s] [%(tagname)s] [%(myfn)s:%(mylno)d:%(myfunc)s] %(message)s", "%m-%d %H:%M:%S")
        fh_wf.setFormatter(fmt_fh_wf)

        # 将handler加入logger
        self.logger.addHandler(fh_wf)

        # 保存logpath，便于unpickle
        self.logpath = logpath
    # -------- (end)文件日志设置 --------

    # -------- 日志打印函数 --------
    def debug(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "0")    # 白色
        self.logger.debug(msg, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "36")   # 浅蓝色
        self.logger.info(msg, **kwargs)

    def success(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "32")   # 绿色
        self.logger.log(SUCCESS, msg, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "33")   # 黄色
        self.logger.warning(msg, **kwargs)

    def diagnose(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "35")   # 粉红色
        self.logger.log(DIAGNOSE, msg, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "31")   # 红色
        self.logger.error(msg, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.__update_caller(kwargs)
        msg = self._handle_msg(msg, args, kwargs)
        self._update_kwargs(kwargs, "41")   # 红底
        self.logger.critical(msg, **kwargs)
    # -------- （end）日志函数 --------

    # -------- find caller --------
    def __update_caller(self, kwargs):
        '''
        @summary: 更新kwargs中的caller信息
        
        @attention:
            - 必须直接被debug等函数调用
            - 不能被子类改写
            
        '''
        # 设置nest_level
        if "nest_level" in kwargs:
            nest = kwargs["nest_level"]
            del kwargs["nest_level"]
        else:
            nest = 0    # 默认为0

        # 获取正确的栈信息
        try:
            frame = inspect.stack()[2+nest]     # 默认向上数2层：__update_caller <- log functions <- log invoker
            _, fn, lno, func, _, _ = frame
            fn = os.path.basename(fn)
        except Exception:
            fn, lno, func = "(unknown file)", 0, "(unknown function)"

        # 设置extra字典
        if not "extra" in kwargs:
            # kwargs中没有extra字典，创建它
            kwargs["extra"] = {}

        kwargs["extra"]["myfn"] = fn
        kwargs["extra"]["mylno"] = lno
        kwargs["extra"]["myfunc"] = func
    # -------- (end)find caller --------

    # -------- msg修正函数 --------
    def _handle_msg(self, msg, args, kwargs):
        if args:
            msg = msg % args
        msg = self.__encgb_excinfo(msg, kwargs)

        msg = self.__indent_msg(msg.rstrip(), args)
        return msg

    def __encgb_excinfo(self, msg, kwargs):
        '''
        @summary: 将kwargs中的exc_info，转码为gb18030后merge到msg中
        @attention: exc_info为traceback三元组时，不进行转码
        
        '''
        if not "exc_info" in kwargs or not kwargs["exc_info"] or isinstance(kwargs["exc_info"], tuple):
            # kwargs不存在exc_info
            # 或者 exc_info为False
            # 或者 exc_info为tuple
            return msg

        # exc_info为True
        del kwargs["exc_info"]

        s = traceback.format_exc()
        msg = msg + "\n" + s
        return msg

    def __indent_msg(self, msg, args):
        '''
        @summary: 将msg从第2行开始indent
        
        '''
        msg_lines = msg.splitlines(True)
        if not msg_lines:
            msg_lines = [""]

        msg_indent_lines = []
        msg_indent_lines.append(msg_lines[0])
        msg_indent_lines.extend(["  - " + line for line in msg_lines[1:]] )

        return "".join(msg_indent_lines)
    # -------- (end)msg修正函数 --------

    # -------- kwargs修正函数 --------
    def _update_kwargs(self, kwargs, colorcode):
        # 设置extra字典
        kwargs["extra"]["colorcode"] = colorcode

        # 设置extra字典中的tagname
        if "tag_name" in kwargs:
            tagname = kwargs["tag_name"]
            del kwargs["tag_name"]
        else:
            tagname = self.tag_name
        kwargs["extra"]["tagname"] = tagname

        # 清除非法键值
        self.__clean_kwargs(kwargs)

    def __clean_kwargs(self, kwargs):
        '''
        @summary: 清除kwargs中的非法键值
        
        '''
        for key in kwargs.keys():
            if key not in ("exc_info", "extra"):
                del kwargs[key]
    # -------- (end)kwargs修正函数 --------


class LogProxy(object):
    '''
    @summary: logger代理类，全局唯一
    
    '''
    def __init__(self, inst):
        self.set_instance(inst)

    def set_instance(self, inst):
        self.inst = inst

    def __getattr__(self, name):
        '''
        @summary: 将不存在的成员访问，委托给self.inst
        
        '''
        return getattr(self.inst, name)


# dplog 全局句柄，默认设置屏幕输出
dplog = LogProxy(_dplog())
dplog.init_stream_handler()


def _test():
    dplog.init_logger("./test.log")

    dplog.debug("debug 日志")
    dplog.info("info %s 日志\n换行")
    try:
        raise Exception, "except 异常"     # this is a 异常注释 !
    except Exception:
        dplog.warning("warning %s", "日志", exc_info=True)
    dplog.diagnose("error %s日志", "格式字符串")
    dplog.critical("critical 日志")

if __name__ == "__main__":
    _test()
