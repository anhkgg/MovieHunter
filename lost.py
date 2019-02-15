#coding: utf8

import os, sys

def read_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data
    
def get_lost_file(ts_list, path):
    lost_file = []
    for ts in ts_list:
        ts_file = os.path.join(path, os.path.basename(ts))
        if not os.path.exists(ts_file):
            lost_file.append(ts)
    return lost_file

def get_lost_file1(path):
    list_file = os.path.join(path, 'ts_list.txt')
    ts_list = read_file(list_file)
    ts_list = ts_list.split('\n')
    get_lost_file(ts_list, path)

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) < 2:
        print 'usage: lost.py dir'
    else:
        path = sys.argv[1]
        print get_lost_file(path)
    