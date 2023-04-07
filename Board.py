import numpy as np
from tkinter import PhotoImage
from enum import Enum

class Board:
    class Direction(Enum):
        VERTICAL = 0
        HORIZONTAL = 1
        DOWNHILL = 2
        UPHILL = 3

    def __init__(self, size):
        self.pxSize = 571
        self.size = size
        self.pxStep = self.pxSize / (self.size - 1)
        self.boardImgPath = "img/board.png"
        self.whiteImgPath = "img/white.png"
        self.blackImgPath = "img/black.png"
        self.startCoord = np.asarray([21,23])
        self.board = np.ones([size,size])*-1
        self.boardImg = []
        self.stoneImgList = []

        self.winTarget = 5
        return

    def getNextMove(self, playerId):
        # computer player next move
        return
    
    def boardPos2Coord(self,x,y):
        coord = self.startCoord + np.asarray([x,y]) * self.pxStep
        return coord.tolist()
    
    def coord2BoardPos(self,coord):
        pos = (np.asarray(coord) - self.startCoord) / self.pxStep
        return np.rint(pos).tolist()
    
    def displayStone(self, canvas, playerId, coord):
        if playerId==0:
            self.stoneImgList.append(PhotoImage(file=self.blackImgPath))
        elif playerId==1:
            self.stoneImgList.append(PhotoImage(file=self.whiteImgPath))
        canvas.create_image(coord,image=self.stoneImgList[len(self.stoneImgList)-1])
    
    def displayBoard(self, canvas):
        self.boardImg.append(PhotoImage(file=self.boardImgPath))
        canvas.create_image(310,310,image=self.boardImg)

        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x]==-1:
                     continue
                self.displayStone(canvas,self.board[y][x],self.boardPos2Coord(x,y))

        return
    
    def getDirArrayAndPos(self,dir,curPos,addCheck):
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
    
    def isNConnected(self,arr,playerId,pos):
        if (arr.size < self.winTarget):
            return False
        
        connected = 0
        for i in range(arr.size):
            if(arr[i]==playerId):
                connected = connected + 1
            else:
                connected = 0
            if(connected==self.winTarget):
                return True

        return False
    
    def isPlayerWon(self,playerId,lastPlayCoord):
        # Check 4 directions, each direction check +/- self.winTarget-1, total 2*self.winTarget-2 cells
        # 1. top-to-bottom
        arr,_ = self.getDirArrayAndPos(Board.Direction.VERTICAL,lastPlayCoord,0)
        if(self.isNConnected(arr,playerId,lastPlayCoord)):  
            return True
        
        # 2. left-to-right
        arr,_ = self.getDirArrayAndPos(Board.Direction.HORIZONTAL,lastPlayCoord,0)
        if(self.isNConnected(arr,playerId,lastPlayCoord)):  
            return True
        
        # 3. top-left-to-bottom-right
        arr,_ = self.getDirArrayAndPos(Board.Direction.DOWNHILL,lastPlayCoord,0)
        if(self.isNConnected(arr,playerId,lastPlayCoord)):  
            return True
        
        # 4. bottom-left-to-top-right
        arr,_ = self.getDirArrayAndPos(Board.Direction.UPHILL,lastPlayCoord,0)
        if(self.isNConnected(arr,playerId,lastPlayCoord)):  
            return True
      
        return False   

    
# def getDir(dir,curPos,win,addi):
#     size = 10
#     winTarget = win+addi
#     arr = None
#     pos = -1
#     start = 0
#     end = size
#     if (dir == 0):
#         arr = a[:,curPos[0]] # extract whole column
#         pos = curPos[1]
#     elif (dir == 1):
#         arr = a[curPos[1],:] # extract whole row
#         pos = curPos[0]
#     elif (dir == 2):
#         diff = curPos[1]-curPos[0]
#         startX = max(0,-diff)
#         startY = max(0,diff)
#         arrSize = size - abs(diff)
#         arr = np.empty(arrSize)
#         for i in range(arrSize):
#             arr[i] = a[startY+i][startX+i]
#         pos = curPos[0] - startX
#     elif (dir == 3):
#         yDiff = size - 1 - curPos[1]
#         startX = max(0,curPos[0] - yDiff)
#         startY = min(size-1,curPos[0]+curPos[1])
#         arrSize = abs(startX-startY)+1
#         arr = np.empty(arrSize)
#         for i in range(arrSize):
#             arr[i] = a[startY-i][startX+i]
#         pos = curPos[0] - startX
#     start = max(0,pos-winTarget+1)
#     end = min(size,pos+winTarget)
#     arr = arr[start:end]
#     pos = pos - start
#     return [arr,pos]

