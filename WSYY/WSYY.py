#！/usr/bin/env python3
# -*- coding:utf-8 -*-
import requests,time
from bs4 import BeautifulSoup

"""
无损音乐聚合搜索API
【说明】利用此API，您可以方便获得全网的免费无损音乐资源
    返回数据一般为百度网盘链接（包含链接与提取码），少部分资源为城通网盘资源
【作者】@LMR
【版本号】20190815
【更新说明】
0812 上线三个平台（wsyyxz.com、52flac.com、baiduonce.com）的聚合搜索
0813 新增一个平台（sq688.com）；支持全页码检索
0814 破解52flac.com的验证码获取问题
0815 新增一个平台（acgjc.com，填补acg音乐空白）；修复网盘链接错乱问题
"""
__author__='@LMR'

class WSYY(object):
    def __init__(self):
        pass

    #getList函数为获取搜索列表函数，返回字典数据，title为标题，url为关键链接（可传入getPAN获得网盘链接）
    def getList_1(self,inp):
        """获取搜索列表，来源：wsyyxz.com"""
        url="http://www.wsyyxz.com/e/search/index.php"
        #post数据包
        data={'tempid': '1',
              'classid': '1,2,3,4,5,6,7,8,9,10,11,12',
              'show': 'title,newstext,ftitle',
              'keyboard':inp,
              'Submit22': '搜索'}
        #此处注意，采用禁止重定向获取定向后url
        searchid=requests.post(url,data=data,allow_redirects=False).headers['Location']
        listpage=requests.get('http://www.wsyyxz.com/e/search/%s'%(searchid))
        soup=BeautifulSoup(listpage.text, "html.parser")
        listdata=[]
        #获取总页码数
        try:
            pagenum=int(int(soup.find('table',class_="list_page").find_all('b')[0].text)/20)+2
        except:
            pagenum=2
        #爬取网页
        for j in range(1,pagenum):
            if(j>1):
                listpage=requests.get('http://www.wsyyxz.com/e/search/%s&page=%d'%(searchid,j))
                soup=BeautifulSoup(listpage.text, "html.parser")
            #分析网页，读取结果
            for i in soup.find_all('a',class_='l'):
                listdata.append({'url':i['href'],'title':i.text})
        return listdata
    
    def getList_2(self,inp):
        """获取搜索列表，来源：52flac.com"""
        url="https://www.52flac.com/search.php?q=%s"%(inp)
        listpage=requests.get(url)
        soup=BeautifulSoup(listpage.text, "html.parser")
        listdata=[]
        #获取总页码数
        pagenum=len(soup.find('div',class_="pagebar").find_all('a'))
        if(pagenum==2):
            pagenum=3
        #爬取网页
        for j in range(1,pagenum-1):
            if(j>1):
                url="https://www.52flac.com/search.php?q=%s&page=%d"%(inp,j)
                listpage=requests.get(url)
                soup=BeautifulSoup(listpage.text, "html.parser")
            #分析网页，读取结果
            for i in soup.find_all('h2')[1:]:
                listdata.append({'url':i.a['href'],'title':i.text})
        return listdata

    def getList_3(self,inp):
        """获取搜索列表，来源：baiduonce.com"""
        url="http://www.baiduonce.com/s-%s-0"%(inp)
        listpage=requests.get(url)
        soup=BeautifulSoup(listpage.text, "html.parser")
        listdata=[]
        #获取总页码数
        pagenum=int(soup.find('td',class_='hidden-xs').find_all('b')[1].text)
        tnum=int(soup.find('td',class_='hidden-xs').find_all('b')[0].text)
        #爬取网页
        for j in range(1,pagenum+1):
            if(j>1):
                url="http://www.baiduonce.com/s-%s-0-10-%d-%d"%(inp,tnum,j)
                listpage=requests.get(url)
                soup=BeautifulSoup(listpage.text, "html.parser")
                #此处注意！！！本网站设置有间隔时间封锁，间隔时间为1s，考虑响应时间所以设置0.5s，如果追求保险可设置1s
                time.sleep(0.5)
            #分析网页，读取结果
            for i in soup.find_all('div',class_="aw-item active"):
                if(i.find('p',class_="aw-text-color-green").text.find('所属分类：MP3音乐')==-1):
                    listdata.append({'url':i.h1.a['href'],'title':i.h1.text})
        return listdata

    def getList_4(self,inp):
        """获取搜索列表，来源：sq688.com"""
        url="https://www.sq688.com/search.php?key=%s"%(inp)
        listpage=requests.get(url)
        soup=BeautifulSoup(listpage.text, "html.parser")
        #获取全部页码
        listdata=[]
        for i in range(1,len(soup.find('div',class_='pagewarp').find_all('a'))-1):
            #页面更新
            if(i>1):
                url="https://www.sq688.com/search.php?key=%s&page=%d"%(inp,i)
                listpage=requests.get(url)
                soup=BeautifulSoup(listpage.text, "html.parser")
            #获取信息
            for j in soup.find_all('tr')[1:]:
                title='%s-%s.%s'%(j.text.split("\n")[1],j.text.split("\n")[2],j.text.split("\n")[4])
                url=j.find('a',class_='st')['href']
                listdata.append({'url':url,'title':title})
        return listdata
    def getList_5(self,inp):
        """获取搜索列表，来源：acgjc.com"""
        url="http://www.acgjc.com/?s=%s"%(inp)
        listpage=requests.get(url)
        soup=BeautifulSoup(listpage.text, "html.parser")
        listdata=[]
        for j in range(1,len(soup.find_all('option'))+1):
            if(j>1):
                url="http://www.acgjc.com/page/%d/?s=%s"%(j,inp)
                listpage=requests.get(url)
                soup=BeautifulSoup(listpage.text, "html.parser")
            for i in soup.find_all('div' ,class_="card-bg"):
                if(i.text.find('ACG音乐')!=-1):
                    listdata.append({'url':i.a['href'],'title':i.a['title']})
        return listdata
            
        
    #getPAN函数获取网盘链接，返回text数据，包含链接与提取码
    def getPAN_1(self,url):
        """搜索页URL转百度网盘链接，来源：wsyyxz.com"""
        #第一层网页：文件描述页
        linkpage=requests.get(url)
        soup=BeautifulSoup(linkpage.content.decode("utf-8"), "html.parser")
        tmplink="http://www.wsyyxz.com/e/DownSys/DownSoft/?%s"%(
            soup.find('a',href="#ecms")['onclick'].split("'")[1].split('?')[1]
            )
        #提取提取码
        key=soup.find('div',style="text-align:center;").text.replace(" 密码: ","")
        #第二层网页：文件下载页
        downloadpage=requests.get(tmplink)
        soup=BeautifulSoup(downloadpage.text, "html.parser")
        downlink="http://www.wsyyxz.com/e/DownSys/%s"%(soup.find("a")['href']).split("/")[1]
        #重定向获取链接
        baidupan=requests.get(downlink,allow_redirects=False).headers['Location']
        return "链接: %s 提取码: %s"%(baidupan,key)

    def getPAN_2(self,url):
        """搜索页URL转百度网盘链接，来源：52flac.com"""
        link="https://www.52flac.com/download/%s"%(url.split("/")[-1])
        #注意这里有一个cookies设置，一个需要关注公众号获取的暗号，暂时是flac666
        linkpage=requests.get(link,cookies={'Nobird_DownLoad':'flac666'})
        #可以用下面这句检验暗号的正确与否
        """backnum=requests.post('https://www.52flac.com/zb_users/plugin/Nobird_DownLoad/do/do.php',data=
                          {'Nobird_DownLoad_password':'flac666','Nobird_DownLoad_PostID':url.split("/")[-1].split('.')[0]}).text.find('验证成功')
 """
        if(linkpage.text.find('验证码')!=-1):
            return {'link':'暂无法获取','key':'暂无法获取'}
        else:
            soup=BeautifulSoup(linkpage.text, "html.parser")
            res=soup.find_all('div',class_="con")[1].p.text
            return res       

    def getPAN_3(self,url):
        """搜索页URL转百度网盘链接，来源：baiduonce.com"""
        #第一层网页：文件描述页
        linkpage=requests.get("http://www.baiduonce.com%s"%(url))
        soup=BeautifulSoup(linkpage.content.decode("utf-8"), "html.parser")
        tmplink="http://www.baiduonce.com%s"%(soup.find('dl').a['href'])
        #获取提取码
        key=soup.find_all('dd')[1].text.replace("\n","")
        #第二层网页：文件下载页
        downloadpage=requests.get(tmplink)
        soup=BeautifulSoup(downloadpage.text, "html.parser")
        downlink="http://www.baiduonce.com%s"%(soup.find('div',class_="btnbox").a['href'])
        baidupan=requests.get(downlink,allow_redirects=False).headers['Location']
        return "链接: %s 提取码: %s"%(baidupan,key)

    def getPAN_4(self,url):
        """搜索页URL转百度网盘链接，来源：sq688.com"""
        #这个网页比较好爬，并且资源也比较多非常不错
        downloadpage=requests.get("https://www.sq688.com%s"%(url))
        soup=BeautifulSoup(downloadpage.text, "html.parser")
        res=soup.find('p',class_="downurl").text
        return res

    def getPAN_5(self,url):
        """搜索页URL转百度网盘链接，来源：baiduonce.com"""
        #第一层网页：文件描述页
        if(url.find('http://www.acgjc.com')==-1):
            url="http://www.acgjc.com%s"%(url)
        linkpage=requests.get(url)
        soup=BeautifulSoup(linkpage.text, "html.parser")
        #第二层网页：文件下载页
        link=soup.find_all('a',class_="meta meta-post-storage")[0]['href']
        if(link.find('http://www.acgjc.com')==-1):
            link="http://www.acgjc.com%s"%(link)
        downloadpage=requests.get(link)
        soup=BeautifulSoup(downloadpage.text, "html.parser")
        baidupan=soup.find('a',class_='btn btn-lg btn-success btn-block')['href']
        try:
            key=soup.find_all('input',class_="form-control pwd")[0]['value']
        except:
            key='无'
        try:
            extra=soup.find_all('input',class_="form-control pwd")[1]['value']
        except:
            extra='无' 
        return "【解压密码：%s】链接: %s 提取码: %s"%(extra,baidupan,key)

if __name__=="__main__":
    while(1):
        A=WSYY()
        a=A.getList_5(input("输入搜索词"))
        """
        for i in a:
            print(i)
            print("\n\n\n")"""
        print(A.getPAN_5(a[int(input("输入序号"))]['url']))
