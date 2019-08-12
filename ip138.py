#！/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
ip138 IP/手机号归属查询API
版本号：20190728
警告：仅供学习交流！
"""

__author__='@LMR'

import requests
from bs4 import BeautifulSoup

class ip138(object):
    def __init__(self):
        self.Headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Mobile Safari/537.36'}
        #本网站无headers则禁止访问
    def selfip(self):
        """返回本机IP地址"""
        page=requests.get("http://200019.ip138.com/",headers=self.Headers)
        soup=BeautifulSoup(page.text,'html.parser')
        return soup.title.text.split('：')[1]
        
    def ip(self,inp):
        """ip查询模块，
返回数据List，[本站数据,参考数据1,参考数据2,兼容IPv6地址,映射IPv6地址]"""
        try:
            page=requests.get("http://www.ip138.com/ips138.asp",params={'ip':inp},headers=self.Headers)
            soup=BeautifulSoup(page.content.decode("gbk"),'html.parser')
            res=[]
            for i in soup.find('ul',class_='ul1').find_all("li"):
                res.append(i.text.split('：')[1].replace(" ",""))
            return res
        except:
            return 'error'
    def mobile(self,inp):
        """手机归属地查询模块，返回数据List，[归属地,卡类型]"""
        try:
            page=requests.get("http://www.ip138.com:8080/search.asp",params={'action':'mobile','mobile':inp},headers=self.Headers)
            soup=BeautifulSoup(page.content.decode("gbk"),'html.parser')
            data=soup.find_all('td',class_='tdc2')
            return [data[1].text.replace('\xa0',''),data[2].text]
        except:
            return 'error'


if __name__=="__main__":
    A=ip138()
    while(1):
        inp=input("请输入待查询的IP地址或手机号（段）")
        if(inp.find(".")!=-1):
            print(A.ip(inp))
        elif(inp!=''):
            print(A.mobile(inp))
        else:
            print(A.selfip())
    
