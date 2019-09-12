from WSYY import *

from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import threading#多线程搜索
import webbrowser

root=Tk()
root.title("无损音乐搜索器 byLMR")
root.geometry("400x300")

word= StringVar()

                 
def trefun(event):
    global sels
    sels= event.widget.selection()#event.widget获取Treeview对象，调用selection获取选择对象名称

def linking(i,j,k):
    labelinf['text']='检索到：%d条 正在查询网盘链接......'%(num[0])
    if(j=='wsyyxz.com'):
        TMP=WSYY().getPAN_1(k)
    elif(j=='52flac.com'):
        TMP=WSYY().getPAN_2(k)
    elif(j=='baiduonce.com'):
        TMP=WSYY().getPAN_3(k)
    elif(j=='sq688.com'):
        TMP=WSYY().getPAN_4(k)
    elif(j=='acgjc.com'):
        TMP=WSYY().getPAN_5(k)
    if(i=='return'):
        labelinf['text']='检索到：%d条 正在跳转下载器'%(num[0])
        webbrowser.open("https://www.baiduwp.com/s/?surl=%s"%(TMP))
        labelinf['text']='检索到：%d条 请至浏览器下载'%(num[0])
    else:
        labelinf['text']='检索到：%d条 已复制到剪贴板'%(num[0])
        root.clipboard_clear()
        root.clipboard_append(TMP)
        top=Toplevel()
        top.title(i)
        top.geometry("500x30")
        show=ttk.Entry(top)
        show.insert ( 0, TMP )
        show.pack(fill='both',expand=1)
    root.update()
            
def trerun(*event):
    for idx in sels:
        threading.Thread(target=linking,args=(tree.item(idx)['values'][0],tree.item(idx)['values'][1],tree.item(idx)['values'][2])).start()

num=[0,0]
def doing(i):
    global tree,labelinf,num
    try:
        if(i=='wsyyxz.com'):
                TMP=WSYY().getList_1(word.get())
        elif(i=='52flac.com'):
            TMP=WSYY().getList_2(word.get())
        elif(i=='baiduonce.com'):
            TMP=WSYY().getList_3(word.get())
        elif(i=='sq688.com'):
            TMP=WSYY().getList_4(word.get())
        elif(i=='acgjc.com'):
            TMP=WSYY().getList_5(word.get())
        for j in TMP:
            Values=[]
            Values.append(j['title'])
            Values.append(i)
            Values.append(j['url'])
            tree.insert('','end',values=Values)
            num[0]=num[0]+1
            labelinf['text']='检索到：%d条 %d/5'%(num[0],num[1])
            root.update()
    except:
        pass
    num[1]=num[1]+1
    if(num[1]==5):
        labelinf['text']='检索到：%d条 检索完毕！'%(num[0])
    else:
        labelinf['text']='检索到：%d条 %d/5'%(num[0],num[1])
    root.update()

def download():
    threading.Thread(target=linking,args=('return',tree.item(sels[0])['values'][1],tree.item(sels[0])['values'][2])).start()
    
def pop(event):
    menubar.post(event.x_root,event.y_root)    
            
def search(*args):
    global frame2,tree,labelinf,num,menubar
    frame2=ttk.Frame(root)
    frame1.destroy()
    tree=ttk.Treeview(frame2,columns=['title','from'],show='headings')
    tree.heading('title',text='文件名')
    tree.heading('from',text='来源')
    tree.column('title',width=300)
    tree.column('from',width=100)
    yscrollbar = ttk.Scrollbar(frame2, orient=VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand = yscrollbar.set)
    yscrollbar.pack(side = RIGHT, fill = Y)
    tree.pack(fill='both',side=TOP,expand=1)
    tree.bind("<<TreeviewSelect>>", trefun)
    tree.bind("<Double-Button-1>",trerun)
    labelinf=ttk.Label(frame2,text="检索到：0条 0/5")
    labelinf.pack(fill='both',side=LEFT)
    ttk.Button(frame2,text="返回",command=init).pack(fill='both',side=RIGHT)
    
    frame2.pack(fill='both',expand=1)
    sourcelist=['sq688.com','wsyyxz.com','52flac.com','baiduonce.com','acgjc.com']
    num=[0,0]
    for i in sourcelist:
        threading.Thread(target=doing,args=(i,)).start()
    menubar=Menu(tree,tearoff = 0)
    menubar.add_command(label=['提取链接'],command=trerun)
    menubar.add_separator()
    menubar.add_command(label=['跳转网盘'],command=download)
    tree.bind("<Button-3>",pop)
    
    
def init():
    global frame1
    try:
        frame2.destroy()
    except:
        pass
    frame1=ttk.Frame(root)
    Label(frame1,text="无损音乐搜索神器",font=('',20)).pack(side=TOP)
    Label(frame1,text="@LMR 20190815",font=('',13)).pack(side=BOTTOM)
    Label(frame1,text=">配合PanDownload使用更佳",font=('',13)).pack(side=BOTTOM)
    Label(frame1,text="\n\n>多平台聚合搜索，双击一键获取提取链接",font=('',13)).pack(side=BOTTOM)
    entry=ttk.Entry(frame1,width=40,textvariable=word)
    entry.pack(side=LEFT)
    ttk.Button(frame1,text="搜索",command=search).pack(side=RIGHT)
    frame1.pack(expand=1)
    entry.focus_set()
    entry.bind('<KeyPress-Return>', search)


#主窗口
init()
root.mainloop()

