import numpy as np
from tkinter import PhotoImage
import time

class Board:
    def __init__(self, size):
        self.pxSize = 571
        self.size = size
        self.pxStep = self.pxSize / (self.size - 1)
        self.boardImgPath = "img/board.png"
        self.whiteImgPath = "img/white.png"
        self.blackImgPath = "img/black.png"
        self.startCoord = np.asarray([21,23])
        self.board = np.zeros([size,size])
        self.boardImg = []
        self.stoneImgList = []
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
        if playerId==1:
            self.stoneImgList.append(PhotoImage(file=self.blackImgPath))
        elif playerId==2:
            self.stoneImgList.append(PhotoImage(file=self.whiteImgPath))
        canvas.create_image(coord,image=self.stoneImgList[len(self.stoneImgList)-1])
    
    def displayBoard(self, canvas):
        self.boardImg.append(PhotoImage(file=self.boardImgPath))
        canvas.create_image(310,310,image=self.boardImg)
        #time.sleep(0.5)

        #count = 0
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x]==0:
                     continue
                self.displayStone(canvas,self.board[y][x],self.boardPos2Coord(x,y))

        return
    

    



    

