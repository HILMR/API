from tkinter import *
from tkinter import ttk

"""扩展对话框库，美化对话框风格
@LMR v1.0
"""
class exDialog(object):
    def __init__(self,win):
        self.win=win
        self.back=None

    def notice(self,Title,Text,t,cmd=None,*i):
        """win10提醒风格，Title标题，Text提示文字，t停留时间"""
        fps=int(1000/100)
        if(len(i)==0):
            top=Toplevel(self.win,bg='black')
            top.overrideredirect(True)#设置无框窗体
            top.attributes("-alpha", 0.8)
            top.wm_attributes('-topmost',1)
            Label(top,text=Title,font=('微软雅黑','20','bold'),bg='black',fg='white').pack()
            Label(top,text=Text,font=('微软雅黑','15'),bg='black',fg='white',justify='left').pack(anchor=W)
            top.update()
            h=top.winfo_height()
            if(h<50):
                h=50
            w=top.winfo_width()
            if(w<300):
                w=300
            ii=top.winfo_screenwidth()
            ty=0
        else:
            ii=i[0]
            h=i[1]
            w=i[2]
            top=i[3]
            ty=i[4]
        #执行命令
        if(ty==2):
            if(cmd!=None):
                try:
                    cmd[0](cmd[1])
                except:
                    pass
            ty=1
        top.geometry("%dx%d+%d+%d"%(w,h,ii,top.winfo_screenheight()-h-50))
        top.update()
        if(ty==0):
            ii-=w/(200/fps)
            if(ii>(top.winfo_screenwidth()-w-10)):
                self.win.after(fps,lambda:self.notice(Title,Text,t,cmd,ii,h,w,top,ty))
            else:
                ty=1
                top.bind("<Button-1>",lambda event:self.notice(Title,Text,t,cmd,ii,h,w,top,2,event))
                if(t>0):
                    self.win.after(t,lambda:self.notice(Title,Text,t,cmd,ii,h,w,top,ty))
        else:
            ii+=w/(200/fps)
            if(ii<top.winfo_screenwidth()):
                self.win.after(fps,lambda:self.notice(Title,Text,t,cmd,ii,h,w,top,ty))
            else:
                top.destroy()

    def msgbox_cmd(self,Type,Top,i):
        fps=int(1000/100)
        if(Type==11):
            self.back=True
            self.msgbox_cmd(0,Top,i)
        elif(Type==10):
            self.back=False
            self.msgbox_cmd(0,Top,i)
        elif(Type==0):
            Top.attributes("-alpha", i)
            Top.update()
            i-=0.8/(500/fps)
            if(i>0):
                self.win.after(fps,lambda:self.msgbox_cmd(0,Top,i))
            else:
                Top.destroy()

    def msgbox_fre(self,Title,Text,Type,ii,top):
        fps=int(1000/100)
        top.attributes("-alpha", ii)
        top.update()
        ii+=0.8/(500/fps)
        if(ii<0.8):
            self.win.after(fps,lambda:self.msgbox_fre(Title,Text,Type,ii,top))

    def msgbox(self,Title,Text,Type,WH):
        top=Toplevel(self.win,bg='black')
        top.overrideredirect(True)#设置无框窗体
        top.wm_attributes('-topmost',1)
        self.win.update()
        if(WH==[]):
            top.geometry("%dx%d+%d+%d"%(self.win.winfo_width()+5,self.win.winfo_height()+35,self.win.winfo_x()+5,self.win.winfo_y()))
        else:
            top.geometry("%dx%d+%d+%d"%(WH[0],WH[1],WH[2],WH[3]))
        Label(top,text=Title,font=('微软雅黑','30','bold'),bg='black',fg='white').pack(expand=1)
        Label(top,text=Text,font=('微软雅黑','20'),bg='black',fg='white').pack(expand=1)
        if(Type==0):
            ttk.Button(top,text='确认',command=lambda:self.msgbox_cmd(0,top,0.7)).pack(expand=1)
        elif(Type==1):
            frame=Frame(top,bg='black')
            ttk.Button(frame,text='是',command=lambda:self.msgbox_cmd(11,top,0.7)).grid(row=0,column=0,padx=5)
            ttk.Button(frame,text='否',command=lambda:self.msgbox_cmd(10,top,0.7)).grid(row=0,column=1,padx=5)
            frame.pack(expand=1)
        else:
            ttk.Button(top,text='确认').pack(expand=1)
        self.msgbox_fre(Title,Text,Type,0,top)
        top.wait_window()
        return self.back
        
        
