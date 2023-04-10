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
    timerStep = 0.5

    def __init__(self, maxTime, addTime, timerId):
        if (maxTime<0):
            raise ValueError(f"Time must be positive. Input maxTime = {maxTime}")
        self._maxTime = maxTime
        self._time = maxTime
        if (addTime<0):
            raise ValueError(f"Time add must be positive. Input addTime = {addTime}")
        self._addTime = addTime

        self.timerBar = ttk.Progressbar()

        self._styleName = 'text.Horizontal.TProgressbar' + str(timerId)
        self._style = ttk.Style()
        self._style.layout(self._styleName,
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
        self._style.configure(self._styleName, text="{:.1f}".format(self.maxTime))

        self._timeOutEvent = Event()
        self._pauseEvent = Event()
        #self._countingEvent = Event()
        #self._countingEvent.set()

        self.countDownThread = Thread(target=self.countDown)
        self.countDownThread.start()

        self._stopThreadFlag = False       
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
        self.resetTimer()
        return
    
    def addCountDownTime(self):
        self._time = self._time + self.addTime
        self.updateTimerBar()
        return
    
    def countDown(self):
        while(not self._stopThreadFlag):
            self._pauseEvent.wait()
            #self._countingEvent.clear()
            time.sleep(Timer.timerStep)
            self._time = self._time - Timer.timerStep
            self.updateTimerBar()
            if(self.isNoTime()):
                self._timeOutEvent.set()
                self.pauseTimer()

            #self._countingEvent.set()
            
        return

    def updateTimerBar(self):
        self._style.configure(self._styleName, text="{:.1f}".format(self._time))
        if(self._time >= self.maxTime):
            self.timerBar['value'] = self.maxTime
        else:
            self.timerBar['value'] = self._time
        return
    
    def isNoTime(self):
        return (self._time < (Timer.timerStep/2))
    
    def waitAndResetTimeOutEvent(self):
        self._timeOutEvent.wait()
        self._timeOutEvent.clear()
        return
    
    def resetTimer(self):
        #self._countingEvent.wait()
        self._time = self.maxTime
        self.timerBar['value'] = self._time
        self._style.configure(self._styleName, text="{:.1f}".format(self._time))
        self._timeOutEvent.clear()
        self.pauseTimer()
        return
    
    def pauseTimer(self):
        self._pauseEvent.clear()
        return
    
    def resumeTimer(self):
        self._pauseEvent.set()
        return
    
    # def startTimer(self):
    #     self.countDownThread.start()
    #     return
    
    # def stopTimer(self):
    #     self._stopThreadFlag = True
    #     return
    
    # def waitThreadFinish(self):
    #     self.countDownThread.join()
    #     return

