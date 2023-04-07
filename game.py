from tkinter import *
import tkinter.font as font
from tkinter import ttk
import numpy as np
from Board import Board
from Player import Player
from threading import *
import time

class Game:
    def __init__(self, boardSize, timeLimit, addTime):
        self.numPlayers = 2

        self.root = Tk()
        self.frm = ttk.Frame(self.root, width=700, height=650, padding=10)
        self.canvas = Canvas(self.frm,width=620,height=620)
        
        self.selectPos = None
        self.selectBoxImgPath = ["img/box1.png","img/box2.png"]
        self.selectBoxImg = [PhotoImage(file=self.selectBoxImgPath[0]),PhotoImage(file=self.selectBoxImgPath[1])]
        self.selectBox = [None,None]

        self.gameBoard = Board(boardSize)

        self.players = []
        self.playersButton = []
        for i in range(self.numPlayers):
             self.players.append(Player(i,timeLimit,addTime))
             self.playersButton.append(
                  Button(self.frm, text="Player"+str(i+1), 
                        fg="green" if(i==0) else "red", 
                        command=lambda info=self.players[i].id:self.placeStone(info)))
             
             self.players[i].initTimerBar(self.frm,600)
             self.players[i].startTimerThread()
        
        self.gameStartButton = Button(self.frm, text="Game Start!", width=20, command=self.gameStart)
        self.gameStartButton['font'] = font.Font(family='Helvetica',size=30,weight="bold")

        self.turn = 0

        self.initView()

    def initView(self):
        self.root.geometry("800x750")
        
        self.frm.pack()
        self.frm.place(anchor='center', relx=0.5, rely=0.5)
        
        self.players[1].getTimerBar.grid(column=0,row=0,padx=0,pady=0)
        self.playersButton[1].grid(column=0,row=1,padx=0,pady=0)

        self.canvas.grid(column=0,row=2,padx=0,pady=0)
        self.canvas.bind("<Button-1>",self.onBoardClick)

        self.playersButton[0].grid(column=0,row=3,padx=0,pady=0)
        self.players[0].getTimerBar.grid(column=0,row=4,padx=0,pady=0)

        self.gameStartButton.grid(row=2)
        self.gameStartButton.lift()


        # self.gameBoard.board[4][10] = 2
        # self.gameBoard.board[6][8] = 2
        # self.gameBoard.board[12][10] = 2
        # self.gameBoard.board[14][0] = 2
        # self.gameBoard.board[2][5] = 1
        # self.gameBoard.board[9][6] = 1
        # self.gameBoard.board[11][11] = 1
        # self.gameBoard.board[14][14] = 1

        self.gameBoard.displayBoard(self.canvas)

    def onBoardClick(self,event):
        if (self.selectBox[self.turn] != None):
            self.canvas.delete(self.selectBox[self.turn])
        pos = self.gameBoard.coord2BoardPos([event.x,event.y])
        if (pos[0] >= self.gameBoard.size or pos[1] >= self.gameBoard.size):
             return
        self.selectPos = pos
        coord = self.gameBoard.boardPos2Coord(self.selectPos[0],self.selectPos[1])
        self.selectBox[self.turn] = self.canvas.create_image(coord,image=self.selectBoxImg[self.turn])
        return

    def placeStone(self,playerId):
            if(self.selectPos == None or playerId != self.turn):
                 return
            
            x = int(self.selectPos[0])
            y = int(self.selectPos[1])
            if (self.gameBoard.board[y][x] == 0):
                self.gameBoard.board[y][x] = playerId + 1
                self.gameBoard.displayStone(self.canvas,playerId,self.gameBoard.boardPos2Coord(x,y))
                self.canvas.delete(self.selectBox[self.turn])

                self.players[self.turn].stopTimerCount()
                self.turn = (self.turn + 1) % 2
                self.players[self.turn].startTimerCount()

            return
    
    def gameStart(self):
         self.players[self.turn].startTimerCount()
         self.gameStartButton.grid_forget()

         return



game = Game(boardSize=15,timeLimit=60,addTime=3)
game.root.mainloop()
