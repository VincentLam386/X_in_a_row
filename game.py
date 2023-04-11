from tkinter import *
import tkinter.font as font
from tkinter import ttk
from Board import Board
from Player import Player
from threading import *

from Timer import Timer
import time

class Game:
     """
     A class to represent the gomoku game

     Attributes
     ----------




     Methods
     -------

     
     
     
     
     
     
     """
    
     __numPlayers = 2
     __selectBoxImgPath = ["img/box1.png","img/box2.png"]
     __startGameMsg = "Start the Game!"
     __tieGameMsg = "Game is Tie."

     def __winGameMsg(playerId):
          return "Player{:d} Win!".format(playerId+1)

     def __init__(self, boardSize, winRequirement, timeLimit, addTime):
          self.winRequirement = winRequirement
          self.isGameQuit = False
          self.winPlayer = -1

          self.root = Tk()
          self.frm = ttk.Frame(self.root, width=700, height=650, padding=10)
          self.canvas = Canvas(self.frm,width=620,height=620)

          self.selectPos = None
          self.selectBoxImg = [PhotoImage(file=Game.__selectBoxImgPath[0]),PhotoImage(file=Game.__selectBoxImgPath[1])]
          self.selectBox = [None,None]
          
          self.gameBoard = Board(boardSize,self.winRequirement)

          self.players = []
          self.playersButton = []
          for i in range(Game.__numPlayers):
               self.players.append(Player(i,timeLimit,addTime))
               self.playersButton.append(
                    Button(self.frm, text="Player"+str(i+1), 
                         fg="green" if(i==0) else "red", 
                         command=lambda info=self.players[i].id:self.placeStone(info)))
               
               self.players[i].getTimer().initTimerBar(self.frm,600)

          self.msgFrm = Frame(self.frm,bg="grey",padx=10,pady=10)
          
          self.gameFinishMsg = StringVar()
          self.gameFinishMsg.set(Game.__startGameMsg)
          self.gameFinishLabel = Label(self.msgFrm, textvariable=self.gameFinishMsg, width=20, anchor="n",pady=50)
          self.gameFinishLabel['font'] = font.Font(family='Helvetica',size=30,weight="bold")
          self.gameFinishLabel.config(bg="grey")

          self.gameStartButton = Button(self.msgFrm, text="Game Start!", width=12, command=self.gameStart)
          self.gameStartButton['font'] = font.Font(family='Helvetica',size=20,weight="bold")

          self.gameQuitButton = Button(self.msgFrm, text="Quit", width=10, command=self.quit)
          self.gameQuitButton['font'] = font.Font(family='Helvetica',size=10,weight="bold")


          self.turn = 0

          self.initView()
          self.timeOutThreads = []
          for i in range(Game.__numPlayers):
               self.timeOutThreads.append(Thread(target=lambda id=self.players[i].id:self.timeOut(id)))
               self.timeOutThreads[i].start()

          self.resetGame()
          return
     
     def __str__(self):
          return f"""
Game:
     Gameboard: {self.gameBoard}
     Player1: {self.players[0]}
     Player2: {self.players[1]}
          """
     
     def __repr__(self):
          return f"Game(gameBoard={repr(self.gameBoard)}, players=[{repr(self.players[0])}, {repr(self.players[1])}])"

     def initView(self):
          self.root.geometry("800x750")
          
          self.frm.pack()
          self.frm.place(anchor='center', relx=0.5, rely=0.5)
          
          self.players[1].getTimerBar().grid(column=0,row=0,padx=0,pady=0)
          self.playersButton[1].grid(column=0,row=1,padx=0,pady=0)

          self.canvas.grid(column=0,row=2,padx=0,pady=0)
          self.canvas.bind("<Button-1>",self.onBoardClick)

          self.playersButton[0].grid(column=0,row=3,padx=0,pady=0)
          self.players[0].getTimerBar().grid(column=0,row=4,padx=0,pady=0)

          self.msgFrm.grid(row=2)
          Label(self.msgFrm,text=' ',width=10,bg="grey").grid(row=1,column=0) # for centering grid layout
          self.msgFrm.lift()
          
          self.gameFinishLabel.grid(row=0,column=0,columnspan=3)
          self.gameStartButton.grid(row=1,column=1)
          self.gameQuitButton.grid(row=1,column=2)


          #self.gameBoard.board[4][10] = 1
          #self.gameBoard.board[5][10] = 1
          # self.gameBoard.board[12][10] = 0
          # self.gameBoard.board[14][0] = 0
          # self.gameBoard.board[2][5] = 1
          # self.gameBoard.board[9][6] = 1
          # self.gameBoard.board[11][11] = 1
          # self.gameBoard.board[14][14] = 1

          self.gameBoard.displayBoard(self.canvas)
          return

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
          if (self.gameBoard.board[y][x] == -1):
               self.gameBoard.board[y][x] = playerId
               self.players[self.turn].getTimer().setSkipTimeFlag()
               self.gameBoard.displayStone(self.canvas,playerId,self.gameBoard.boardPos2Coord(x,y))
               self.canvas.delete(self.selectBox[self.turn])

               if(self.gameBoard.isPlayerWon(playerId,self.selectPos)):
                    self.winPlayer = playerId
                    self.gameFinish()
                    return

               self.switchPlayers()

          return
     
     def switchPlayers(self):
          self.players[self.turn].getTimer().pauseTimer()
          self.players[self.turn].getTimer().addCountDownTime()
          self.turn = (self.turn + 1) % 2
          self.players[self.turn].getTimer().resumeTimer()
          return
     
     def timeOut(self,id):
          nextId = (id + 1) % 2
          while(not self.isGameQuit):
               if(self.players[id].getTimer().waitAndResetTimeOutEvent()):
                    self.canvas.delete(self.selectBox[id])

                    self.players[id].getTimer().pauseTimer()
                    self.players[id].getTimer().addCountDownTime()

                    self.turn = nextId
                    self.players[nextId].getTimer().resumeTimer()

                    if(self.players[nextId].getTimer().isNoTime()):
                         self.gameFinish()
                         continue
          return
     
     def resetGame(self):
          self.turn = 0
          self.winPlayer = -1
          self.msgFrm.grid()
          for i in range(Game.__numPlayers):
               self.players[i].getTimer().resetTimer()
               self.playersButton[i]['state'] = DISABLED
          return

    
     def gameStart(self):
          self.players[self.turn].getTimer().resumeTimer()
          self.msgFrm.grid_remove()
          for i in range(Game.__numPlayers):
               self.playersButton[i]['state'] = NORMAL

          return
     
     def gameFinish(self):
          for i in range(Game.__numPlayers):
               self.players[i].getTimer().pauseTimer()
          if(self.winPlayer == -1):
               print("Game is tie.")
               self.gameFinishMsg.set(Game.__tieGameMsg)
          else:
               print("Player " + str(self.winPlayer) + " win!")
               self.gameFinishMsg.set(Game.__winGameMsg(self.winPlayer))

          self.resetGame()

          return
     
     def quit(self):
          self.isGameQuit = True
          for i in range(Game.__numPlayers):
               self.players[i].getTimer().stopTimer()
               self.players[i].getTimer().waitThreadFinish()
               self.timeOutThreads[i].join()

          self.root.destroy()

          return



game = Game(boardSize=15,winRequirement=5,timeLimit=3,addTime=0)
#print(repr(game))
#print(game)
game.root.mainloop()

