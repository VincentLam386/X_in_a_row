from Timer import Timer

class Player:
    def __init__(self, id, maxTime, addTime):
        self.id = id
        self.timer = Timer(maxTime, addTime, id)
        return
    
    def initTimerBar(self, frame, length):
        self.timer.initTimerBar(frame,length)
        return
    
    @property
    def getTimerBar(self):
        return self.timer.getTimerBar
    
    def startTimerThread(self):
        self.timer.startThread()
        return
    
    def startTimerCount(self):
        self.timer.startCountDown()
        return
    
    def stopTimerCount(self):
        self.timer.stopCountDown()
        return


