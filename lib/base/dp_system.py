# -*- coding: GB18030 -*-

'''
@Created on Apr 24, 2014

@summary: �����е���
    - Bash�����е���
    - �й������е��õ�������������־��ͻ

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
    @summary: (����)����shell����cmd
    @attention: ���Ҫ��̨����������ʹ��dpsystem_async()
    
    @param output: 
     - ΪTrueʱ������cmd�� (return code, stdout output, stderr output)
     - ΪFalseʱ��ֻ����cmd��return code�������������ض���/dev/null
    
    @param loglevel: 
     - ����ΪNone, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - ��ΪNoneʱ��ִ�е�cmd��������־
    
    @param errlevel: 
     - ����ΪNone, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - ��ΪNoneʱ����cmd�����벻Ϊ0�����¼��־
    
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
    
    @param logger: log object��Ĭ��Ϊdplog
    
    @param prompt: ��־��ʾ��
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
    @summary: ��̨����shell����cmd
    
    @param loglevel: 
     - ����ΪNone, "debug", "info", "success", "warning", "diagnose", "error", "critical"
     - ��ΪNoneʱ��ִ�е�cmd��������־
     
    @param prompt: ��־��ʾ��
    
    @param pflag: print flag��ΪTrueʱ��ӡcmd����Ļ���
    
    @param logger: log object��Ĭ��Ϊdplog
    
    @return: ����cmd��pid
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
    '''@return: ����(return code, stdout output, stderr output)'''
    outdata_l = []
    errdata_l = []
    
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    # stderr�����ǵ�����PIPE
    
    # ��proc��stdout��stderr����Ϊ������
    for f in [proc.stdout, proc.stderr]:
        flags = fcntl.fcntl(f, fcntl.F_GETFL)
        fcntl.fcntl(f, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    
    while True:
        # ��ѯ
        ret = proc.poll()
        r, w, x = select.select([proc.stdout, proc.stderr], [], [], 1)     # �������1s��EOFҲ��linux��Ϊ�����
        
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
            # cmd����
            break
        
    outdata = "".join(outdata_l)
    errdata = "".join(errdata_l)
        
    if ret != 0 and err_func:
        # cmd�����벻Ϊ0
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
    ret = dpsystem("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)  # cmd����꣬���ret
    print "ret:", ret
    
def _test_dpsystem_output():
    ret = dpsystem("echo '12345' > a.txt", output=True, loglevel="debug")
    print "ret:", ret
    ret = dpsystem("rm a.txt b.txt", output=True, loglevel="debug", prompt="Remove files")
    print "ret:", ret
    ret = dpsystem("for ((i=0; i<8; i++)); do echo $i; echo 100$i >&2; sleep 0.5; done", output=True, loglevel="info", pflag=True)  # cmd����꣬���ret
    print "ret:", ret
    
def _test_dpsystem_async():
    ret = dpsystem_async("echo '12345' > a.txt", loglevel="debug")
    print "pid:", ret
    ret = dpsystem_async("rm a.txt b.txt", loglevel="debug", prompt="Remove files")
    print "pid:", ret
    ret = dpsystem_async("for ((i=0; i<8; i++)); do echo $i; sleep 0.5; done", loglevel="info", pflag=True)    # �����pid����cmd���
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

