from tkinter import *
import tkinter.font as font
from tkinter import ttk
from Board import Board
from Player import Player
from threading import *
import numpy as np

class Game:
     """
     A class to represent the gomoku game

     Attributes
     ----------




     Methods
     -------

     
     
     
     
     
     
     """
    
     __TIE = -1
     __NO_COMPUTER = -1
     __numPlayers = 2
     __selectBoxImgPath = ["img/box1.png","img/box2.png"]
     __startGameMsg = "Start the Game!"
     __tieGameMsg = "Game is Tie."

     def __winGameMsg(playerId):
          return f"Player{playerId+1} Win!"
     
     def __offerDrawMsg(playerId):
          return f"Player{playerId+1} offer a Draw.\nPlayer{Game._getAnotherPlayerId(playerId)+1} accept?"
     
     def __resignMsg(playerId):
          return f"Player{playerId+1} resign.\nPlayer{Game._getAnotherPlayerId(playerId)+1} Win!"

     def __init__(self, boardSize, winRequirement, timeLimit, addTime):
          self.winRequirement = winRequirement
          self.isGameQuit = False
          self.winPlayer = Game.__TIE

          self.root = Tk()
          self.frm = ttk.Frame(self.root, width=700, height=650, padding=10)
          self.canvas = Canvas(self.frm,width=620,height=620)

          self.selectBoxImg = [PhotoImage(file=Game.__selectBoxImgPath[0]),PhotoImage(file=Game.__selectBoxImgPath[1])]
          self.selectBox = [None,None]
          
          self.gameBoard = Board(boardSize,self.winRequirement)

          self.players = []
          self.playersButton = []
          self.drawButton = []
          self.resignButton = []
          for i in range(Game.__numPlayers):
               self.playersButton.append(
                    Button(self.frm, text="Player"+str(i+1), 
                         fg="green" if(i==0) else "red", 
                         command=lambda id=i:self.placeStone(id)))
               self.players.append(Player(i,timeLimit,addTime,self.playersButton[i]))
               self.players[i].getTimer().initTimerBar(self.frm,600)

               self.drawButton.append(
                    Button(self.frm, text="Offer a draw", width=10,
                           fg="green" if(i==0) else "red", 
                           command=lambda id=i:self.offerDraw(id)))
               self.resignButton.append(
                    Button(self.frm, text="Resign", width=10,
                           fg="green" if(i==0) else "red", 
                           command=lambda id=i:self.resignGame(id)))
               
          self.computerPlayerId = Game.__NO_COMPUTER
          self.isVsComputer = BooleanVar()
          self.isVsComputer.set(False)

          self.startFrm = Frame(self.frm,bg="grey",padx=10,pady=10)
          
          self.gameFinishMsg = StringVar()
          self.gameFinishMsg.set(Game.__startGameMsg)
          self.gameFinishLabel = Label(self.startFrm, textvariable=self.gameFinishMsg, width=20, anchor="n",pady=50)
          self.gameFinishLabel['font'] = font.Font(family='Helvetica',size=30,weight="bold")
          self.gameFinishLabel.config(bg="grey")

          self.checkVsComputer = Checkbutton(self.startFrm,text="Vs Computer?",variable=self.isVsComputer, onvalue=True, offvalue=False, bg="grey",command=self.enableDisableComputerPlayer)
          self.checkVsComputer['font'] = font.Font(family='Helvetica',size=15)
          
          self.computerPlayerFrm = Frame(self.startFrm,bg="grey",highlightbackground="grey25",highlightthickness=2)
          self.computerPlayerMsg = Label(self.computerPlayerFrm,text="Computer\nplayer as: ",pady=10)
          self.computerPlayerMsg['font'] = font.Font(family='Helvetica',size=15)
          self.computerPlayerMsg.config(bg="grey")
          self.computerPlayerButton = [Button(self.computerPlayerFrm,text="Player1",relief=RAISED,command=lambda id=0:self.changeComputerPlayerSelection(id)),
                                       Button(self.computerPlayerFrm,text="Player2",relief=SUNKEN,command=lambda id=1:self.changeComputerPlayerSelection(id))]
          for child in self.computerPlayerFrm.winfo_children():
               child.configure(state=DISABLED)

          self.gameStartButton = Button(self.startFrm, text="Game Start!", width=12, command=self.startGame)
          self.gameStartButton['font'] = font.Font(family='Helvetica',size=20,weight="bold")

          self.gameQuitButton = Button(self.startFrm, text="Quit", width=10, command=self.quit)
          self.gameQuitButton['font'] = font.Font(family='Helvetica',size=10,weight="bold")

          self.msgFrm = Frame(self.frm,bg="grey75",padx=10,pady=10)
          self.gameMsg = StringVar()
          self.gameMsgLabel = Label(self.msgFrm, textvariable=self.gameMsg, width=15, anchor="n",pady=10,bg="grey75")
          self.gameMsgLabel['font'] = font.Font(family='Helvetica',size=20)
          self.gameMsgOkButton = Button(self.msgFrm,text="Ok",width=5,padx=2,pady=2,command=self.returnToStart)
          self.gameMsgAcceptButton = Button(self.msgFrm,text="Accept",width=5,padx=2,pady=2,command=self.acceptDraw)
          self.gameMsgRejectButton = Button(self.msgFrm,text="Reject",width=5,padx=2,pady=2,command=self.rejectDraw)



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

