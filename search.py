#coding: utf8

import requests, urllib
import os, sys, time
try:
    import json
except:
    import simplejson as json

def utf2gbk(s):
    return s.decode('utf8').encode('gbk')

def gbk2utf(s):
    return s.decode('gbk').encode('utf8')

def getdata(s, f1, f2):
    p = s.find(f1)
    if p == -1:
        return ''
    d = s[p + len(f1) :]
    p = d.find(f2)
    if p == -1:
        return d
    return d[:p]

def timestamp():
    return str(int(time.time()*1000))
    #1549945342314

def search(name):
    try:
        host = 'http://www.xxxxxx.com'
        url = 'http://www.xxxxxx.com/index.php?s=home-search-vod&q=' + urllib.quote(gbk2utf(name)) + '&limit=12&timestamp=' + timestamp()
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
            'Host': 'www.xxxxxx.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            }
        ret = requests.get(url)#, headers=headers)
        data = ret.content.replace('\\', '')
        data = json.loads(data)
        if data['status'] != 1:
            print utf2gbk(ret.content)
            return
        vod_url = host + data['data'][0]['vod_url']
        #print vod_url
        ret = requests.get(vod_url)
        data = ret.content
        player_list = data.split('player_list')
        if len(player_list) <= 1:
            print '[-] no palyer_list'
            return
        player_list = player_list[1]
        player_url = host + getdata(player_list, 'href="', '"')
        #print player_url
        ret = requests.get(player_url)
        data = ret.content
        data = getdata(data, 'zanpiancms_player = ', ';')
        data = json.loads(data)
        #print data
        url = data['url']
        return url
    except Exception as e:
        print e
        return

if __name__ == '__main__':
    print search(sys.argv[1])
    #print json.dumps('{"data":[{"vod_name":"流浪地球","vod_title":"HD1280高清国语","vod_url":"/kehuanpian/liulangdiqiu/"}],"info":"ok","status":1}')