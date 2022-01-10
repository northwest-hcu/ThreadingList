import threading
from time import sleep
import time
import PySimpleGUI as psg

class ThreadListWindow:
    def __init__(self,ThreadList,name,x=None,y=None,timeout=None):
        self.ThreadList=ThreadList
        self.name=name
        self.x=x
        self.y=y
        self.flag=True
        self.timeout=timeout
        self.startTime=None
        #デザイン設定
        psg.theme('Dark 2')

    def start(self):
        layout=list()
        lines=list()
        for key in self.ThreadList.threads.keys():
            if key=='ThreadListWindow':
                continue
            lines.append(str(key)+' : '+str(self.ThreadList.statusThread(key)))
        lines=str("\n".join(lines))
        layout.append([psg.Text(lines,key='ThreadList')])
        layout=tuple(layout)
        self.window=psg.Window("ThreadList:"+str(self.name),layout,size=(200,300),location=(self.x,self.y))
        t=time.time()
        while True:
            event,values=self.window.read(timeout=10)
            if event == psg.WINDOW_CLOSED or self.flag==False:
                break
            self.reload()
        self.window.close()

    def reload(self):
        lines=list()
        self.ThreadList.cleanThreads()
        for key in self.ThreadList.threads.keys():
            if key=='ThreadListWindow':
                continue
            lines.append(str(key)+' : '+str(self.ThreadList.statusThread(key)))
        if self.timeout is not None:
            if len(lines)==0 and self.startTime is None:
                self.startTime=time.time()
            elif len(lines)==0 and self.startTime is not None:
                if time.time()-self.startTime>self.timeout:
                    print('ThreadListWindow is timeout. ('+str(self.timeout)+'s)')
                    self.quit()
            else:
                self.startTime=None
        lines=str("\n".join(lines))
        self.window['ThreadList'].update(lines)

    def quit(self):
        self.flag=False
        del self

class ThreadList:
    def __init__(self):
        self.threads=dict()

    def addThread(self,name,func,*args):
        try:
            self.cleanThreads()
            if name in self.threads.keys():
                print('\tThe thread name ['+str(name)+'] is already used.')
                return False
            t=threading.Thread(target=func,args=args,daemon=True,name=str(name))
            t.start()
            self.threads[name]=t
            print('\tExecute process ['+str(name)+'].')
            return True
        except Exception as err:
            print('\tProcess ['+name+'] is error.')
            print('\tError is '+str(err))
            if name in self.threads.keys():
                del self.threads[name]
            return False

    def waitThreads(self):
        arr=list()
        for name in self.threads.keys():
            if self.threads[name].is_alive():
                arr.append(name)
        for name in arr:
            if name=='ThreadListWindow' or name not in self.threads.keys():
                continue
            print('\tWaiting ['+str(name)+']')
            self.threads[name].join()
            while self.threads[name].is_alive():
                sleep(0.01)

    def statusThread(self,name):
        if name not in self.threads.keys():
            print('\tThe process ['+str(name)+'] is not found.')
            return False
        t=self.threads[name]
        if t.is_alive():
            return True
        else:
            return False

    def showThreads(self):
        print('\t--Now threads--')
        self.cleanThreads()
        for name in self.threads.keys():
            if name=='ThreadListWindow':
                continue
            status=self.statusThread(name)
            print('\t['+name+']>>'+str(status))

    def viewThreads(self,name,timeout):
        if 'ThreadListWindow' not in self.threads.keys():
            tw=ThreadListWindow(self,name,timeout=timeout)
            self.addThread('ThreadListWindow',tw.start)
        else:
            print('\tThreadListWindow has already done.')

    def cleanThreads(self):
        arr=list()
        for name in self.threads.keys():
            if not self.threads[name].is_alive():
                arr.append(name)
        for name in arr:
            del self.threads[name]

def bigFunc(list):
    num=list[0]
    t=list[2]
    print('start:'+str(num))
    sleep(list[1])
    print('stop:'+str(num))
    print(str(int(time.time()-t)/60)+'分経過')

if __name__=="__main__":
    t=time.time()
    tl=ThreadList()
    tl.addThread('bigFunc1',bigFunc,(1,10,t))
    tl.addThread('bigFunc2',bigFunc,(2,20,t))
    tl.addThread('bigFunc3',bigFunc,(3,10,t))
    tl.viewThreads('test',None)
    tl.waitThreads()
    tl.addThread('bigFunc4',bigFunc,(3,10,t))
    tl.waitThreads()
    print(str(int(time.time()-t)/60)+'分')
