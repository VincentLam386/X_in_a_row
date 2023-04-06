from tkinter import *
from tkinter import ttk
import numpy as np
from Board import Board
from Player import Player

class Game:
    def __init__(self, boardSize):
        self.root = Tk()
        self.frm = ttk.Frame(self.root, width=700, height=650, padding=10)
        self.canvas = Canvas(self.frm,width=620,height=620)
        
        self.selectPos = None
        self.selectBoxImgPath = ["img/box1.png","img/box2.png"]
        self.selectBoxImg = [PhotoImage(file=self.selectBoxImgPath[0]),PhotoImage(file=self.selectBoxImgPath[1])]
        self.selectBox = [None,None]

        self.gameBoard = Board(boardSize)
        self.player1 = Player(1)
        self.player2 = Player(2)
        self.player1Button = Button(self.frm, text="Player1", fg="green", command=lambda info=self.player1.id:self.placeStone(info))
        self.player2Button = Button(self.frm, text="Player2", fg="red", command=lambda info=self.player2.id:self.placeStone(info))

        self.turn = 0

        self.initView()

    def initView(self):
        self.root.geometry("800x750")
        
        self.frm.pack()
        self.frm.place(anchor='center', relx=0.5, rely=0.5)
        
        self.player2Button.pack(side='top')

        self.canvas.pack()
        self.canvas.bind("<Button-1>",self.onBoardClick)

        self.player1Button.pack(side='bottom')

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
        self.selectPos = self.gameBoard.coord2BoardPos([event.x,event.y])
        coord = self.gameBoard.boardPos2Coord(self.selectPos[0],self.selectPos[1])
        self.selectBox[self.turn] = self.canvas.create_image(coord,image=self.selectBoxImg[self.turn])

    def placeStone(self,playerId):
            if((playerId-1) == self.turn):
                x = int(self.selectPos[0])
                y = int(self.selectPos[1])
                if (self.gameBoard.board[y][x] == 0):
                    self.gameBoard.board[y][x] = playerId
                    self.gameBoard.displayStone(self.canvas,playerId,self.gameBoard.boardPos2Coord(x,y))
                    self.canvas.delete(self.selectBox[self.turn])
                    self.turn = (self.turn + 1) % 2
            return



game = Game(15)
game.root.mainloop()