# -*- coding: utf-8 -*-
__author__ = 'xujh'

import  re

globalFix2Line = {}
globalReplyMsgParam = {}
globalFunid2Name = {}
globalRequireFixIdx = {}
curfunid = None
curfunname = None

typeDict = {'BIGINT':'l', 'SMALLINT':'n','CHAR(1)':'c','INTEGER':'n','CMONEY':'d','CPRICE':'d',}

def getValue(subcontent):
    if subcontent in typeDict:
        return typeDict[subcontent]
    elif "VARCHAR" in subcontent or "CHAR" in subcontent:
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
            global  globalReplyMsgParam
            if not curfunid in globalReplyMsgParam:
                globalReplyMsgParam[curfunid] = { k : v }
            else:
                globalReplyMsgParam[curfunid][k] = v



def processFixDict(line):
    content = line.strip().split('\t')
    if len(content) > 3 and content[3].isdigit():
        fixidx = content[3].strip()
        py_line = 'fixDict["%s"] = c_char_p("%s")#%s\n' % (content[1].strip(), fixidx, content[0].strip())
        k = int(fixidx)
        global  globalFix2Line
        if not k in  globalFix2Line:
            globalFix2Line[k] = [py_line,]
        elif k in globalFix2Line and not py_line in globalFix2Line[k]:
            globalFix2Line[k].append(py_line)

def processInput(line):
    if line.strip().isdigit():
        global curfunid
        curfunid = int(line.strip())
    elif len(line.strip().split('\t')) == 1 and len(line.strip()) > 0:
        global curfunname
        curfunname = line.strip()
        globalFunid2Name[curfunid] = curfunname
    else:
        content = line.strip().split('\t')
        if len(content) > 4 and content[4].isdigit():
            fixidx = content[4].strip()
            py_line = 'fixDict["%s"] = c_char_p("%s")#%s\n' % (content[1].strip(), fixidx, content[0].strip())
            k = int(fixidx)
            global  globalFix2Line
            if not k in  globalFix2Line:
                globalFix2Line[k] = [py_line,]
            elif k in globalFix2Line and not py_line in globalFix2Line[k]:
                globalFix2Line[k].append(py_line)

            if content[3].strip().decode('gbk').encode('utf-8') == '√':
                global globalRequireFixIdx
                if not curfunid in globalRequireFixIdx:
                    globalRequireFixIdx[curfunid] = {content[1].strip() : None}
                else:
                    globalRequireFixIdx[curfunid][content[1].strip()] = None


def process_line(line):
    if line == '\n' or len(line.strip()) == 0:
        return

    if "#input#" in line:
        processInput(line.replace("#input#", ""))
    else:
        processFixDict(line)
        processReplyMsgParam(line)

def main():
    """主函数"""
    try:
        fcpp = open('maApi.txt','r')
        filepath = "../auto/data_type.py"
        fpy = open(filepath, 'w')

        fpy.write('# encoding: UTF-8\n')
        fpy.write('# auto generate by generate_fixDict.py\n')
        fpy.write('\n')
        fpy.write('from ctypes import *\n')
        fpy.write('\n')
        fpy.write('fixDict = {}\n')
        fpy.write('\n')

        for line in fcpp:
            process_line(line)

        for k in sorted(globalFix2Line.keys()):
            for py_line in globalFix2Line[k]:
                fpy.write(py_line.decode('gbk').encode('utf-8'))

        fpy.write('\n')
        fpy.write('\n')
        fpy.write('replyMsgParam = {}\n')
        for k in sorted(globalReplyMsgParam.keys()):
            to_write = '#%s\nreplyMsgParam["%s"] = {' % (globalFunid2Name[k],k)
            for k_inner in sorted(globalReplyMsgParam[k].keys()):
                to_write += "'%s': '%s',\n" % (k_inner, globalReplyMsgParam[k][k_inner])
                to_write += "                             "
            to_write += "}\n"
            fpy.write(to_write.decode('gbk').encode('utf-8'))


        fpy.write('\n')
        fpy.write('\n')
        fpy.write('funNameDict = {}\n')
        for k in sorted(globalFunid2Name.keys()):
            to_write = 'funNameDict["%s"] = u"%s"\n' % (k, globalFunid2Name[k])
            fpy.write(to_write.decode('gbk').encode('utf-8'))


        fpy.write('\n')
        fpy.write('\n')
        fpy.write('requireFixidxDict = {}\n')
        for k in sorted(globalRequireFixIdx.keys()):
            to_write = '#%s\nrequireFixidxDict["%s"] = {' % (globalFunid2Name[k],k)
            for k_inner in sorted(globalRequireFixIdx[k].keys()):
                to_write += "'%s': %s,\n" % (k_inner, globalRequireFixIdx[k][k_inner])
                to_write += "                                 "
            to_write += "}\n"
            fpy.write(to_write.decode('gbk').encode('utf-8'))

        fcpp.close()
        fpy.close()

        print u'%s生成过程完成'%filepath
    except BaseException,e:
        print u'%s生成过程出错'%filepath
        print e


if __name__ == '__main__':
    main()
