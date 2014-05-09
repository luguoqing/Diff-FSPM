# -*- coding: GB18030 -*-

'''
@Created on Apr 24, 2014

@summary: 命令行调用
    - Bash命令行调用
    - 托管命令行调用的输出，避免和日志冲突

@author: luguoqing <guoqing@nfs.iscas.ac.cn>

'''

import sys
import subprocess
import fcntl
import os
import select

from dp_log import dplog


def dpsystem(cmd, output=False, loglevel=None, errlevel="warning", prompt="Run cmd", pflag=False, logger=dplog):
    '''
    @summary: (阻塞)调用shell命令cmd
    @attention: 如果要后台启动程序，请使用dpsystem_async()
    
    @param output: 
     - 为True时，返回cmd的 (return code, stdout output, stderr output)
     - 为False时，只返回cmd的return code。命令的输出被重定向到/dev/null
    
    @param loglevel: 
     - 可以为None, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - 不为None时，执行的cmd被记入日志
    
    @param errlevel: 
     - 可以为None, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - 不为None时，当cmd返回码不为0，则记录日志
    
    @param pflag: print flag。为True时打印cmd的屏幕输出
    
    @param logger: log object。默认为dplog
    
    @param prompt: 日志提示符
    '''
    if loglevel:
        log_func = getattr(logger, loglevel)
        log_func("%s: %s", prompt, cmd)
        
    if errlevel:
        err_func = getattr(logger, errlevel)
    else:
        err_func = None
    
    if output:
        return _dpsystem_output(cmd, err_func, prompt, pflag)
    else:
        return _dpsystem_output(cmd, err_func, prompt, pflag)[0]
    
    
def dpsystem_async(cmd, loglevel=None, prompt="Run cmd", pflag=False, logger=dplog):
    '''
    @summary: 后台运行shell命令cmd
    
    @param loglevel: 
     - 可以为None, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - 不为None时，执行的cmd被记入日志
     
    @param prompt: 日志提示符
    
    @param pflag: print flag。为True时打印cmd的屏幕输出
    
    @param logger: log object。默认为dplog
    
    @return: 返回cmd的pid
    '''
    if loglevel:
        log_func = getattr(logger, loglevel)
        log_func("%s: %s", prompt, cmd)
        
    if pflag:
        dev = sys.stdout
    else:
        dev = open("/dev/null", "w")
    proc = subprocess.Popen(cmd, shell=True, stdout=dev, stderr=subprocess.STDOUT)
    return proc.pid
    
    
def _dpsystem_output(cmd, err_func, prompt, pflag):
    '''@return: 返回(return code, stdout output, stderr output)'''
    outdata_l = []
    errdata_l = []
    
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    # stderr必须是单独的PIPE
    
    # 将proc的stdout和stderr设置为非阻塞
    for f in [proc.stdout, proc.stderr]:
        flags = fcntl.fcntl(f, fcntl.F_GETFL)
        fcntl.fcntl(f, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    
    while True:
        # 轮询
        ret = proc.poll()
        r, w, x = select.select([proc.stdout, proc.stderr], [], [], 1)     # 阻塞最多1s。EOF也被linux认为有输出
        
        if proc.stdout in r:
            tmp_out = proc.stdout.read()
            outdata_l.append(tmp_out)
            if pflag:
                sys.stdout.write(tmp_out)
            
        if proc.stderr in r:
            tmp_err = proc.stderr.read()
            errdata_l.append(tmp_err)
            if pflag:
                sys.stdout.write(tmp_err)
        
        if ret is not None:
            # cmd结束
            break
        
    outdata = "".join(outdata_l)
    errdata = "".join(errdata_l)
        
    if ret != 0 and err_func:
        # cmd返回码不为0
        if errdata:
            err_func("Return %d when %s: %s\nError message: %s", ret, prompt, cmd, errdata)
        else:
            err_func("Return %d when %s: %s", ret, prompt, cmd)
        
    return ret, outdata, errdata


def _test_dpsystem():
    ret = dpsystem("echo '12345' > a.txt", loglevel="debug")
    print "ret:", ret
    ret = dpsystem("rm a.txt b.txt", loglevel="debug", prompt="Remove files")
    print "ret:", ret
    ret = dpsystem("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)  # cmd输出完，输出ret
    print "ret:", ret
    
def _test_dpsystem_output():
    ret = dpsystem("echo '12345' > a.txt", output=True, loglevel="debug")
    print "ret:", ret
    ret = dpsystem("rm a.txt b.txt", output=True, loglevel="debug", prompt="Remove files")
    print "ret:", ret
    ret = dpsystem("for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done", output=True, loglevel="info", pflag=True)  # cmd输出完，输出ret
    print "ret:", ret
    
def _test_dpsystem_async():
    ret = dpsystem_async("echo '12345' > a.txt", loglevel="debug")
    print "pid:", ret
    ret = dpsystem_async("rm a.txt b.txt", loglevel="debug", prompt="Remove files")
    print "pid:", ret
    ret = dpsystem_async("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)    # 先输出pid，后cmd输出
    print "pid:", ret

if __name__ == "__main__":
    dplog.set_sh_debug()
    
    print "="*4 + "test dpsystem" + "="*4
    _test_dpsystem()
    
    print
    print "="*4 + "test dpsystem_output" + "="*4
    _test_dpsystem_output()
    
    print
    print "="*4 + "test dpsystem_async" + "="*4
    _test_dpsystem_async()

