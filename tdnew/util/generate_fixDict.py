# -*- coding: utf-8 -*-
__author__ = 'xujh'

import re

globalFix2Line = {}
globalReplyMsgParam = {}
globalFunid2Name = {}
globalRequireFixCol = {}
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
                global globalRequireFixCol
                if not curfunid in globalRequireFixCol:
                    globalRequireFixCol[curfunid] = {content[1].strip() : None}
                else:
                    globalRequireFixCol[curfunid][content[1].strip()] = None


def process_mapi_line(line):
    if line == '\n' or len(line.strip()) == 0:
        return

    if "#input#" in line:
        processInput(line.replace("#input#", ""))
    else:
        processFixDict(line)
        processReplyMsgParam(line)

#字典定义：globaldefineDict['ORDER_STATUS'] = {'0': u'未报'...}
globaldefineDict = {}
#字典注释：ORDER_STATUS -》2.2.12委托状态【ORDER_STATUS】
defineDictNote = {}
curdict = None
def process_madict_line(line):
    if line == '\n' or len(line.strip()) == 0:
        return
    global curdict
    content = line.strip().split('\t')
    if len(content) >= 2 and re.match(r'\d.\d.\d', content[0]):

        curdict = re.findall(r'\w+', content[1].strip())[0]
        defineDictNote[curdict] = content[0].strip() + content[1].strip()
    elif len(content) >= 2 and content[0].strip().isalnum():
        if not curdict in globaldefineDict:
            globaldefineDict[curdict] = {content[0].strip(): content[1].strip()}
        else:
            globaldefineDict[curdict][content[0].strip()] = content[1].strip()


def main():
    """主函数"""
    try:
        filepath = "../auto/data_type.py"
        fpy = open(filepath, 'w')

        fpy.write('# -*- coding: utf-8 -*-\n')
        fpy.write('# auto generate by generate_fixDict.py\n')
        fpy.write('\n')
        fpy.write('from ctypes import *\n')
        fpy.write('\n')
        fpy.write('fixDict = {}\n')
        fpy.write('\n')

        fmapi = open('maApi.txt','r')
        for line in fmapi:
            process_mapi_line(line)

        for k in sorted(globalFix2Line.keys()):
            for py_line in globalFix2Line[k]:
                fpy.write(py_line.decode('gbk').encode('utf-8'))

        fpy.write('\n')
        fpy.write('\n')
        fpy.write('replyMsgParam = {}\n')
        for k in sorted(globalReplyMsgParam.keys()):
            to_write = '#%s\nreplyMsgParam["%s"] = {\n' % (globalFunid2Name[k],k)
            for k_inner in sorted(globalReplyMsgParam[k].keys()):
                to_write += "    '%s': '%s',\n" % (k_inner, globalReplyMsgParam[k][k_inner])
                #to_write += "                             "
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
        fpy.write('requireFixColDict = {}\n')
        for k in sorted(globalRequireFixCol.keys()):
            to_write = '#%s\nrequireFixColDict["%s"] = {\n' % (globalFunid2Name[k],k)
            for k_inner in sorted(globalRequireFixCol[k].keys()):
                to_write += "    '%s': %s,\n" % (k_inner, globalRequireFixCol[k][k_inner])
                #to_write += "                                 "
            to_write += "}\n"
            fpy.write(to_write.decode('gbk').encode('utf-8'))


        fpy.write('\n')
        fpy.write('\n')
        fpy.write('defineDict = {}\n')
        fdict = open('maDict.txt','r')
        for line in fdict:
            process_madict_line(line)

        for k in sorted(globaldefineDict.keys()):
            to_write = '#%s\ndefineDict["%s"] = {\n' % (defineDictNote[k], k)
            for k_inner in sorted(globaldefineDict[k].keys()):
                to_write += "    '%s': u'%s',\n" % (k_inner, globaldefineDict[k][k_inner])
                #to_write += "                              "
            to_write += "}\n"
            fpy.write(to_write.decode('gbk').encode('utf-8'))


        fmapi.close()
        fdict.close()
        fpy.close()

        print u'%s生成过程完成'%filepath
    except BaseException,e:
        print u'%s生成过程出错'%filepath
        print e

if __name__ == '__main__':
    main()
