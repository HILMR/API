#！/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
BJUT网关相关的API
版本号：20190920
"""
__author__='@LMR'

import requests,sys
from bs4 import BeautifulSoup

#以下是网关登陆API
def results(back):
    if(back.find('登录成功窗')!=-1):
        return '登陆成功'
    elif(back.find('ldap auth error')!=-1):
        return '账号密码错误'
    elif(back.find('IP conflict !')!=-1):
        return 'IP冲突，通过强制下线可解决'
    elif(back.find('userid error1')!=-1):
        return '用户ID错误，检查拼写'
    elif(back.find('Msg=14')!=-1):
        return '注销成功'
    elif(back.find('Logout Error(-1)')!=-1):
        return '注销失败'
    else:
        return '未知错误'

def getnowinf(typ):
    """获取lgn网站的实时信息，包括在线状态、流量消耗、余额"""
    if(typ==4):
        try:
            a=requests.get("https://lgn.bjut.edu.cn/",timeout=2).content.decode("gb2312")
        except:
            return False
    elif(typ==6):
        try:
            a=requests.get("https://lgn6.bjut.edu.cn/",timeout=2).content.decode("gb2312")
        except:
            return False
    elif(typ==46):
        try:
            a=requests.get("https://lgn.bjut.edu.cn/",timeout=2).content.decode("gb2312")
            a=requests.get("https://lgn6.bjut.edu.cn/",timeout=2).content.decode("gb2312")
        except:
            return False
    
    if(a.find("您已登陆")!=-1):
        sta1=a.find("flow='")
        usedflow=int(a[sta1+6:a.find(" ",sta1)])
        sta2=a.find("fee='")
        leftmoney=int(a[sta2+5:a.find(" ",sta2)])
        return {'usedflow':usedflow/1024,'leftmoney':leftmoney/10000}
    else:
        return False
   
def wlanlogin(name,password):
    """WLAN登陆，name为学号，password为密码"""
    data={
        'DDDDD': name,
        'upass': password,
        '6MKKey':'%B5%C7%C2%BC+Login'}
    try:
        back=requests.post("https://wlgn.bjut.edu.cn/",data=data,timeout=5).text
        return results(back)
    except:
        return '网络错误'

def login(name,password,Type):
    """IPV6登陆，name为学号，password为密码,Type为ipv4/6选择"""
    msg=''
    if(Type==4):
        try:
            requests.get("https://wlgn.bjut.edu.cn/",timeout=1)
            return wlanlogin(name,password)
        except:
            url="https://lgn.bjut.edu.cn/"
    elif(Type==6):
        url="https://lgn6.bjut.edu.cn/"
    elif(Type==46):
        msg='ipv4:'+login(name,password,4)+'|ipv6:'
        url="https://lgn6.bjut.edu.cn/"
    else:
        url="https://lgn.bjut.edu.cn/"
    data={
    'DDDDD': name,
    'upass': password,
    'v46s': '2','v6ip': '','f4serip': '172.30.201.2','0MKKey':'' }
    try:
        back=requests.post(url,data=data,timeout=5).content.decode("gb2312")
        return msg+results(back)
    except:
        return '网络错误'

def logout(Type):
    """注销"""
    try:
        if(Type==4):
            try:
                return results(requests.get("https://wlgn.bjut.edu.cn/F.htm",timeout=1).text)
            except:
                return results(requests.get("https://lgn.bjut.edu.cn/F.htm",timeout=5).text)
        elif(Type==6):
            return results(requests.get("https://lgn6.bjut.edu.cn/F.htm",timeout=5).text)
        elif(Type==46):
            return 'ipv4:'+logout(4)+'|ipv6:'+logout(6)
    except:
        return '网络错误'
        
#以下是网关账户管理API
def managelogin(name,password):
    """网关账户管理登陆，name为学号，password为密码"""
    try:
        A=requests.Session()#新建一个会话，储存cookies（决定性的是JSESSIONID）
        getCK=A.get('https://jfself.bjut.edu.cn/nav_login',timeout=2).text#get一次网页获取验证码
        checkcode=getCK[getCK.find('checkcode=')+11:getCK.find('"',getCK.find('checkcode=')+11)]#提取验证码
        #这个有点坑，jfself这个网页，checkcode是直接展示在网页中了，但是如果输入错误太多就会启动图片验证码就是code
        #因此需要get一下这个网页把code生成，虽然最后post的时候不用，但是没有这个信息，会始终报错
        A.get('https://jfself.bjut.edu.cn/RandomCodeAction.action?randomNum=0.1',timeout=2)
        #所需的数据
        postdata={
            'account': name,
            'password': password,
            'code': '',
            'checkcode': checkcode,
            'Submit': '登 录'}
        B=A.post("https://jfself.bjut.edu.cn/LoginAction.action",timeout=2,data=postdata,headers={'Host': 'jfself.bjut.edu.cn'})
        if(B.text.find("登 录")==-1):
            return A#返回session会话，后面直接调用就行
        else:
            return False
    except:
        return '网络错误'

def getinf(session):
    """获取网关账户信息，session为登陆会话"""
    B=session.get("https://jfself.bjut.edu.cn/nav_getUserInfo")
    soup=BeautifulSoup(B.text, "html.parser")
    leftmoney=soup.find_all('td', class_="t_r1")[0].text.replace("\r","").replace("\n","").replace("\t","").replace("\xa0","")
    usedflow=soup.find_all('td', class_="t_r1")[2].text.replace("\r","").replace("\n","").replace("\t","").replace("\xa0","")
    costmoney=soup.find_all('td', class_="t_r1")[3].text.replace("\r","").replace("\n","").replace("\t","").replace("\xa0","")
    service=session.get("https://jfself.bjut.edu.cn/refreshaccount?t=0").json()['note']['service']
    return {'leftmoney':leftmoney,
            'usedflow':usedflow,
            'costmoney':costmoney,
            'service':service}
            

def getoffid(session):
    """获取在线账户信息，session为登陆会话"""
    B=session.get("https://jfself.bjut.edu.cn/nav_offLine")
    soup=BeautifulSoup(B.text, "html.parser")
    backlist=[[j.text.replace('\xa0','') for j in i.find_all('td')] for i in soup.find_all('tr')]
    backlist[0]=[j.text.replace('\xa0','') for j in soup.find_all('tr')[0].find_all('th')]
    return backlist

def dooffid(session,offid):
    """强制下线用户，offid为获取到的id值"""
    B=session.get('https://jfself.bjut.edu.cn/tooffline?t=0.7536954024209961&fldsessionid=%s'%(offid))
    
def getlog(session,start,end):
    """获取上网日志，session为登陆会话，start为日期开始日XXXX-XX-XX，end为日期结束日XXXX-XX-XX"""
    B=session.get("https://jfself.bjut.edu.cn/UserLoginLogAction.action?type=4&startDate=%s&endDate=%s"%(start,end))
    soup=BeautifulSoup(B.text, "html.parser")
    backlist=[[j.text.replace('\r','').replace('\n','').replace('\t','') for j in i.find_all('td')] for i in soup.find('table', class_="display").find_all('tr')]
    backlist[0]=[j.text for j in soup.find('table', class_="display").find_all('tr')[0].find_all('th')]
    return backlist

def getmacs(session):
    """获取绑定的mac地址，session为登陆会话"""
    B=session.get("https://jfself.bjut.edu.cn/nav_unBandMacJsp")
    soup=BeautifulSoup(B.text, "html.parser")
    return [i['value'] for i in soup.find_all('input',attrs={'name':"macs"})]

def domacs(session,mac):
    """提交mac地址，session为登陆会话，mac为MAC地址"""
    session.post('https://jfself.bjut.edu.cn/nav_unbindMACAction.action',data={'macStr':mac,'Submit': '提交'})

if __name__=="__main__":
    inf="""
对BJUT的网关进行登陆、注销、管理
使用方法：
    <lgn.py路径> <命令> [参数]
命令：
    i 登录网关，参数包含：[用户名,密码,登录方式(4为ipv4，6为ipv6，46为ipv4和6)]
    o 注销网关，参数包含：[注销方式(4为ipv4，6为ipv6，46为ipv4和6)]
"""


    try:
        if(sys.argv[1]=='i'):
            print(login(sys.argv[2],sys.argv[3],int(sys.argv[4])))
        elif(sys.argv[1]=='o'):
            print(logout(int(sys.argv[2])))
    except:
        print(inf)
        exit()
        
