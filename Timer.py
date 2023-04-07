from threading import *
import time
from tkinter import ttk

class Timer:
    def __init__(self, maxTime, addTime, timerId):
        self.maxTime = maxTime
        self.time = maxTime
        self.addTime = addTime
        self.timerBar = ttk.Progressbar()
        self.startCountEvent = Event()
        self.styleName = 'text.Horizontal.TProgressbar' + str(timerId)
        self.style = ttk.Style()
        self.style.layout(self.styleName,
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure(self.styleName, text="{:.1f}".format(self.maxTime))

        return

    def initTimerBar(self, frame, length):
        self.timerBar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", 
                                        style=self.styleName, length=length, maximum=self.maxTime)
        self.timerBar['value'] = self.maxTime
        #self.timerBar.config('text.Horizontal.TProgressbar',text=int(self.time))
        return
    
    @property
    def getTimerBar(self):
        return self.timerBar
    
    def startThread(self):
        t1 = Thread(target=self.countDown)
        t1.start()
        return
    
    def startCountDown(self):
        self.startCountEvent.set()
        return
    
    def stopCountDown(self):
        self.startCountEvent.clear()
        self.time = self.time + self.addTime
        self.updateTimerBar()
        return
    
    def countDown(self):
        while(self.time > 0):
            self.startCountEvent.wait()
            time.sleep(0.1)
            self.time = self.time - 0.1
            self.updateTimerBar()
        return

    def updateTimerBar(self):
        self.style.configure(self.styleName, text="{:.1f}".format(self.time))
        if(self.time >= self.maxTime):
            self.timerBar['value'] = self.maxTime
        else:
            self.timerBar['value'] = self.time
        return