# view
     def initView(self):
          self.root.geometry("800x750")
          
          self.frm.pack()
          self.frm.place(anchor='center', relx=0.5, rely=0.5)
          
          self.players[1].getTimerBar().grid(column=1,row=0,padx=0,pady=0)
          self.playersButton[1].grid(column=1,row=1,padx=0,pady=0)
          self.drawButton[1].grid(column=0,row=1)
          self.resignButton[1].grid(column=0,row=0)

          self.canvas.grid(column=1,row=2,padx=0,pady=0)
          self.canvas.bind("<Button-1>",self.onBoardClick)

          self.playersButton[0].grid(column=1,row=3,padx=0,pady=0)
          self.players[0].getTimerBar().grid(column=1,row=4,padx=0,pady=0)
          
          self.drawButton[0].grid(column=2,row=3)
          self.resignButton[0].grid(column=2,row=4)

          self.startFrm.grid(row=2,column=1)
          Label(self.startFrm,text=' ',width=10,bg="grey").grid(row=1,column=0) # for centering grid layout
          self.startFrm.lift()
          
          self.gameFinishLabel.grid(row=0,column=0,columnspan=3)
          self.checkVsComputer.grid(row=1,columnspan=3)
          self.computerPlayerFrm.grid(row=2,columnspan=3,pady=10)
          self.gameStartButton.grid(row=3,column=1)
          self.gameQuitButton.grid(row=3,column=2)

          self.computerPlayerMsg.grid(row=0,column=0)
          self.computerPlayerButton[0].grid(row=0,column=1)
          self.computerPlayerButton[1].grid(row=0,column=2)

          self.msgFrm.grid(row=2,column=1)
          self.msgFrm.lift()
          self.gameMsgLabel.grid(row=0,columnspan=3)
          self.gameMsgOkButton.grid(row=1,column=1)
          self.gameMsgAcceptButton.grid(row=1,column=0)
          self.gameMsgRejectButton.grid(row=1,column=2)

          self.gameBoard.displayBoard(self.canvas)
          return

