from ZIMU import *

from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog

import threading#多线程下载

root=Tk()
root.title("字幕下载器")
root.geometry("700x300")


word= StringVar()
totalnum=0
nownum=0
pbar=ttk.Progressbar(root)

def downloader(url,savepath):
    try:
        global totalnum,nownum
        pbar.pack(fill='both',expand=1)
        load=requests.get(url,stream=True)
        totalnum=totalnum+int(load.headers['Content-Length'])#获取文件总大小
        pbar["maximum"]=totalnum
        with open(savepath+"/"+load.headers['content-disposition'].split('"')[1], "wb") as f:
            for chunk in load.iter_content(chunk_size=1024):
                nownum=nownum+1024
                f.write(chunk)
                pbar["value"] =nownum
                root.update()
        totalnum=totalnum-int(load.headers['Content-Length'])
        nownum=nownum-int(load.headers['Content-Length'])
        tkinter.messagebox.showinfo("下载成功","已保存%s"%(load.headers['content-disposition'].split('"')[1]))
        if(totalnum==0):
            pbar.pack_forget()
        else:
            pbar["maximum"]=totalnum
            pbar["value"] =nownum
            root.update()
    except:
        tkinter.messagebox.showerror("下载失败","下载失败")
                    
def trefun(event):
    global sels
    sels= event.widget.selection()#event.widget获取Treeview对象，调用selection获取选择对象名称

def trerun(event):
    try:
        savepath=tkinter.filedialog.askdirectory(title ='保存目录')
        if (savepath!=''):
            for idx in sels:
                threading.Thread(target=downloader,args=(getLink(tree.item(idx)['values'][4]),savepath,)).start()
    except:
        pass
                



def search():
    global frame2,tree
    frame2=ttk.Frame(root)
    frame1.destroy()
    tree=ttk.Treeview(frame2,columns=['movtitle','subtitle','rank','dsum'],show='headings')
    tree.heading('movtitle',text='电影名')
    tree.heading('subtitle',text='字幕标题')
    tree.heading('rank',text='评分')
    tree.heading('dsum',text='下载量')
    tree.column('movtitle',width=300)
    tree.column('subtitle',width=300)
    tree.column('rank',width=50)
    tree.column('dsum',width=50)
    tree.pack(fill='both',side=TOP,expand=1)
    tree.bind("<<TreeviewSelect>>", trefun)
    tree.bind("<Double-Button-1>",trerun)
    ttk.Button(frame2,text="返回",command=init).pack(side=BOTTOM)
    frame2.pack(fill='both',expand=1)
    TMP=getList(word.get())
    for i in TMP:
        for j in i['detail']:
            Values=[]
            Values.append(i['title'])
            Values.append(j['title'])
            Values.append(j['rank'])
            Values.append(j['dsum'])
            Values.append(j['linkid'])
            tree.insert('','end',values=Values)
    
def init():
    global frame1
    try:
        frame2.destroy()
    except:
        pass
    frame1=ttk.Frame(root)
    Label(frame1,text="轻量版字幕下载器",font=('',20)).pack(side=TOP)
    Label(frame1,text="@LMR 20190726",font=('',13)).pack(side=BOTTOM)
    ttk.Entry(frame1,width=50,textvariable=word).pack(side=LEFT)
    ttk.Button(frame1,text="搜索",command=search).pack(side=RIGHT)
    frame1.pack(expand=1)
    
#主窗口
init()
root.mainloop()

