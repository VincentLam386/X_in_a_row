from threading import *
import time
from tkinter import ttk

class Timer:
    """
    A class to represent the countdown timer

    Attributes
    ----------




    Methods
    -------

    
    
    
    
    
    
    """
    def __init__(self, maxTime, addTime, timerId):
        if (maxTime<0):
            raise ValueError(f"Time must be positive. Input maxTime = {maxTime}")
        self._maxTime = maxTime
        self._time = maxTime
        if (addTime<0):
            raise ValueError(f"Time add must be positive. Input addTime = {addTime}")
        self._addTime = addTime

        self.timerBar = ttk.Progressbar()

        self._startCountEvent = Event()
        self._styleName = 'text.Horizontal.TProgressbar' + str(timerId)
        self._style = ttk.Style()
        self._style.layout(self._styleName,
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
        self._style.configure(self._styleName, text="{:.1f}".format(self.maxTime))
        return
    
    @property
    def maxTime(self):
        return self._maxTime

    @maxTime.setter
    def maxTime(self,maxTime):
        if (maxTime<0):
            raise ValueError(f"Time must be positive. Input maxTime = {maxTime}")
        self._maxTime = maxTime
        return
    
    @property
    def addTime(self):
        return self._addTime
    
    @addTime.setter
    def addTime(self,addTime):
        if (addTime<0):
            raise ValueError(f"Time add must be positive. Input addTime = {addTime}")
        self._addTime = addTime
        return
    
    def __str__(self):
        return f"""
                Timer:
                    Max time: {self.maxTime}s
                    Current time: {self._time}s
                    Additional time after each move: {self.addTime}s
        """
    
    def __repr__(self):
        return f"Timer(maxTime='{self.maxTime}', time='{self._time}', addTime='{self.addTime}')"

    def initTimerBar(self, frame, length):
        self.timerBar = ttk.Progressbar(frame, orient="horizontal", mode="determinate", 
                                        style=self._styleName, length=length, maximum=self.maxTime)
        self.timerBar['value'] = self.maxTime
        return
    
    def startThread(self):
        t1 = Thread(target=self.countDown)
        t1.start()
        return
    
    def startCountDown(self):
        self._startCountEvent.set()
        return
    
    def stopCountDown(self):
        self._startCountEvent.clear()
        self._time = self._time + self.addTime
        self.updateTimerBar()
        return
    
    def countDown(self):
        while(self._time > 0):
            self._startCountEvent.wait()
            time.sleep(0.1)
            self._time = self._time - 0.1
            self.updateTimerBar()
        return

    def updateTimerBar(self):
        self._style.configure(self._styleName, text="{:.1f}".format(self._time))
        if(self._time >= self.maxTime):
            self.timerBar['value'] = self.maxTime
        else:
            self.timerBar['value'] = self._time
        return