# UI button functions
     def enableDisableComputerPlayer(self):
          if(self.isVsComputer.get() == True):
               # Enable frame
               for child in self.computerPlayerFrm.winfo_children():
                    child.config(state=NORMAL)
               for i in range(Game.__numPlayers):
                    if(self.computerPlayerButton[i].cget('relief')==SUNKEN):
                         self.computerPlayerButton[i].config(state=DISABLED)
               self.computerPlayerFrm.config(highlightbackground="black")
          else:
               # Disable frame
               for child in self.computerPlayerFrm.winfo_children():
                    child.config(state=DISABLED)
               self.computerPlayerFrm.config(highlightbackground="grey25")

          return
     
     def changeComputerPlayerSelection(self,id):
          thisId = id
          nextId = Game._getAnotherPlayerId(thisId)
          
          self.computerPlayerButton[nextId].config(relief=RAISED,state=NORMAL)
          self.computerPlayerButton[thisId].config(relief=SUNKEN,state=DISABLED)
          return
     
     def getComputerPlayerId(self):
          if(self.isVsComputer.get() == False):
               return Game.__NO_COMPUTER
          for i in range(Game.__numPlayers):
               if(self.computerPlayerButton[i].cget('relief')==SUNKEN):
                    return i
          return Game.__NO_COMPUTER

     def onBoardClick(self,event):
          if (self.selectBox[self.turn] != None):
               self.canvas.delete(self.selectBox[self.turn])
          pos = self.gameBoard.coord2BoardPos([event.x,event.y])
          if (pos[0] >= self.gameBoard.size or pos[1] >= self.gameBoard.size):
               return
          self.players[self.turn].selectPos = pos
          coord = self.gameBoard.boardPos2Coord(pos[0],pos[1])
          self.selectBox[self.turn] = self.canvas.create_image(coord,image=self.selectBoxImg[self.turn])
          return

     def placeStone(self,playerId):
          if(playerId != self.turn or len(self.players[self.turn].selectPos)==0):
               return
          
          x = int(self.players[self.turn].selectPos[0])
          y = int(self.players[self.turn].selectPos[1])
          if (self.gameBoard.isPosEmpty(x,y)):
               self.gameBoard.set(x,y,playerId)
               self.players[self.turn].getTimer().setSkipTimeFlag()
               self.gameBoard.displayStone(self.canvas,playerId,self.gameBoard.boardPos2Coord(x,y))
               self.canvas.delete(self.selectBox[self.turn])

               if(self.gameBoard.isPlayerWon(playerId,self.players[self.turn].selectPos)):
                    self.winPlayer = playerId
                    self.gameFinish()
                    return

               self.switchPlayers()

          return
     
     def offerDraw(self,id):
          self.gameMsgOkButton.grid_remove()
          self.gameMsgAcceptButton.grid()
          self.gameMsgRejectButton.grid()
          self.gameMsg.set(Game.__offerDrawMsg(id))
          self.msgFrm.grid()
          self.stopGame()
          return
     
     def acceptDraw(self):
          self.winPlayer = Game.__TIE
          self.returnToStart()
          return
     
     def rejectDraw(self):
          self.msgFrm.grid_remove()
          self.resumeGame()
          return
     
     def resignGame(self,id):
          self.gameMsgAcceptButton.grid_remove()
          self.gameMsgRejectButton.grid_remove()
          self.gameMsgOkButton.grid()
          self.gameMsg.set(Game.__resignMsg(id))
          self.msgFrm.grid()
          self.stopGame()
          self.winPlayer = Game._getAnotherPlayerId(id)
          return
     
     def returnToStart(self):
          self.msgFrm.grid_remove()
          self.gameFinish()
          return
     
# rules (to be implemented)
     def ruleRenju(self):

          return
     
     def ruleSwap2(self):

          return
     
