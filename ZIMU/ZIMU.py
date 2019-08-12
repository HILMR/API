#！/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
字幕库搜索下载API
版本号：20190726
"""

__author__='@LMR'

import requests
from bs4 import BeautifulSoup

#返回结果：电影名+字幕列表，字幕列表包含字幕标题、字幕ID、字幕评分以及总下载量
def getList(word):
    """获取字幕搜索结果，word为输入搜索词"""
    listpage=requests.get("http://www.zimuku.la/search",params={'q':word})
    soup=BeautifulSoup(listpage.text, "html.parser")
    sublist=[]
    for i in soup.find_all('div',class_='item prel clearfix'):
        keytmp={}
        sublink=[]
        keytmp['title']=i.find('p',class_='tt clearfix').b.text
        for j in i.find_all('tr'):
            kkeytmp={}
            try:
                kkeytmp['title']=j.find('a',target="_blank")['title']
                kkeytmp['linkid']=j.find('a',target="_blank")['href'].split('.')[0].split('/')[2]
                kkeytmp['rank']=j.find_all('div',class_="hidden-xs")[0].i['title'].split(":")[1]
                kkeytmp['dsum']=j.find_all('div',class_="hidden-xs")[1].text
                sublink.append(kkeytmp)
            except:
                pass
        keytmp['detail']=sublink
        sublist.append(keytmp)
    return sublist

def getLink(linkid,ch=0):
    """获取字幕下载地址，linkid为字幕ID号，ch为下载源，默认为电信0"""
    dpage=requests.get("http://www.zimuku.la/dld/%s.html"%(linkid))
    soup=BeautifulSoup(dpage.text, "html.parser")
    dlist=soup.find_all('a',rel="nofollow")
    Headers={'Host':'www.zimuku.la','Referer':'http://www.zimuku.la/dld/%s.html'%(linkid)}
    redir=requests.get("http://www.zimuku.la%s"%(dlist[ch]['href']),headers=Headers,allow_redirects=False)
    #获取下载链接需要注意：此处设置有重定向，重定向后的地址即为下载地址，重定向的发起方式需要headers，包含主机和源
    return redir.headers['Location']

def download(linkid,savepath,ch=0):
    """下载字幕，savepath为保存路径"""
    try:
        subtitle=requests.get(getLink(linkid,ch))
        with open(savepath+'/'+subtitle.headers['content-disposition'].split('"')[1],'wb') as f:
            f.write(subtitle.content)
        return subtitle.headers['content-disposition'].split('"')[1]
    except:
        return False

if __name__=="__main__":
    while(1):
        print(getList(input("输入搜索词")))
        #download('120956','E:')
