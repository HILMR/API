#！/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
网关助手
"""
__author__='@LMR'
__version__='1.6.1'
__update__="""
v1.0 20190913上线
v1.1 加入多线程数据读取
v1.2 提升悬浮窗流畅度
v1.3 20190917
新增多用户管理、屏幕贴附以及专业模式和精简模式的鼠标手势
v1.4 20190919
新增设置系统、提示UI美观度，兼容WIN7系统，加入开机自动启动功能
v1.4.1 修复开机启动变量出错
v1.5.0 加入防掉线以及风险登陆设备自动拦截功能，修复程序名变更无法开机自启的BUG
v1.5.1 修复研究生流量套餐识别错误
20190922上线
v1.6.0 可以为您的设备自定义命名，风险检测可以选择不显示相似网段的登录
v1.6.1 更换icon，修复有线网络MAC地址信任的BUG，修复流量报警设置逻辑的BUG
"""
__tips__=['悬浮窗模式可以通过ESC键返回主界面',
          '晃动悬浮窗可以快速进入专业模式',
          '将悬浮窗移动至屏幕上边缘会自动吸附',
          '鼠标移动至流量或金额条可显示详细信息',
          '单击流量或金额条可切换显示内容',
          '自动登陆+开机自启从此不再输入密码'
          ]
    
#第三方库导入
from tkinter import *
from tkinter import ttk
import configparser
import random,time,json,sys,os
import subprocess
import threading
import win32api
import win32con
from lgn import *
from exDialog import *
from icon import *
#建立主窗口
root=Tk()
root.title('请登陆你的网关账号-BJUT网关助手%s'%(__version__))
root.geometry("500x200")
showicon(root)
#写入配置文件的全局变量
name= StringVar()#用户名
namelist=[]#多用户列表
namechange=0#用户改变标记
namelast=''#上次成功登录的用户
key= StringVar()#密钥
typ = IntVar()#ipv4/6类型，0为ipv4.1为ipv4+6
auto = IntVar()#自动登陆，1启动
pro = IntVar()#专业模式，1启动
dev = IntVar()#新设备授权，0启动
sdev = IntVar()#非信任设备自动下线
fsty=IntVar()#流量提醒模式
msty=IntVar()#余额提醒模式
fn=IntVar()#流量超额提醒
sfn=IntVar()#流量超额下线
lout=IntVar()#自动注销
lin=IntVar()#防掉线模式
fret=IntVar()#刷新频率
bzm=IntVar()#刷新频率
sam=IntVar()#相似网段
macbz={}
saflist={}#信任列表储存


#临时全局变量
choo= StringVar()#流量统计项目
flowper=1
moneyper=1
ipv4state='#00FA9A'
ipv6state='#00FA9A'
count=[]#在线设备列表
fs2=0
moneytext=['','']
flowtext=['','']
sup=IntVar()#开机自启
sels=['','','']

#窗口退出后自动注销功能
def rootend():
    root.withdraw()
    if(lout.get()==1):
        logout(46)
    root.destroy()
        
root.protocol("WM_DELETE_WINDOW", rootend)

def updateurl(url):
    import webbrowser
    webbrowser.open(url)

def getnewversion():
    try:
        A=requests.get("https://github.com/HILMR/API/blob/master/BJUTLAN/version",timeout=10).text
        ver=A[A.find("=",A.find("#version"))+1:A.find(";",A.find("#version"))]
        oldver=int(__version__.replace(".",""))
        uplog=A[A.find("=",A.find("#uplog"))+1:A.find(";",A.find("#uplog"))].replace("\\n","\n")
        upurl=A[A.find("=",A.find("#upurl"))+1:A.find(";",A.find("#upurl"))]
        if(int(ver.replace(".",""))>oldver):
            exDialog(root).notice("新版本%s更新"%(ver),"%s"%(uplog),10000,[updateurl,upurl])
    except:
        print("error")
        pass

threading.Thread(target=getnewversion,args=()).start()

def sign(inp,typ):
    """密钥生成函数，inp为输入明文，typ为0时为加密，1时为解密，函数返回暗文密钥"""
    out=''
    if(typ==0):
        for i in inp:
            a=random.randint(1,9)
            b=random.randint(1,99)
            out=out+str(ord(i)*a+b)+' '+str(a)+' '+str(b)+' '
    else:
        tmp=inp.split(' ')
        for i in range(0,int(len(tmp)/3)):
            a=int(tmp[i*3+1])
            b=int(tmp[i*3+2])
            out=out+chr(int((int(tmp[i*3])-b)/a))
    return out

def color(inp,*keyframes):
    """RGB全彩插补函数，inp为百分比，keyframes为RGB关键帧"""
    #处理非正常输入
    if(len(keyframes)==0):
        return False
    elif(len(keyframes)==1):
        keyframes=keyframes+keyframes
    back='#'
    #RGB遍历
    for i in range(0,3):
        now=len(keyframes)-2
        #判断区段
        for j in range(0,len(keyframes)):
            if((inp*(len(keyframes)-1))>=j):
                continue
            now=j-1
            break
        #插补
        if(keyframes[now][i]<keyframes[now+1][i]):
            tmp=str(hex(int(keyframes[now][i]+(inp*(len(keyframes)-1)-now)*abs(keyframes[now+1][i]-keyframes[now][i]))))
            if(len(tmp)==3):
                back+='0%s'%(tmp)
            else:
                back+=tmp
        else:
            tmp=str(hex(int(keyframes[now][i]-(inp*(len(keyframes)-1)-now)*abs(keyframes[now+1][i]-keyframes[now][i]))))
            if(len(tmp)==3):
                back+='0%s'%(tmp)
            else:
                back+=tmp
    return back.replace("0x","")

def writeini():
    """写入配置文件"""
    #config.remove_section(
    a=configparser.ConfigParser()
    a.read("%s/login.ini"%(os.path.split(sys.argv[0])[0]))
    try:
        a.add_section("GLOBAL")
    except:
        pass
    a.set("GLOBAL", "namelist",json.dumps(namelist))
    a.set("GLOBAL", "namelast",str(namelast))
    try:
        a.add_section(name.get())
    except:
        pass
    a.set(name.get(), "typ", str(typ.get()))
    a.set(name.get(), "auto", str(auto.get()))
    a.set(name.get(), "pro", str(pro.get()))
    a.set(name.get(), "dev", str(dev.get()))
    a.set(name.get(), "fsty", str(fsty.get()))
    a.set(name.get(), "msty", str(msty.get()))
    a.set(name.get(), "fn", str(fn.get()))
    a.set(name.get(), "sfn", str(sfn.get()))
    a.set(name.get(), "lout", str(lout.get()))
    a.set(name.get(), "lin", str(lin.get()))
    a.set(name.get(), "sdev", str(sdev.get()))
    a.set(name.get(), "fret", str(fret.get()))
    a.set(name.get(), "bzm", str(bzm.get()))
    a.set(name.get(), "sam", str(sam.get()))
    a.set(name.get(), "macbz", json.dumps(macbz))
    a.set(name.get(), "saflist", json.dumps(saflist))
    if(auto.get()==1):
        a.set(name.get(), "key",sign(key.get(),0))
    with open("%s/login.ini"%(os.path.split(sys.argv[0])[0]),"w") as f:
        a.write(f)

def readini(*ty):
    """读取配置文件"""
    global saflist,macbz,namelist,namechange
    try:
        a=configparser.ConfigParser()
        a.read("%s/login.ini"%(os.path.split(sys.argv[0])[0]))
        namelist=json.loads(a.get("GLOBAL","namelist"))
        if(len(ty)!=0):
            namechange=1
        else:
            if(name.get()==''):
                name.set(a.get("GLOBAL","namelast"))
        typ.set(int(a.get(name.get(),"typ")))
        auto.set(int(a.get(name.get(),"auto")))
        pro.set(int(a.get(name.get(),"pro")))
        dev.set(int(a.get(name.get(),"dev")))
        fsty.set(int(a.get(name.get(),"fsty")))
        msty.set(int(a.get(name.get(),"msty")))
        fn.set(int(a.get(name.get(),"fn")))
        sfn.set(int(a.get(name.get(),"sfn")))
        lout.set(int(a.get(name.get(),"lout")))
        lin.set(int(a.get(name.get(),"lin")))
        sdev.set(int(a.get(name.get(),"sdev")))
        fret.set(int(a.get(name.get(),"fret")))
        bzm.set(int(a.get(name.get(),"bzm")))
        sam.set(int(a.get(name.get(),"sam")))
        saflist=json.loads(a.get(name.get(),"saflist"))
        macbz=json.loads(a.get(name.get(),"macbz"))
        if(auto.get()==1):
            key.set(sign(a.get(name.get(),"key"),1))
        else:
            key.set('')
    except:
        typ.set(0)
        auto.set(0)
        pro.set(0)
        dev.set(0)
        fsty.set(0)
        msty.set(0)
        fn.set(0)
        sfn.set(0)
        lout.set(0)
        lin.set(1)
        sdev.set(0)
        fret.set(5000)
        bzm.set(1)
        sam.set(1)

#############################################################################################
#
#                                            精简模式
#
#############################################################################################
getdata_state=True
def getdata():
    """数据更新函数，线程使用"""
    global flowper,moneyper,ipv4state,ipv6state,count,moneytext,flowtext
    #注意信息更新的时效性，通过getinf更新的数据不是即时数据，因此需要使用getnowinf，同时能够确认是否在线
    data1=getnowinf(4)
    data2=getnowinf(6)
    data3=getinf(session)#获取信息
    
    if((data3['service']=='专科生、本科生默认套餐')or(data3['service']=='硕士生默认套餐')or(data3['service']=='博士生默认套餐')):
        flowtotal=12288
    elif((data3['service']=='专科生、本科生20元套餐')or(data3['service']=='硕士生20元套餐')or(data3['service']=='博士生20元套餐')):
        flowtotal=25600
    elif((data3['service']=='专科生、本科生25元套餐')or(data3['service']=='硕士生25元套餐')or(data3['service']=='博士生25元套餐')):
        flowtotal=30720
    else:
        flowtotal=12288

     #在线检查
    if(data1!=False):
        ipv4state='#00FA9A'
        data=data1
    else:
        data=None
        ipv4state='#FF1493'
    if(data2!=False):
        ipv6state='#00FA9A'
    else:
        ipv6state='#FF1493'

    if(data!=None):
        flowper=float(data['usedflow'])/flowtotal#计算流量百分比
        if(flowper>1):
            flowper=1#防出错处理
        #流量提示语1
        if(float(data['usedflow'])>1024):
           flowtext=['消耗流量\t免费额度\n%.2fGB\t%dGB'%(float(data['usedflow'])/1024,flowtotal/1024)]
        else:
           flowtext=['消耗流量\t额度\n%.1fMB\t%dfGB'%(float(data['usedflow']),flowtotal/1024)]
        #流量提示语2
        if(abs((flowtotal-float(data['usedflow'])))>1024):
           flowtext.append('剩余流量\t免费额度\n%.2fGB\t%dGB'%(flowtotal/1024-float(data['usedflow'])/1024,flowtotal/1024))
        else:
           flowtext.append('剩余流量\t免费额度\n%.1fMB\t%dGB'%(flowtotal-float(data['usedflow']),flowtotal/1024))
           
        #计算金额百分比
        if((float(data['leftmoney'])+float(data3['costmoney']))==0):
            moneyper=1
        else:
            moneyper=float(data3['costmoney'])/(float(data['leftmoney'])+float(data3['costmoney']))
            if(moneyper>1):
                moneyper=1
        #余额提示
        moneytext=[
            '余额\t消耗\n%.1f元\t%.1f元'%(float(data['leftmoney']),float(data3['costmoney'])),
            '预计可补充流量\n%.1fGB'%(float(data['leftmoney'])/2)
            ]
   

    #设备登陆许可
    if((dev.get()==1)and(count!=[])and(sdev.get()==0)):
        new=getoffid(session)[1:]
        for i in new:
            if(i[0].find('.')!=-1):
                flag=0
                #检查IP是否在已有列表中，如果无则为新增设备
                for j in count:
                    if(j[0]==i[0]):
                        flag=1
                        break
                if(flag==0):
                    global getdata_state
                    getdata_state=False
                    if(i[2] in macbz):
                        back=exDialog(root).msgbox('有新设备登录','设备:%s\n是否允许登录？'%(macbz[i[2]]),1,[500,200,int(root.winfo_screenwidth()/2-250),0])
                    else:
                        back=exDialog(root).msgbox('有新设备登录','设备IP:%s\n是否允许登录？'%(i[0]),1,[500,200,int(root.winfo_screenwidth()/2-250),0])
                    if(back==False):
                        dooffid(session,i[3])
                        time.sleep(2)
                        getdata_state=True
    if(sdev.get()==1):
        new=getoffid(session)[1:]
        for i in new:
            if(i[0].find('.')!=-1):
                flag=0
                #检查IP是否在信任列表中，如果无则为新增设备
                for j in saflist:
                    #检查MAC匹配，如果MAC匹配则不检查IP
                    if(saflist[j][0]==i[2]):
                        flag=1
                        break
                    #检查IP匹配
                    elif(j==i[0]):
                        flag=1
                        break
                if(flag==0):
                    getdata_state=False
                    dooffid(session,i[3])
                    exDialog(root).notice("设备拦截","已拦截：[IP]%s\n[MAC]%s"%(i[0],i[2]),5000)
                    time.sleep(2)
                    getdata_state=True
                        

    count=[]
    for i in getoffid(session):
        if(i[0].find('.')!=-1):
            count.append([i[0],i[3],i[2]])

#流量监控小窗事件
leapm=[0,0,0,0]
def move(event,top):
    """拖动事件"""
    #屏幕边缘磁贴功能
    if(((event.x_root-xy[0]+top.winfo_width())>(top.winfo_screenwidth()-30))and((event.y_root-xy[1])<30)):
        top.geometry("%dx%d+%d+%d"%(top.winfo_width(),top.winfo_height(),top.winfo_screenwidth()-top.winfo_width(),0))
    elif(((event.x_root-xy[0])<30)and((event.y_root-xy[1])<30)):
        top.geometry("%dx%d+%d+%d"%(top.winfo_width(),top.winfo_height(),0,0))
    elif((event.y_root-xy[1])<30):
        top.geometry("%dx%d+%d+%d"%(top.winfo_width(),top.winfo_height(),event.x_root-xy[0],0))
    else:
        top.geometry("%dx%d+%d+%d"%(top.winfo_width(),top.winfo_height(),event.x_root-xy[0],event.y_root-xy[1]))
    #鼠标手势检测
    delta=event.x_root-leapm[2]
    if(leapm[2]!=0):
        leapm[1]+=delta
    leapm[2]=event.x_root
    if((leapm[0]==0)and(delta<=0)):
        leapm[1]=0
    if((leapm[0]==0)and(leapm[1]>200)):
        leapm[0]=1
        leapm[1]=0
        leapm[3]=time.time()
    if((leapm[0]==1)and(delta>=0)):
        leapm[1]=0
    if((leapm[0]==1)and(leapm[1]<-200)):
        leapm[0]=0
        leapm[1]=0
        if((time.time()-leapm[3])<0.5):
            top.destroy()
            pro.set(1)
            Login(1)

def end(event,top):
    """结束窗体"""
    global count
    count=[]
    root.deiconify()
    top.destroy()

def moves(event,top,lab):
    """单击移动事件"""
    global xy#定义全局变量
    xy=[event.x,event.y]#用于储存初始的指针相对坐标
    #流量提示语模式切换
    if((event.x>10)and(event.x<200)and(event.y>10)and(event.y<20)):
        if(fsty.get()==0):
            fsty.set(1)
        else:
            fsty.set(0)
    #余额提示语模式切换
    if((event.x>10)and(event.x<200)and(event.y>30)and(event.y<40)):
        if(msty.get()==0):
            msty.set(1)
        else:
            msty.set(0)
    #刷新提示语
    if(fs2==1):
        lab['text']=flowtext[fsty.get()]
    elif(fs2==2):
        lab['text']=moneytext[msty.get()]
    #IPV4离线/下线
    if(lin.get()==0):
        if((event.x>10)and(event.x<60)and(event.y>50)and(event.y<70)):
            if(ipv4state=='#00FA9A'):
                back=logout(4)
                threading.Thread(target=getdata,args=()).start()
                exDialog(top).notice("IPV4注销",back,5000)
            else:
                back=login(name.get(),key.get(),4)
                getdata()
                exDialog(top).notice("IPV4登陆",back,5000)
    #IPV6离线/下线
    if((lin.get()==0)or(typ.get()==0)):
        if((event.x>80)and(event.x<130)and(event.y>50)and(event.y<70)):
            if(ipv6state=='#00FA9A'):
                back=logout(6)
                threading.Thread(target=getdata,args=()).start()
                exDialog(top).notice("IPV6注销",back,5000)
            else:
                back=login(name.get(),key.get(),6)
                threading.Thread(target=getdata,args=()).start()
                exDialog(top).notice("IPV6登陆",back,5000)
    #在线设备查询
    if((event.x>150)and(event.x<200)and(event.y>50)and(event.y<70)):
         text=''
         for i in count:
             if(i[2] in macbz):
                 text=text+'[%d]%s\n'%(count.index(i)+1,macbz[i[2]])
             else:
                 text=text+'[%d]IP:%s\n'%(count.index(i)+1,i[0]) 

         exDialog(top).notice("在线用户",text,5000)
    top.bind("<Button1-Motion>",lambda event:move(event,top))#鼠标单击+移动事件

def pop(event,menubar):
    """右键窗显示位置控制"""
    menubar.post(event.x_root,event.y_root)
  
def flowstart(event,showwin):
    """小悬浮窗显示"""
    showwin.deiconify()
    showwin.geometry("100x50+%d+%d"%(event.x_root+20,event.y_root-20))
def flowhide(event,showwin):
    """小悬浮窗隐藏"""
    showwin.withdraw()

def flowshow2(event,showwin,lab):
    """显示流量余额条详情"""
    global fs2
    showwin.geometry("120x50+%d+%d"%(event.x_root+20,event.y_root-20))
    if((event.x>10)and(event.x<200)and(event.y>10)and(event.y<20)):
        lab['text']=flowtext[fsty.get()]
        showwin.deiconify()
        fs2=1
    elif((event.x>10)and(event.x<200)and(event.y>30)and(event.y<40)):
        lab['text']=moneytext[msty.get()]
        showwin.deiconify()
        fs2=2
    else:
        fs2=0
        showwin.withdraw()

def recoveronline():
    if(typ.get()==1):
        cmp='ipv4:登陆成功|ipv6:登陆成功'
        back=login(name.get(),key.get(),46)
    else:
        cmp='登陆成功'
        back=login(name.get(),key.get(),4)

    if(cmp==back):
        exDialog(root).notice("防掉线","已为您重新连接网络",5000)
    else:
        exDialog(root).notice("重新连接失败",back,5000)

def main(top,cv,lab):
    """悬浮窗主函数"""
    global flowper,moneyper,ipv4state,ipv6state,count,moneytext,flowtext

    
    if(sfn.get()==1):
        if(flowper==1.0):
            for i in getoffid(session)[1:]:
                dooffid(session,i[3])
            root.deiconify()
            exDialog(root).notice("流量耗尽","已为您强制下线所有设备\n保护您的流量安全",5000)
            top.destroy()
            return 0
    if(fn.get()==1):
        if(flowper==1.0):
                exDialog(root).notice("流量耗尽！","达到免费额度上限，接下来将使用计费流量",2000)
        elif(flowper>0.9):
            exDialog(root).notice("流量即将耗尽！","请关注您的流量消耗",2000)

    if((lin.get()==1)and(sfn.get()==0)):
        if(ipv4state!='#00FA9A'):
            threading.Thread(target=recoveronline,args=()).start()
        elif((ipv6state!='#00FA9A')and(typ.get()==1)):
            threading.Thread(target=recoveronline,args=()).start()
    
    if(getdata_state==True):
        threading.Thread(target=getdata,args=()).start()

    if(fs2==1):
        lab['text']=flowtext[fsty.get()]
    elif(fs2==2):
        lab['text']=moneytext[msty.get()]
    cv.create_rectangle(0, 50, 410, 100,
        outline='black', # 边框颜色
        fill='black'
        )

    cv.create_rectangle(10+int(190*(1-flowper)), 10, 200, 20,
    outline='black', # 边框颜色
    fill='black'
    )
    cv.create_rectangle(10+int(190*(1-moneyper)), 30, 200, 40,
    outline='black',
    fill='black'# 边框颜色
    )
    cv.create_rectangle(10, 10, 200, 20,
    outline='white'
    )
    cv.create_rectangle(10, 30, 200, 40,
    outline='white'
    )

    cv.create_rectangle(10, 50, 60, 70,
    outline=ipv4state, # 边框颜色
    )
    cv.create_text((15, 60),text = 'IPV4',
    font = ('',15),
    fill=ipv4state,
    anchor = W,
    justify = CENTER)

    cv.create_rectangle(80, 50, 130, 70,
    outline=ipv6state, # 边框颜色
    )
    cv.create_text((85, 60),text = 'IPV6',
    font = ('',15),
    fill=ipv6state,
    anchor = W,
    justify = CENTER)

    cv.create_rectangle(150, 50, 200, 70,
    outline='#00FFFF', # 边框颜色
    )
    cv.create_text((170, 60),text = len(count),
    font = ('',15),
    fill='#00FFFF',
    anchor = W,
    justify = CENTER)

    top.after(fret.get(),lambda:main(top,cv,lab))
    top.update()
#############################################################################################
#
#                                            专业模式
#
#############################################################################################
def flowshow(event,showwin,dlist,draw_2,draw_1,lab):
    """流量统计悬浮窗显示"""
    showwin.geometry("100x50+%d+%d"%(event.x_root+20,event.y_root-20))
    num=int((event.x-draw_1)/(draw_2*3))
    if(num<len(dlist)):
        if((dlist[num][1]/1024)>1):
            lab['text']='%s\n%1.fGB'%(dlist[num][0],dlist[num][1]/1024)
        else:
            lab['text']='%s\n%1.fMB'%(dlist[num][0],dlist[num][1])
            
def profre(top,tree1,tree2,tree3):
    """专业模式刷新"""
    
    for item in tree1.get_children():
        tree1.delete(item)
    for item in tree2.get_children():
        tree2.delete(item)
    for item in tree3.get_children():
        tree3.delete(item)
        
    host=['','','']
    #适用pyinstall版本，获取当前主机MAC地址
    p = subprocess.Popen('ipconfig /all',shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    macs = ''
    for line in p.stdout.readlines():
        macs += line.decode('gbk')
    state=p.wait()
    #获取在线设备列表
    for i in getoffid(session)[1:]:
        if(i[0].find('.')!=-1):
            if(macs.find("-".join([i[2][e:e+2] for e in range(0,11,2)]))!=-1):
                #查询到本设备信息为本机，并添加到信任列表
                host=i
                saflist[host[0]]=[host[2],'本机']
                tree2.insert('','end',values=[host[0],host[2],'本机',host[2]])
        #将获取到的在线设备列表加入目录树1
        i[-1]=i[2]
        tree1.insert('','end',values=i)
    #获取绑定的MAC地址列表
    for i in getmacs(session):
        if(i!=host[2]):
            #非主机，则为无感知设备列表
            tree2.insert('','end',values=['',i,'无感知设备',i])
    #获取储存在本地的信任设备列表
    for i in saflist:
        if((i!=host[0])and(saflist[i][1]=='本机')):
            #主机IP变化后，将之前的主机信任变更为信任设备
           saflist[i][1]='信任设备'
        if(i!=host[0]):
            tree2.insert('','end',values=[i,saflist[i][0],saflist[i][1],saflist[i][0]])
    #获取风险登陆
    tmp=[]#tmp列表为未进行去重、次数统计的风险列表
    for i in getlog(session,time.strftime("%Y-%m-%d",time.localtime(time.time()-3600*24*31)),
                    time.strftime("%Y-%m-%d",time.localtime(time.time())))[1:]:
        #获取近31天登陆信息
        if(i[5]==''):
            continue
        flag=0
        for j in saflist:
            if((sam.get()==0)and(i[5]==j)):
                #将每条登陆信息在信任列表中检查，当存在则跳出循环，并标记flag为1
                flag=1
                break
            if(sam.get()==1):
                tmp1=j.split(".")
                tmp2=i[5].split(".")
                tmp1=tmp1[0]+tmp1[1]+tmp1[2]
                tmp2=tmp2[0]+tmp2[1]+tmp2[2]
                if(tmp1==tmp2):
                    flag=1
                    break
        if(flag==0):
            #添加未在信任列表中的项目
            k=[i[0],i[1],i[5],i[3]]
            tmp.append(k)

    data3={}#储存去重后的风险列表，并未统计次数
    for i in tmp:
        #去重操作
        if(i[2] not in data3):
            data3[i[2]]=[[i[0],i[1],i[3]]]
        else:
            data3[i[2]].append([i[0],i[1],i[3]])

    tmp=[]#储存统计次数后的非重复列表
    for i in data3:
        total=0
        cou=len(data3[i])
        last=data3[i][-1][1]
        for j in data3[i]:
            total=total+int(float(j[2]))
        tmp.append([cou,last,i,total])
    #按次数从多到少排序
    tmp=sorted(tmp, key=lambda tmp: tmp[0], reverse=True)
    for i in tmp:
        tree3.insert('','end',values=i)
    #写入本地配置文件
    writeini()
    cobz(tree1,tree2,1)
    top.update()
    #top.after(5000,lambda:profre(top,tree1,tree2,tree3))

def flowpic(cv,lab1,lab2,showwin,lab):
    """数据统计绘图"""
    #刷新绘图板
    cv.create_rectangle(0, 0, int(cv['width']), int(cv['height']),
        outline='white', # 边框颜色
        fill='white'
        )
    a=cv.create_text((int(cv['width'])/2-70,int(cv['height'])/2),text="Loading......",
    font = ('',30),
    fill='black',
    anchor = W,
    justify = CENTER)
    
    data4={}
    totalflow=0
    if(choo.get()=='本月'):
        li=getlog(session,time.strftime("%Y-%m-01",time.localtime()),time.strftime("%Y-%m-%d",time.localtime()))[1:]
    elif(choo.get()=='近7天'):
        li=getlog(session,time.strftime("%Y-%m-%d",time.localtime(time.time()-3600*24*7)),time.strftime("%Y-%m-%d",time.localtime()))[1:]
    elif(choo.get()=='近30天'):
        li=getlog(session,time.strftime("%Y-%m-%d",time.localtime(time.time()-3600*24*30)),time.strftime("%Y-%m-%d",time.localtime()))[1:]
    elif(choo.get()=='近60天'):
        li=getlog(session,time.strftime("%Y-%m-%d",time.localtime(time.time()-3600*24*60)),time.strftime("%Y-%m-%d",time.localtime()))[1:]
    elif(choo.get()=='本年'):
        li=getlog(session,time.strftime("%Y-01-01",time.localtime()),time.strftime("%Y-%m-%d",time.localtime()))[1:]
        
    for i in li:
        if(i[1].split(" ")[0] not in data4):
            data4[i[1].split(" ")[0]]=float(i[3])
        else:
            data4[i[1].split(" ")[0]]=data4[i[1].split(" ")[0]]+float(i[3])
        totalflow=totalflow+float(i[3])
    dlist=sorted(data4.items(),key=lambda x:x[0])
    sortlist=sorted(data4.items(),key=lambda x:x[1])
    draw_1=10
    draw_2=(int(cv['width'])-draw_1*2)/(len(data4)*3)
    draw_3=30
    draw_4=(int(cv['height'])-draw_1*2-draw_3)/sortlist[-1][1]
    posy=int(cv['height'])-draw_3-draw_1
    posx=draw_1
    textlen=0
    for i in dlist:
        cv.create_rectangle(posx, posy, posx+draw_2*2, posy-i[1]*draw_4,
        outline='black', # 边框颜色
        fill='black'
        )
        textlen=textlen+draw_2*2
        if(textlen>10*2):
            cv.create_text((posx,int(cv['height'])-draw_3/2),text = '%s\n%s'%(i[0].split('-')[1],i[0].split('-')[2]),
    font = ('',10),
    fill='black',
    anchor = W,
    justify = CENTER)
            textlen=0
        
        posx=posx+draw_2*3
    lab1['text']='共使用%dGB%dMB'%(totalflow/1024,totalflow-int(totalflow/1024)*1024)
    lab2['text']='%s消耗最多'%(sortlist[-1][0])
    cv.delete(a)
    cv.bind("<Motion>",lambda event:flowshow(event,showwin,dlist,draw_2,draw_1,lab))
    cv.bind("<Enter>",lambda event:flowstart(event,showwin))
    cv.bind("<Leave>",lambda event:flowhide(event,showwin))
    
def trfun(event,t):
    global sels
    sels[t]= event.widget.selection()
    
def offline(ty,top,tree1,tree2,tree3):
    global sels
    try:
        if(len(tree1.get_children())==0):
            exDialog(top).notice("强制下线",'无在线设备',5000)
            return False
        if(ty==0):
            if(sels[0]==''):
                exDialog(top).notice("强制下线",'未选中',5000)
                return False
            for idx in sels[0]:
                dooffid(session,tree1.item(idx)['values'][3])
                exDialog(top).notice("强制下线","已将%s移除"%(tree1.item(idx)['values'][0]),5000)
        elif(ty==1):
            hostip=tree2.item(tree2.get_children()[0])['values'][0]
            text='已将：\n'
            for i in tree1.get_children():
                if(tree1.item(i)['values'][0]!=hostip):
                    dooffid(session,tree1.item(i)['values'][3])
                    text=text+tree1.item(i)['values'][0]+'\n'
            text=text+'移除'
            exDialog(top).notice("强制下线",text,5000)
        elif(ty==2):
            text='已将：\n'
            for i in tree1.get_children():
                dooffid(session,tree1.item(i)['values'][3])
                text=text+tree1.item(i)['values'][0]+'\n'
            text=text+'移除'
            exDialog(top).notice("强制下线",text,5000)
        sels[0]=''
    except:
        exDialog(top).notice("强制下线","失败了",5000)
            
    time.sleep(1)
    profre(top,tree1,tree2,tree3)   
 
def addsaflist(ty,top,tree1,tree2,tree3):
    global sels
    if(ty==0):
        if(sels[0]==''):
            exDialog(top).notice("信任设备添加",'未选中',5000)
            return False 

        for idx in sels[0]:
            if(tree1.item(idx)['values'][2]==0):
                saflist[tree1.item(idx)['values'][0]]=['','信任设备']
            else:
                saflist[tree1.item(idx)['values'][0]]=[tree1.item(idx)['values'][2],'信任设备']
            exDialog(top).notice("信任设备添加","已添加%s"%(tree1.item(idx)['values'][0]),5000)
        sels[0]=''
    elif(ty==1):
        if(sels[2]==''):
            exDialog(top).notice("信任设备添加",'未选中',5000)
            return False
        
        for idx in sels[2]:
            saflist[tree3.item(idx)['values'][2]]=['','信任设备']
            exDialog(top).notice("信任设备添加","已添加%s"%(tree3.item(idx)['values'][2]),5000)
        sels[2]=''
    writeini()
    profre(top,tree1,tree2,tree3)
                
def delsaflist(top,tree1,tree2,tree3):
    global sels
    if(sels[1]==''):
            exDialog(top).notice("移除信任设备",'未选中',5000)
            return False
        
    for idx in sels[1]:
        if(tree2.item(idx)['values'][2]=='信任设备'):
            saflist.pop(tree2.item(idx)['values'][0])
            exDialog(top).notice("移除信任设备","已移除%s"%(tree2.item(idx)['values'][0]),5000)
        elif(tree2.item(idx)['values'][2]=='无感知设备'):
            tp=getmacs(session)
            if(len(tp)==1):
                domacs(session,'')
            else:
                for i in tp:
                    if(i != tree2.item(idx)['values'][1]):
                        domacs(session,i)
            exDialog(top).notice("移除信任设备","已移除%s"%(tree2.item(idx)['values'][1]),5000)
        else:
            exDialog(top).notice("移除信任设备","不可移除",5000)
    writeini()
    profre(top,tree1,tree2,tree3)
    sels[1]=''



def cobz(tree1,tree2,*t):
    
    if(len(t)==0):
        if(bzm.get()==1):
            bzm.set(0)
        else:
            bzm.set(1)
    
    if(bzm.get()==0):
        for tree in [tree1,tree2]:
            tree.heading('mac',text='MAC')
            for i in tree.get_children():
                tmp=tree.item(i,'values')[-1]
                tree.set(i,column='mac',value=tmp)
                    
            
    if(bzm.get()==1):
        for tree in [tree1,tree2]:
            tree.heading('mac',text='备注名')
            for i in tree.get_children():
                tmp=tree.item(i,'values')[-1]
                if(tmp in macbz):
                    tmp=macbz[tmp]
                    tree.set(i,column='mac',value=tmp)
    
def cgbz(event,tree1,tree2,t):
    global sels
    if((bzm.get()==1)and(len(sels)!=0)):
        if(t==0):
            tree=tree1
            j=2
        else:
            tree=tree2
            j=1
        if(sels[t]==''):
            return 0
        row=sels[t][0]
        if(tree.item(row)['values'][j]==''):
            return 0
        smtop=Toplevel(tree)
        smtop.overrideredirect(True)#设置无框窗体
        smtop.wm_attributes('-topmost',1)
        smtop.attributes("-alpha", 0.8)
        smtop.geometry("150x80+%d+%d"%(event.x_root+20,event.y_root-20))
        lab=Label(smtop,text="设备专属标记~")
        lab.pack()
        
        def end(*event):
            sels[t]=''
            smtop.destroy()
        def ok():
            if(inp.get() in macbz.values()):
                lab['text']="名字重复了"
            else:
                if(tree.item(row)['values'][j]!=inp.get()):
                    macbz[tree.item(row)['values'][-1]]=inp.get()
                    cobz(tree1,tree2,1)
                end()
        
        inp=ttk.Entry(smtop)
        inp.insert(0,tree.item(row)['values'][j])
        inp.pack()
        ttk.Button(smtop,text="修改",command=ok).pack(side='left')
        ttk.Button(smtop,text="关闭",command=end).pack(side='right')
    
   
def promode(top):
    frame1=ttk.Frame(top)
    ttk.Label(frame1, text="设备管理",font=('微软雅黑',20)).grid(row=0,column=1,sticky=E,padx=20)
    ttk.Label(frame1, text="在线设备",font=('微软雅黑',12)).grid(row=1,column=0)
    ttk.Label(frame1, text="标记设备",font=('微软雅黑',12)).grid(row=1,column=1)
    ttk.Label(frame1, text="风险登录（近31天）",font=('微软雅黑',12)).grid(row=1,column=2,sticky=E)
    ttk.Checkbutton(frame1, text="去除相似网段",variable=sam).grid(row=1,column=3,sticky=W)
    
    
    tree1=ttk.Treeview(frame1,columns=['ipv4','ipv6','mac'],show='headings')
    tree1.heading('ipv4',text='IPV4')
    tree1.column('ipv4',width=100)
    tree1.heading('ipv6',text='IPV6')
    tree1.column('ipv6',width=100)
    tree1.heading('mac',text='MAC')
    tree1.column('mac',width=100)
    tree1.grid(row=2,column=0)
    tree1.bind("<<TreeviewSelect>>",lambda event:trfun(event,0))
    menubar1=Menu(tree1,tearoff = 0)
    menubar1.add_command(label=['强制下线'],command=lambda:offline(0,top,tree1,tree2,tree3))
    menubar1.add_command(label=['只保留本机'],command=lambda:offline(1,top,tree1,tree2,tree3))
    menubar1.add_command(label=['全部下线'],command=lambda:offline(2,top,tree1,tree2,tree3))
    menubar1.add_separator()
    menubar1.add_command(label=['添加信任设备'],command=lambda:addsaflist(0,top,tree1,tree2,tree3))
    tree1.bind("<Button-3>",lambda event:pop(event,menubar1))
    
    tree2=ttk.Treeview(frame1,columns=['ip','mac','flag'],show='headings')
    tree2.heading('ip',text='IP')
    tree2.column('ip',width=100)
    tree2.heading('mac',text='MAC')
    tree2.column('mac',width=100)
    tree2.heading('flag',text='标记')
    tree2.column('flag',width=100)
    tree2.grid(row=2,column=1)
    tree2.bind("<<TreeviewSelect>>",lambda event:trfun(event,1))
    menubar2=Menu(tree2,tearoff = 0)
    menubar2.add_command(label=['移除信任'],command=lambda:delsaflist(top,tree1,tree2,tree3))
    tree2.bind("<Button-3>",lambda event:pop(event,menubar2))

    tree1.heading('mac',command=lambda:cobz(tree1,tree2))
    tree2.heading('mac',command=lambda:cobz(tree1,tree2))
    tree1.bind('<Double-1>',lambda event:cgbz(event,tree1,tree2,0))
    tree2.bind('<Double-1>',lambda event:cgbz(event,tree1,tree2,1))
    
    tree3=ttk.Treeview(frame1,columns=['u','d','ip','used'],show='headings')
    tree3.heading('u',text='次数')
    tree3.column('u',width=50)
    tree3.heading('d',text='最近一次下线时间')
    tree3.column('d',width=150)
    tree3.heading('ip',text='登录IP')
    tree3.column('ip',width=100)
    tree3.heading('used',text='消耗流量MB')
    tree3.column('used',width=100)
    tree3.grid(row=2,column=2,columnspan=2)
    tree3.bind("<<TreeviewSelect>>",lambda event:trfun(event,2))
    menubar3=Menu(tree3,tearoff = 0)
    menubar3.add_command(label=['添加信任设备'],command=lambda:addsaflist(1,top,tree1,tree2,tree3))
    tree3.bind("<Button-3>",lambda event:pop(event,menubar3))
    ttk.Button(frame1,text='刷新',command=lambda:profre(top,tree1,tree2,tree3)).grid(row=0,column=2,sticky=W)
    frame1.pack(expand=1)

    showwin=Toplevel(top)
    showwin.geometry("200x100")
    showwin.overrideredirect(True)#设置无框窗体
    showwin.wm_attributes('-topmost',1)
    showwin.attributes("-alpha", 0.8)
    lab=ttk.Label(showwin, text='00.0GB',font=('微软雅黑',10))
    lab.pack()
    showwin.withdraw()

    frame2=ttk.Frame(top)
    ttk.Label(frame2, text="流量统计",font=('微软雅黑',20)).grid(row=0,column=0,columnspan=2)
    cv = Canvas(frame2,bg="white",width=800,height=200)
    cv.grid(row=1,column=0,rowspan=6)
    ttk.Label(frame2, text="--数据概述--",font=('微软雅黑',15)).grid(row=1,column=1)
    lab1=ttk.Label(frame2, text="共使用00.0GB",font=('微软雅黑',10))
    lab2=ttk.Label(frame2, text="X月X日消耗最多",font=('微软雅黑',10))
    lab1.grid(row=2,column=1)
    lab2.grid(row=3,column=1)
    ttk.Label(frame2, text="--统计范围--",font=('微软雅黑',15)).grid(row=4,column=1)
    Chosen = ttk.Combobox(frame2,textvariable=choo)
    Chosen ['values'] =('本月','本年','近7天','近30天','近60天')
    Chosen .current(0)
    Chosen.grid(row=5,column=1)
    
    def flowpicn(cv,lab1,lab2,showwin,lab):
        threading.Thread(target=flowpic,args=(cv,lab1,lab2,showwin,lab)).start()
        
    ttk.Button(frame2,text='刷新',command=lambda:flowpicn(cv,lab1,lab2,showwin,lab)).grid(row=6,column=1)
    frame2.pack(expand=1)

    profre(top,tree1,tree2,tree3)
    flowpicn(cv,lab1,lab2,showwin,lab)
    
def proend(event,top,*p):
    """结束pro窗体"""
    global count
    count=[]
    root.deiconify()
    top.destroy()
    writeini()
    try:
        if(p[0][0]==1):
            pro.set(0)
            Login()
    except:
        pass

def Login(*p):
    """用户登陆，入口"""
    global session,namechange,namelast
    
    tips=Toplevel(root,bg='black')
    tips.overrideredirect(True)#设置无框窗体
    tips.wm_attributes('-topmost',1)
    tips.attributes("-alpha", 0.8)
    root.update()
    tips.geometry("%dx%d+%d+%d"%(root.winfo_width()+5,root.winfo_height()+35,root.winfo_x()+5,root.winfo_y()))
    inf=Label(tips,text='正在登录管理系统',font=('微软雅黑','30','bold'),bg='black',fg='white')
    inf.pack(expand=1)
    Label(tips,text=random.sample(__tips__, 1)[0],font=('微软雅黑','20','bold'),bg='black',fg='white').pack(expand=1)
    tips.update()
    #登陆网关管理系统，保存对话cookies
    session=managelogin(name.get(),key.get())
    #检测是否为用户切换后登录，是则下线当前用户
    if(session=='网络错误'):
        tips.destroy()
        exDialog(root).msgbox('登陆失败','未连接校园网',0,[])
        return 0
    
    if(pro.get()==0):
        if(name.get()!=namelast):
            namechange=1
        if(namechange==1):
            inf['text']='检查到多用户，注销中'
            tips.update()
            if(typ.get()==1):
                logout(46)
            else:
                logout(4)
            namechange=0

    #登陆网关，如果在线则不登陆
    
    inf['text']='正在登录网关'
    tips.update()
    if(typ.get()==1):
        cmp='ipv4:登陆成功|ipv6:登陆成功'
        if(getnowinf(46)==False):
            back=login(name.get(),key.get(),46)
        else:
            back=cmp
    else:
        cmp='登陆成功'
        if(pro.get()==1):
            back=cmp
        else:
            if(getnowinf(4)==False):
                back=login(name.get(),key.get(),4)
            else:
                back=cmp
    tips.withdraw()#此处不能先destroy否则会触发后面的.protocol("WM_DELETE_WINDOW")这个问题要注意
    if((back==cmp)and(session!=False)):
        namelast=name.get()
        if(name.get() not in namelist):
            namelist.append(name.get())
            nameinp['values']=namelist
        writeini()#写配置数据
        root.withdraw()#隐藏主窗体
        #监控模式
        if(pro.get()==0):
            #主窗
            top=Toplevel(root)
            top.attributes("-alpha", 0.7)
            top.geometry("210x80")
            top.overrideredirect(True)#设置无框窗体
            top.wm_attributes('-topmost',1)
            #悬浮窗
            showwin=Toplevel(top)
            showwin.geometry("250x100")
            showwin.overrideredirect(True)#设置无框窗体
            showwin.wm_attributes('-topmost',1)
            showwin.attributes("-alpha", 0.8)
            lab=ttk.Label(showwin, text='00.0GB\n00.0GB',font=('微软雅黑',10))
            lab.pack()
            showwin.withdraw()
            #绘图板Canvas
            cv = Canvas(top,bg='black')
            for j in range(0,2):
                #绘制血条边框
                cv.create_rectangle(10, 10+j*20, 200, 20+j*20,
                                    outline='white', # 边框颜色
                                    )
                #绘制全彩血量
                for i in range(0,190):
                    cv.create_line(i+10, 11+j*20, i+10, 20+j*20,
                                   fill=color(1-i/190,(90,255,255),(90,255,90),(255,255,90),(255,90,90))# 填充颜色
                                   )
            cv.pack(fill=BOTH, expand=YES)
            top.update()
            #事件绑定
            top.bind("<Button-1>",lambda event:moves(event,top,lab))#鼠标单击事件
            top.bind("<KeyPress-Escape>",lambda event:end(event,top))#按下键盘Esc键事件
            cv.bind("<Motion>",lambda event:flowshow2(event,showwin,lab))
            cv.bind("<Enter>",lambda event:flowstart(event,showwin))
            cv.bind("<Leave>",lambda event:flowhide(event,showwin))
            #刷新数据
            getdata()
            #进入主循环
            main(top,cv,lab)
        else:
            top=Toplevel(root)
            top.geometry("1000x600")
            top.title('专业模式-BJUT网关助手%s'%(__version__))
            top.protocol("WM_DELETE_WINDOW", lambda:proend('',top,p))
            showicon(top)
            promode(top)
        
    elif((back==cmp)and(session==False)):
        exDialog(root).msgbox('登陆失败','网关管理系统登录失败',0,[])
    else:
        exDialog(root).msgbox('登陆失败',back,0,[])

    tips.destroy()

def checkbind1(event):
    #注意事件触发的时候pro的值还没有改变
    if(pro.get()==0):
        auto.set(0)
        typ.set(0)
def checkbind2(event):
    #注意事件触发的时候pro的值还没有改变
    if((auto.get()==0)or(typ.get()==0)):
        pro.set(0)

def checkbind2(event):
    #注意事件触发的时候pro的值还没有改变
    if((auto.get()==0)or(typ.get()==0)):
        pro.set(0)

def checkbind3(event):
    name = 'BJUTlogin' # 要添加的项值名称
    path = sys.argv[0] # 要添加的exe路径
    try:
        KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
        if(sup.get()==0):
            win32api.RegSetValueEx(key, name, 0, win32con.REG_SZ, path)
        else:
            win32api.RegDeleteValue(key, name)
        win32api.RegCloseKey(key)
    except:
        sup.set(1)
        exDialog(root).notice("开机启动项添加失败","请授权本应用",5000)
        

def delhis():
    """用户登录历史管理"""
    global nameinp
    try:
        a=configparser.ConfigParser()
        a.read("%s/login.ini"%(os.path.split(sys.argv[0])[0]))
        namelist.pop(namelist.index(name.get()))
        a.set("GLOBAL", "namelist",json.dumps(namelist))
        nameinp['values']=namelist
        if(a.get("GLOBAL","namelast")==name.get()):
            a.set("GLOBAL", "namelast","")
        a.remove_section(name.get())
        name.set('')
        with open("%s/login.ini"%(os.path.split(sys.argv[0])[0]),"w") as f:
            a.write(f)
    except:
        pass

def set_end(top):
    if(name.get() in namelist):
        writeini()
    top.destroy()

def devicenotice(event,top):
    if(sdev.get()==0):
        if(len(saflist)==0):
            exDialog(top).msgbox("无法启用","信任列表为空\n无法启用此功能\n请登陆专业模式将设备加入信任列表",0,[])
            sdev.set(0)
        else:
            text='此功能启用后，将只允许以下设备登陆'
            for i in saflist:
                if(saflist[i][0]!=''):
                    text=text+"\n[MAC]%s"%(saflist[i][0])
                else:
                    text=text+"\n[IP]%s"%(i)
                
            text=text+"\n如果您不了解相关内容，请点否"
            if(exDialog(top).msgbox("是否进行此操作",text,1,[])==False):
                sdev.set(0)
            else:
                sdev.set(1)

def scaleset(val,lab):
    lab['text']='数据刷新频率:%.1fs'%(float(val)/1000)
    fret.set(int(float(val)))
    
def Settings():
    """设置界面"""
    readini()
    sup.set(0)
    try:
        KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, KeyName, 0, win32con.KEY_ALL_ACCESS)
        i = 0
        while True:
            if('BJUTlogin'in win32api.RegEnumValue(key, i)):
                if(win32api.RegEnumValue(key, i)[1].replace("\\\\","\\")==sys.argv[0]):
                    sup.set(1)
            i+=1
    except:
        pass
    
    top=Toplevel(root)
    top.geometry("450x400")
    showicon(top)
    if(name.get() in namelist):
        top.title("账户：%s 的系统设置"%(name.get()))
    else:
        top.title("由于输入的账户为无效状态，当前设置不会被保存")
    frame1=LabelFrame(top,foreground='black',text="显示设置",font=('微软雅黑',15))
    ttk.Style().configure('my.TCheckbutton', font=('微软雅黑', 15))
    ttk.Checkbutton(frame1,text='显示剩余流量',variable=fsty,style='my.TCheckbutton').grid(row=0,column=0,padx=20)
    ttk.Checkbutton(frame1,text='显示余额折算流量',variable=msty,style='my.TCheckbutton').grid(row=0,column=1,padx=20)
    lab=ttk.Label(frame1,text="数据刷新频率:%.1f"%(fret.get()/1000),font=('微软雅黑',15))
    lab.grid(row=1,column=0,sticky=E,padx=20)
    sca=ttk.Scale(frame1,orient='horizontal',from_=2000,to=8000,command=lambda val:scaleset(val,lab))
    sca.set(fret.get())
    sca.grid(row=1,column=1,padx=20,sticky=W)
    frame2=LabelFrame(top,foreground='black',text="流量报警",font=('微软雅黑',15))
    ttk.Checkbutton(frame2,text='流量超额提醒',variable=fn,style='my.TCheckbutton').grid(row=0,column=0,padx=20)
    ttk.Checkbutton(frame2,text='流量超额自动下线',variable=sfn,style='my.TCheckbutton').grid(row=0,column=1,padx=20)
    frame3=LabelFrame(top,foreground='black',text="自动设置",font=('微软雅黑',15))
    ttk.Checkbutton(frame3,text='退出程序后自动注销',variable=lout,style='my.TCheckbutton').grid(row=0,column=0,padx=20)
    ttk.Checkbutton(frame3,text='防掉线模式',variable=lin,style='my.TCheckbutton').grid(row=0,column=1,padx=20)
    ck=ttk.Checkbutton(frame3,text='开机自动启动',variable=sup,style='my.TCheckbutton')
    ck.grid(row=1,column=0,columnspan=2,padx=20)
    ck.bind("<Button-1>",checkbind3)
    frame4=LabelFrame(top,foreground='black',text="设备许可",font=('微软雅黑',15))
    ttk.Checkbutton(frame4,text='新设备登陆询问是否允许登陆',variable=dev,style='my.TCheckbutton').grid(row=0,column=0,padx=20)
    ck2=ttk.Checkbutton(frame4,text='只允许登陆信任列表的设备',variable=sdev,style='my.TCheckbutton')
    ck2.grid(row=1,column=0,padx=20)
    ck2.bind("<Button-1>",lambda event:devicenotice(event,top))
    frame1.pack(expand=1)
    frame2.pack(expand=1)
    frame3.pack(expand=1)
    frame4.pack(expand=1)
    top.protocol("WM_DELETE_WINDOW", lambda:set_end(top))
   
def logininput(a):
    """程序主界面入口，a=1为自动登录入口"""
    global nameinp
    #账户输入frame布局
    frame1=ttk.Frame(root)
    ttk.Label(frame1, text="账户 ",font=('微软雅黑',20)).grid(row=0,column=0)
    ttk.Label(frame1, text="密码 ",font=('微软雅黑',20)).grid(row=1,column=0)
    nameinp=ttk.Combobox(frame1,textvariable=name, width=19,font=('微软雅黑', 18))
    nameinp.grid(row=0,column=1)
    nameinp['values']=namelist
    nameinp.bind("<<ComboboxSelected>>", readini)
    nameinp.focus_set()
    me=Menu(nameinp,tearoff = 0)
    me.add_command(label=['删除该条'],command=delhis)
    nameinp.bind("<Button-3>",lambda event:pop(event,me))
    keyinp=ttk.Entry(frame1,textvariable=key,font=('',20),show='⚫')
    keyinp.grid(row=1,column=1)
    keyinp.bind('<KeyPress-Return>',Login)
    frame1.pack(expand=1)
    #设置及登陆frame布局
    frame2=ttk.Frame(root)
    ttk.Style().configure('my.TButton', font=('微软雅黑', 20))
    ttk.Style().configure('my.TCheckbutton', font=('微软雅黑', 15))
    ck1=ttk.Checkbutton(frame2,text='ipv4/6',variable=typ,style='my.TCheckbutton')
    ck1.grid(row=0,column=0,padx=20)
    ck1.bind("<Button-1>",checkbind2)
    ck2=ttk.Checkbutton(frame2,text='自动登录',variable=auto,style='my.TCheckbutton')
    ck2.grid(row=0,column=1,padx=20)
    ck2.bind("<Button-1>",checkbind2)
    ck3=ttk.Checkbutton(frame2,text='专业模式',variable=pro,style='my.TCheckbutton')
    ck3.grid(row=0,column=2,padx=20)
    ck3.bind("<Button-1>",checkbind1)
    ttk.Button(frame2,text='登 录',style='my.TButton',command=Login).grid(row=1,column=1)
    ttk.Button(frame2,text='设置',style='my.TButton',width='4',command=Settings).grid(row=1,column=2)
    frame2.pack(expand=1)
    #版本号
    ttk.Label(root, text="@LMR %s"%(__version__),font=('微软雅黑',10)).pack(expand=1)
    #自动登录
    if(a==1):
        root.update()
        try:
            Login()
        except:
            print(sys.exc_info())
    
    
readini()

if(auto.get()==1):
    logininput(1)
else:
    logininput(0)

root.mainloop()