# main game logics
     @classmethod
     def _getAnotherPlayerId(self,id):
          return (id+1)%2
     
     def switchPlayers(self):
          self.players[self.turn].getTimer().pauseTimer()
          self.players[self.turn].getTimer().addCountDownTime()
          self.turn = Game._getAnotherPlayerId(self.turn)
          self.players[self.turn].getTimer().resumeTimer()
          if(self.turn == self.computerPlayerId):
               self.players[self.turn].startComputerPlayer()
          return
     
     def timeOut(self,id):
          nextId = Game._getAnotherPlayerId(id)
          while(not self.isGameQuit):
               if(self.players[id].getTimer().waitAndResetTimeOutEvent()):
                    self.canvas.delete(self.selectBox[id])

                    self.players[id].getTimer().pauseTimer()
                    self.players[id].getTimer().addCountDownTime()

                    self.turn = nextId
                    if(self.players[nextId].getTimer().isNoTime()):
                         self.gameFinish()
                         continue

                    self.players[nextId].getTimer().resumeTimer()
                    if(nextId == self.computerPlayerId):
                         self.players[nextId].startComputerPlayer()
                    
          return
     
     def resetGame(self):
          self.msgFrm.grid_remove()
          self.turn = 0
          self.winPlayer = Game.__TIE
          self.gameBoard.clearBoard(self.canvas)
          self.startFrm.grid()
          for i in range(Game.__numPlayers):
               self.players[i].getTimer().resetTimer()
               self.playersButton[i]['state'] = DISABLED
               self.drawButton[i]['state'] = DISABLED
               self.resignButton[i]['state'] = DISABLED

          #self.gameBoard.set(11,3,1)
          #self.gameBoard.set(13,1,1)
          #self.gameBoard.set(12,2,1)
             
          # self.gameBoard.set(2,5,1)
          # self.gameBoard.set(2,6,1)
          # self.gameBoard.set(2,7,1)
          # self.gameBoard.set(2,8,1)
          
          #self.gameBoard.set(2,9,1)
          # self.gameBoard.set(14,14,1)
          self.gameBoard.displayBoard(self.canvas)
          return
    
     def startGame(self):
          self.computerPlayerId = self.getComputerPlayerId()
          for i in range(Game.__numPlayers):
               if(self.isVsComputer.get() == True and i==self.computerPlayerId):
                    self.players[i].setComputerPlayer(self.gameBoard)
               else:
                    self.players[i].setNormalPlayer()

          self.resumeGame()
          self.startFrm.grid_remove()
          if(self.turn == self.computerPlayerId):
               #self.players[self.turn].startComputerPlayer()
               # force computer player to place in center
               self.players[self.turn].selectPos = np.asarray([self.gameBoard.size/2,self.gameBoard.size/2])
               self.placeStone(self.computerPlayerId)
          
          return
     
     def stopGame(self):
          for i in range(Game.__numPlayers):
               self.players[i].getTimer().pauseTimer()
               self.playersButton[i]['state'] = DISABLED
               self.resignButton[i]['state'] = DISABLED
               self.drawButton[i]['state'] = DISABLED
          return
     
     def resumeGame(self):
          self.players[self.turn].getTimer().resumeTimer()
          for i in range(Game.__numPlayers):
               self.playersButton[i]['state'] = NORMAL
               self.resignButton[i]['state'] = NORMAL
               self.drawButton[i]['state'] = NORMAL
          return
     
     def gameFinish(self):
          self.stopGame()
          if(self.winPlayer == Game.__TIE):
               print("Game is tie.")
               self.gameFinishMsg.set(Game.__tieGameMsg)
          else:
               print("Player " + str(self.winPlayer+1) + " win!")
               self.gameFinishMsg.set(Game.__winGameMsg(self.winPlayer))

          self.resetGame()

          return
     
     def quit(self):
          self.isGameQuit = True
          self.players[self.computerPlayerId].stopComputerPlayer()
          for i in range(Game.__numPlayers):
               self.players[i].getTimer().stopTimer()
               self.players[i].getTimer().waitThreadFinish()
               self.timeOutThreads[i].join()

          self.root.destroy()

          return



game = Game(boardSize=15,winRequirement=5,timeLimit=150,addTime=20)
#print(repr(game))
#print(game)
game.root.mainloop()

