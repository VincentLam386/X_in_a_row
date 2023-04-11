import numpy as np
from tkinter import PhotoImage
from enum import Enum

class Board:
    """
    A class to represent the gameboard

    Attributes
    ----------




    Methods
    -------

    
    

    
    """

    class Direction(Enum):
        VERTICAL = 0
        HORIZONTAL = 1
        DOWNHILL = 2
        UPHILL = 3

    __pxSize = 571
    __boardImgPath = "img/board.png"
    __whiteImgPath = "img/white.png"
    __blackImgPath = "img/black.png"
    __boardImgStartCoord = np.asarray([21,23])

    def __init__(self, size, winRequirement):
        if (size<3):
            raise ValueError(f"Board size must be at least 3. Input size = {size}")
        self._size = size
        self._pxStep = Board.__pxSize / (self.size - 1)
        
        self._board = np.ones([size,size])*-1
        self.boardImg = []
        self.stoneImgList = []

        if (winRequirement < 3):
            raise ValueError(f"Win requirement must be at least 3. Input win requirement = {winRequirement}")
        if (size < winRequirement):
            raise ValueError(f"Win requirement must be smaller than gameboard size. Input size = {size}, winRequirement = {winRequirement}")
        self._winTarget = winRequirement
        return
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self,size):
        if (size<3):
            raise ValueError(f"Board size must be at least 3. Input size = {size}")
        self._size = size
        return
    
    @property
    def winTarget(self):
        return self._winTarget
    
    @winTarget.setter
    def winTarget(self,winRequirement):
        if (winRequirement < 3):
            raise ValueError(f"Win requirement must be at least 3. Input win requirement = {winRequirement}")
        if (self.size < winRequirement):
            raise ValueError(f"Win requirement must be smaller than gameboard size. Input size = {self.size}, winRequirement = {winRequirement}")
        self._winTarget = winRequirement
        return
    
    @property
    def board(self):
        return self._board
    
    def __str__(self):
        return f"""
        Gameboard:
            Size: {self.size} x {self.size} grids
            Win requirement: {self.winTarget} consecutive stones
        """
    
    def __repr__(self):
        return f"Board(size='{self.size}', winTarget='{self.winTarget}')"

# Getting coordinates
    def boardPos2Coord(self,x,y):
        coord = Board.__boardImgStartCoord + np.asarray([x,y]) * self._pxStep
        return coord.tolist()
    
    def coord2BoardPos(self,coord):
        pos = (np.asarray(coord) - Board.__boardImgStartCoord) / self._pxStep
        return np.rint(pos).tolist()
    
# display graphics
    def displayStone(self, canvas, playerId, coord):
        if playerId==0:
            self.stoneImgList.append(PhotoImage(file=Board.__blackImgPath))
        elif playerId==1:
            self.stoneImgList.append(PhotoImage(file=Board.__whiteImgPath))
        canvas.create_image(coord,image=self.stoneImgList[len(self.stoneImgList)-1])
        return

    def displayBoard(self, canvas):
        self.boardImg.append(PhotoImage(file=Board.__boardImgPath))
        canvas.create_image(310,310,image=self.boardImg)

        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x]==-1:
                     continue
                self.displayStone(canvas,self.board[y][x],self.boardPos2Coord(x,y))
        return

# utilities
    def _getDirArrayAndPos(self,dir,curPos,addCheck):
        size = self.size
        extendLen = self.winTarget+addCheck
        arr = None
        pos = -1
        curPos[0] = int(curPos[0])
        curPos[1] = int(curPos[1])
        # extract whole column/row/diagonal
        if (dir == Board.Direction.VERTICAL):
            arr = self.board[:,curPos[0]] 
            pos = curPos[1]
        elif (dir == Board.Direction.HORIZONTAL):
            arr = self.board[curPos[1],:] 
            pos = curPos[0]
        elif (dir == Board.Direction.DOWNHILL):
            diff = curPos[1]-curPos[0]
            startX = max(0,-diff)
            startY = max(0,diff)
            arrSize = size - abs(diff)
            arr = np.empty(arrSize)
            for i in range(arrSize):
                arr[i] = self.board[startY+i][startX+i]
            pos = curPos[0] - startX
        elif (dir == Board.Direction.UPHILL):
            yDiff = size - 1 - curPos[1]
            startX = max(0,curPos[0] - yDiff)
            startY = min(size-1,curPos[0]+curPos[1])
            arrSize = abs(startX-startY)+1
            arr = np.empty(arrSize)
            for i in range(arrSize):
                arr[i] = self.board[startY-i][startX+i]
            pos = curPos[0] - startX
        
        # extract required number of data
        start = max(0,pos-extendLen+1)
        end = min(size,pos+extendLen)
        arr = arr[start:end]
        pos = pos - start

        return [arr,pos]
    
    @classmethod
    def _isNConnected(self,arr,playerId,pos,n):
        if (arr.size < n):
            return False
        
        connected = 0
        checkStart = max(0,pos - n + 1)
        checkEnd = min(pos + n,arr.size)
        for i in range(checkStart,checkEnd):
            if(arr[i]==playerId):
                connected = connected + 1
            else:
                connected = 0
            if(connected==n):
                return True

        return False
    
# main game logics 
    def isPlayerWon(self,playerId,lastPlayCoord):
        # Check 4 directions, each direction check +/- self.winTarget-1, total 2*self.winTarget-2 cells
        # 1. top-to-bottom
        arr,pos = self._getDirArrayAndPos(Board.Direction.VERTICAL,lastPlayCoord,0)
        if(Board._isNConnected(arr,playerId,pos,self.winTarget)):  
            return True
        
        # 2. left-to-right
        arr,pos = self._getDirArrayAndPos(Board.Direction.HORIZONTAL,lastPlayCoord,0)
        if(Board._isNConnected(arr,playerId,pos,self.winTarget)):  
            return True
        
        # 3. top-left-to-bottom-right
        arr,pos = self._getDirArrayAndPos(Board.Direction.DOWNHILL,lastPlayCoord,0)
        if(Board._isNConnected(arr,playerId,pos,self.winTarget)):  
            return True
        
        # 4. bottom-left-to-top-right
        arr,pos = self._getDirArrayAndPos(Board.Direction.UPHILL,lastPlayCoord,0)
        if(Board._isNConnected(arr,playerId,pos,self.winTarget)):  
            return True
      
        return False   
    
    def ruleRenjuBoard(self):
        # prohibit black 3-and-3, 4-and-4, overline

        return
    
    def ruleSwap2Board(self):

        return

# computer player
    def getNextMove(self, playerId):
        # computer player next move
        
        return
    