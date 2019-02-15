#coding: utf8

import requests
import os, sys, time
import threading
import urlparse

import lost, merge, search

def utf2gbk(s):
    return s.decode('utf8').encode('gbk')

def save_file(path, data):
    f = open(path, 'wb')
    f.write(data)
    f.close()

def read_file(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data

def download_ts_file(url, path):
    try:
        req = requests.get(url)
        save_file(path, req.content)
        return True
    except Exception as e:
        return False

# https://www.cnblogs.com/huchong/p/8244279.html
class ThreadTaskCount(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(ThreadTaskCount, "_instance"):
            with ThreadTaskCount._instance_lock:
                if not hasattr(ThreadTaskCount, "_instance"):
                    ThreadTaskCount._instance = object.__new__(cls)  
        return ThreadTaskCount._instance

    _count_lock = threading.Lock()
    _count = 0
    _thread_list = []

    @classmethod
    def inc(self, t, n):
        ThreadTaskCount._count_lock.acquire()
        ThreadTaskCount._count += 1
        ThreadTaskCount._thread_list.append({'tid': t, 'n': n})
        ThreadTaskCount._count_lock.release()

    @classmethod
    def dec(self, t):
        ThreadTaskCount._count_lock.acquire()
        ThreadTaskCount._count -= 1
        for tt in ThreadTaskCount._thread_list:
            if tt['tid'] == t:
                ThreadTaskCount._thread_list.remove(tt)
                break
        ThreadTaskCount._count_lock.release()

    @classmethod
    def count(self):
        ThreadTaskCount._count_lock.acquire()
        count = ThreadTaskCount._count
        ThreadTaskCount._count_lock.release()
        return count

    @classmethod
    def join(self):
        for t in ThreadTaskCount._thread_list:
            t.join(2*60)

    @classmethod
    def printf(self):
        for t in ThreadTaskCount._thread_list:
            print t['tid'], t['n']

class MyThread(threading.Thread):
    def __init__(self, url_list, path):
        threading.Thread.__init__(self)
        self.url_list = url_list
        self.path = path

    def run(self):
        for url in self.url_list:
            path = os.path.join(self.path, os.path.basename(url))
            if os.path.exists(path):
                continue
            while not download_ts_file(url, path):
                time.sleep(10)
            #print '[+] Download %s success.' % url
        ThreadTaskCount().dec(self)

def download_thread(_url_list, path):
    url_list = list(_url_list)
    all_task = len(url_list)
    max_thread_count = 50
    pre_thread_task_count = 15
    thread_count = all_task / pre_thread_task_count

    '''
    for i in range(10):
        t = threading.Thread(target=task,args=[i,])
        t.start()
    '''
    # print "[+] thread_count = ", thread_count

    while True:
        if len(url_list) <= 0:
            break

        if ThreadTaskCount().count() < max_thread_count:
            ts_url = url_list.pop()
            t = MyThread([ts_url], path)
            ThreadTaskCount().inc(t, ts_url)
            t.setDaemon(True)
            t.start()
            #print '[+] start thread = ', ThreadTaskCount().count()
            print '.',
        time.sleep(0.01)

    print '\n[+] pop task Finish.'
    # ThreadTaskCount.join()

    pre_count = 0
    start_tm = 0
    start_tm_count = 0
    while ThreadTaskCount.count() > 0:
        if pre_count != ThreadTaskCount.count():
            pre_count = ThreadTaskCount.count()
            start_tm = time.time()
            start_tm_count = pre_count
            print '[+} Task %d is running.' % pre_count
        
        '''
        if ThreadTaskCount.count() < 10 and start_tm == 0:
            print '[+] Start calc timeout.', ThreadTaskCount.count(), time.ctime()
            start_tm = time.time()
            start_tm_count = ThreadTaskCount.count()
        '''
        if start_tm > 0 and (time.time() - start_tm > 5*60):
            print '[-] Task timeout...'
            ThreadTaskCount.printf()
            break

        time.sleep(1)

    print '[+] All task finish.'

def parse_m3mu5(url, name):
    result = urlparse.urlsplit(url)
    host = result.scheme +'://' + result.netloc + '/'
    urldir = os.path.dirname(url) + '/'
    urlname = os.path.basename(url)
    m3u8_file = os.path.join(name, urlname)

    data = ''
    if not os.path.exists(m3u8_file):
        req = requests.get(url)
        data = req.content
        save_file(m3u8_file, data)
    else:
        data = read_file(m3u8_file)

    m3u8_list = data.split('\n')
    m3u8_list = [ts for ts in m3u8_list if ts.find('.m3u8') != -1]

    if len(m3u8_list) <= 0:
        print data
        return ""

    m3u8 = m3u8_list[0]
    if m3u8.find('/') == -1:
        url = urlparse.urljoin(urldir, m3u8)
    else:
        url = urlparse.urljoin(host, m3u8)

    return url

def parse_ts_list(url, name):    
    result = urlparse.urlsplit(url)
    host = result.scheme +'://' + result.netloc + '/'
    urldir = os.path.dirname(url) + '/'
    urlname = os.path.basename(url)

    m3u8_file = os.path.join(name, urlname)
    
    data = ''
    if not os.path.exists(m3u8_file):
        req = requests.get(url)
        data = req.content
        save_file(m3u8_file, data)
    else:
        data = read_file(m3u8_file)

    ts_list = data.split('\n')
    ts_list = [ts for ts in ts_list if ts.find('.ts') != -1]

    ts_url_list = []

    for ts in ts_list:
        if ts.find('/') == -1:
            ts_url_list.append(urlparse.urljoin(urldir, ts))
        else:
            ts_url_list.append(urlparse.urljoin(host, ts))
            
    return ts_url_list

def download(url, name):
    try:
        print '[+] Start downloading ', name
        if not os.path.exists(name):
            os.mkdir(name)

        print '[+] start parse ts list...'

        ts_url_list = parse_ts_list(url, name)
        if len(ts_url_list) == 0:
            url = parse_m3mu5(url, name)
            if url == '':
                print utf2gbk('[-]解析m3u8失败')
                return
            ts_url_list = parse_ts_list(url, name)
            if len(ts_url_list) <= 0:
                print utf2gbk('[-]解析2次m3u8失败')
                return

        print '[+] start parse ts list finish. ', len(ts_url_list)
        # print ts_url_list[0]

        ts_list_file = os.path.join(name, 'ts_list.txt')
        save_file(ts_list_file, '\n'.join(ts_url_list))

        print '[+] start download ts file...'
        # download_ts_file(ts_url_list[0], os.path.join(name, os.path.basename(ts_url_list[0])))
        download_thread(ts_url_list, name)

        print '[+] Download ts file finish'

        lost_ts_url = lost.get_lost_file(ts_url_list, name)
        lost_cnt = 0
        while len(lost_ts_url) > 0:
            print '[+] lost some file: ', lost_ts_url
            if lost_cnt > 10:
                print '[-] Lost some ts file,repeat too many times, failed.'
                return
            time.sleep(10)
            download_thread(lost_ts_url, name)
            lost_cnt += 1

        print utf2gbk('[+] 开始合并...')
        #print len(ts_url_list)
        merge.copy(ts_url_list, name, name)
        print utf2gbk('[+] 完成')

    except Exception as e:
        print e

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print utf2gbk('usage: main.py 电影名')
    else:
        name = sys.argv[1]
        url = search.search(name)
        if url != None:
            print '[+] Find film url: ', url
            download(utf2gbk(url), name)
        else:
            print '[-] search %s failed' % name
    