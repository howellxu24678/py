# -*- coding: utf-8 -*-
__author__ = 'xujh'


globalFix2Line = {}
def process_line(line):

    if line == '\n':
        return

    content = line.split('\t')
    if content[3].isdigit() and len(content) > 3:
        fixidx = content[3]
        py_line = 'fixDict["%s"] = c_char_p("%s")#%s\n' % (content[1], fixidx, content[0])
        if not fixidx in  globalFix2Line:
            globalFix2Line[int(fixidx)] = [py_line,]
        elif fixidx in globalFix2Line and not py_line in globalFix2Line[fixidx]:
            globalFix2Line[int(fixidx)].append(py_line)


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

        # print globalFix2Line
        fcpp.close()
        fpy.close()

        print u'data_ty.py生成过程完成'
    except BaseException,e:
        print u'data_ty.py生成过程出错'
        print e


if __name__ == '__main__':
    main()
