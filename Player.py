from Timer import Timer
from threading import Thread, Event

class Player:
    """
    A class to represent the player

    Attributes
    ----------




    Methods
    -------

    
    
    
    
    
    
    """
    __eventTimeOut = 1

    def __init__(self, id, maxTime, addTime, placeButton):
        self.id = id
        self.timer = Timer(maxTime, addTime, id)
        self.selectPos = None

        # for computer player
        self.isComputer = False
        self._computerThread = None
        self._placeButton = placeButton
        self._stopComputerFlag = True
        self._startComputerEvent = Event()
        self._computerFinishEvent = Event()
        return
    
    def __str__(self):
        return f"""
        Player:
            ID: {self.id}
            Timer: {self.timer}
        """
    
    def __repr__(self):
        return f"Player(id='{self.id}', timer={repr(self.timer)})"
      
    def getTimer(self):
        return self.timer
    
    def getTimerBar(self):
        return self.timer.timerBar
    
    def setNormalPlayer(self):
        if(not self.isComputer):
            return
        self.stopComputerPlayer()
        self._computerThread.join()
        self._computerThread = None
        self._stopComputerFlag = True
        self.isComputer = False
        return
    
    def setComputerPlayer(self,gameBoard,isRecordTime):
        if(self.isComputer):
            return
        self.isComputer = True
        self._stopComputerFlag = False
        self._computerThread = Thread(target=lambda gb=gameBoard,bu=self._placeButton,rt=isRecordTime:self._computerPlayerThread(gb,bu,rt))
        self._computerThread.start()
        return
    
    def startComputerPlayer(self):
        self._startComputerEvent.set()
        return
    
    def stopComputerPlayer(self):
        self._stopComputerFlag = True
        return
    
    def _computerPlayerThread(self,gameBoard,placeButton,isRecordTime):
        opponentId = (self.id+1)%2
        while(not self._stopComputerFlag):
            self._startComputerEvent.wait(Player.__eventTimeOut)
            if(self._startComputerEvent.is_set()):
                self.selectPos = gameBoard.getNextMove(self.id,opponentId,isRecordTime)
                placeButton.invoke()
                self._computerFinishEvent.set()
                self._startComputerEvent.clear()
            
        return


