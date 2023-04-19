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

    def __init__(self, id, maxTime, addTime, isComputer, gameBoard=None, placeButton=None):
        self.id = id
        self.timer = Timer(maxTime, addTime, id)
        self.selectPos = None

        self.isComputer = isComputer
        if(isComputer):
            self._computerThread = Thread(target=lambda gb=gameBoard,bu=placeButton:self._computerPlayerThread(gb,bu))
            self._computerThread.start()
            self._stopComputerFlag = False
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
    
    def startComputerPlayer(self):
        self._startComputerEvent.set()
        return
    
    def stopComputerPlayer(self):
        self._stopComputerFlag = True
        return
    
    def _computerPlayerThread(self,gameBoard,placeButton):
        while(not self._stopComputerFlag):
            self._startComputerEvent.wait(Player.__eventTimeOut)
            if(self._startComputerEvent.is_set()):
                self.selectPos = gameBoard.getNextMove(self.id,0)
                placeButton.invoke()
                self._computerFinishEvent.set()
                self._startComputerEvent.clear()
            
        return


