from Timer import Timer

class Player:
    """
    A class to represent the player

    Attributes
    ----------




    Methods
    -------

    
    
    
    
    
    
    """
    def __init__(self, id, maxTime, addTime):
        self.id = id
        self.timer = Timer(maxTime, addTime, id)
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
