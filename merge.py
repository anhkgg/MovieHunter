#coding: utf8

import os, sys

def read_file(path):
    f = open(path, 'rb')
    data = f.read()
    f.close()
    return data

def copy(ts_list, path, name):
    dst_file = os.path.join(path, name+'.ts')
    dst_file = file(dst_file, 'wb')
    for ts in ts_list:
        ts_file = os.path.join(path, os.path.basename(ts))
        dst_file.write(read_file(ts_file))
        os.remove(ts_file)
    dst_file.close()

def copy1(path, name):
    list_file = os.path.join(path, 'ts_list.txt')
    ts_list = read_file(list_file)
    ts_list = ts_list.split('\n')

    #copy_list = '+'.join(os.path.basename(x) for x in ts_list)
    # print copy_list
    #cmd = "copy /B %s %s.ts" % (copy_list, name)
    #os.system(cmd)
    copy(ts_list, path, name)

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) < 2:
        print 'usage: lost.py dir'
    else:
        path = sys.argv[1]
        copy1(path, path)