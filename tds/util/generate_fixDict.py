# -*- coding: utf-8 -*-
__author__ = 'xujh'

import  re

globalFix2Line = {}
globalReplyMsgParam = {}
globalFunid2Name = {}
curfunid = None
curfunname = None

typeDict = {'BIGINT':'l', 'SMALLINT':'n','CHAR(1)':'c','INTEGER':'n','CMONEY':'d','CPRICE':'d',}

def getValue(subcontent):
    if subcontent in typeDict:
        return typeDict[subcontent]
    elif "VARCHAR" in subcontent:
        return  's,' + re.findall(r'\d+', subcontent)[0]

def processReplyMsgParam(line):
    if line.strip().isdigit():
        global curfunid
        curfunid = int(line.strip())
    elif len(line.strip().split('\t')) == 1 and len(line.strip()) > 0:
        global curfunname
        curfunname = line.strip()
        globalFunid2Name[curfunid] = curfunname
    else:
        content = line.strip().split('\t')
        if len(content) > 3 and content[3].isdigit():
            k = content[1]
            v = getValue(content[2])
            if not curfunid in globalReplyMsgParam:
                globalReplyMsgParam[curfunid] = { k : v }
            else:
                globalReplyMsgParam[curfunid][k] = v



def processFixDict(line):
    content = line.strip().split('\t')
    if len(content) > 3 and content[3].isdigit():
        fixidx = content[3].strip()
        py_line = 'fixDict["%s"] = c_char_p("%s")#%s\n' % (content[1].strip(), fixidx, content[0].strip())
        if not fixidx in  globalFix2Line:
            globalFix2Line[int(fixidx)] = [py_line,]
        elif fixidx in globalFix2Line and not py_line in globalFix2Line[fixidx]:
            globalFix2Line[int(fixidx)].append(py_line)

def process_line(line):
    if line == '\n' or len(line.strip()) == 0:
        return

    processFixDict(line)
    processReplyMsgParam(line)

def main():
    """主函数"""
    try:
        fcpp = open('maApi.txt','r')
        fpy = open('data_ty.py', 'w')

        fpy.write('# encoding: UTF-8\n')
        fpy.write('# auto generate by \n')
        fpy.write('\n')
        fpy.write('from ctypes import *\n')
        fpy.write('\n')
        fpy.write('fixDict = {}\n')
        fpy.write('\n')

        for line in fcpp:
            process_line(line)
        #     if py_line:
        #         fpy.write(py_line.decode('gbk').encode('utf-8'))

        for k in sorted(globalFix2Line.keys()):
            for py_line in globalFix2Line[k]:
                fpy.write(py_line.decode('gbk').encode('utf-8'))
        # for k,v in globalFix2Line.iteritems():
        #     for py_line in v:
        #         fpy.write(py_line.decode('gbk').encode('utf-8'))

        print globalReplyMsgParam
        print globalFunid2Name
        fcpp.close()
        fpy.close()

        print u'data_ty.py生成过程完成'
    except BaseException,e:
        print u'data_ty.py生成过程出错'
        print e


if __name__ == '__main__':
    main()
