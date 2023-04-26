import numpy as np
from tkinter import PhotoImage
from enum import IntEnum
import time
from scipy import ndimage

from sympy.utilities.iterables import multiset_permutations
import numpy.lib.stride_tricks as npst

class Board:
    """
    A class to represent the gameboard

    Attributes
    ----------




    Methods
    -------

    
    

    
    """

    class Direction(IntEnum):
        VERTICAL = 0    # 1. top-to-bottom
        HORIZONTAL = 1  # 2. left-to-right
        DOWNHILL = 2    # 3. top-left-to-bottom-right
        UPHILL = 3      # 4. bottom-left-to-top-right

    __EMPTY = -1
    __BORDER = -2
    __CURPOS = -3
    __pxSize = 571
    __boardImgPath = "img/board.png"
    __whiteImgPath = "img/white.png"
    __blackImgPath = "img/black.png"
    __boardImgStartCoord = np.asarray([21,23])

    __PRINTMSG = False
    __PRINTTIME = False

    __DILATE_RANGE = 2

    _fourTargetList = []
    _threeOpentargetList = []
    _threeSpOppBltargetList = []
    _threeBlTargetList = []
    _threeSpPlyBltargetList = []
    _twoOpentargetList = []
    _twoBlTargetList = []
    _oneOpentargetList = []
    _oneBlTargetList = []

    def __init__(self, size, winRequirement):
        if (size<3):
            raise ValueError(f"Board size must be at least 3. Input size = {size}")
        self._size = size
        self._pxStep = Board.__pxSize / (self.size - 1)
        
        self._actualSize = size + 2 # border on 2 sides
        self._board = None
        self.resetBoard()

        self.boardImg = PhotoImage(file=Board.__boardImgPath)
        self.stoneImgList = []

        if (winRequirement < 3):
            raise ValueError(f"Win requirement must be at least 3. Input win requirement = {winRequirement}")
        if (size < winRequirement):
            raise ValueError(f"Win requirement must be smaller than gameboard size. Input size = {size}, winRequirement = {winRequirement}")
        self._winTarget = winRequirement

        if(winRequirement==5):
            Board._prepAllTargetList()
        return
    
    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self,size):
        if (size<3):
            raise ValueError(f"Board size must be at least 3. Input size = {size}")
        self._size = size
        self._actualSize = size + 2
        self.resetBoard()
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
    
    def at(self,x,y):
        if(x < 0 or y < 0 or x >= self.size or y >= self.size):
            raise ValueError(f"Coordinate out of bound (from 0 to {self.size-1}) = {x,y}")
        return self._board[y+1][x+1]
    
    def set(self,x,y,val):
        if(x < 0 or y < 0 or x >= self.size or y >= self.size):
            raise ValueError(f"Coordinate out of bound (from 0 to {self.size-1}) = {x,y}")
        self._board[y+1][x+1] = val
        return
    
    def resetBoard(self):
        self._board = np.ones([self._actualSize,self._actualSize],dtype=np.int8)*Board.__EMPTY
        self._board[0,:] = Board.__BORDER
        self._board[:,0] = Board.__BORDER
        self._board[self._actualSize-1,:] = Board.__BORDER
        self._board[:,self._actualSize-1] = Board.__BORDER
        return
    
        
    def clearBoard(self,canvas):
        self.resetBoard()
        self._clearBoardDisplay(canvas)
        return

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
        canvas.create_image(310,310,image=self.boardImg)

        for y in range(self.size):
            for x in range(self.size):
                if self.at(x,y)==Board.__EMPTY:
                     continue
                self.displayStone(canvas,self.at(x,y),self.boardPos2Coord(x,y))
        return
    
    def _clearBoardDisplay(self,canvas):
        canvas.delete()
        self.stoneImgList.clear()
        self.displayBoard(canvas)
        return

# utilities
    def _getDirArrayAndPos(self,dir,curPos,addCheck):
        size = self._actualSize
        extendLen = self.winTarget+addCheck
        arr = None
        pos = -1
        actualPos = [int(curPos[0]+1),int(curPos[1]+1)]
        # extract whole column/row/diagonal
        if (dir == Board.Direction.VERTICAL):
            arr = self._board[:,actualPos[0]] 
            pos = actualPos[1]
        elif (dir == Board.Direction.HORIZONTAL):
            arr = self._board[actualPos[1],:] 
            pos = actualPos[0]
        elif (dir == Board.Direction.DOWNHILL):
            diff = actualPos[1]-actualPos[0]
            startX = max(0,-diff)
            startY = max(0,diff)
            arrSize = size - abs(diff)
            arr = np.empty(arrSize,dtype=np.int8)
            for i in range(arrSize):
                arr[i] = self._board[startY+i][startX+i]
            pos = actualPos[0] - startX
        elif (dir == Board.Direction.UPHILL):
            yDiff = size - 1 - actualPos[1]
            startX = max(0,actualPos[0] - yDiff)
            startY = min(size-1,actualPos[0]+actualPos[1])
            arrSize = abs(startX-startY)+1
            arr = np.empty(arrSize,dtype=np.int8)
            for i in range(arrSize):
                arr[i] = self._board[startY-i][startX+i]
            pos = actualPos[0] - startX
        
        # extract required number of data
        start = max(0,pos-extendLen+1)
        end = min(size,pos+extendLen)
        arr = arr[start:end]
        pos = pos - start

        return [arr,pos]
    
    @classmethod
    def _isNConnected(self,arr,pos,playerId,n,excludeCur=False,leftOfPos=None):
        if (arr.size < n):
            return [False,None]
        
        connected = 0
        extraCheck = 1 if excludeCur else 0
        checkStart = max(0,pos - n + 1 - extraCheck)
        if(leftOfPos==True): # known n connected found on left, start checking on right instead
            checkStart = pos+1
        checkEnd = min(arr.size,pos + n + extraCheck)

        for i in range(checkStart,checkEnd):
            if(arr[i]==playerId):
                connected = connected + 1
            else:
                connected = 0
            if(connected==n):
                if(not leftOfPos==None):
                    if(i<pos):
                        leftOfPos = True
                    else:
                        leftOfPos = False
                return [True,leftOfPos]

        return [False,leftOfPos]
    
    def _checkAnyMatch(self,arr,targetList):
        targetSize = targetList[0].size
        if(arr.size < targetSize):
            return False
        arr = arr.astype(np.int8)
        numSlices = arr.size - targetSize + 1

        # slower speed compare (about 1.1s)
        # for i in range(numSlices):
        #     a = arr[i:(i+targetSize)]
        #     b = np.where((targetList == a).all(axis=1))
        #     if(b[0].size > 0):
        #         return True
        # return False
            
        # faster speed compare (about 0.8s)
        # get matrix of all sliced a = arr[i:(i+targetSize)]
        slicedArr = npst.as_strided(arr,shape=(numSlices,targetSize),strides=(1,1))
        # compare all arrays by broadcasting
        return (np.sum((targetList==slicedArr[:,None]).all(axis=2)) > 0)
    
    @classmethod
    def _findTargetList(self,mainList,singleEndList=None,doubleEndList=None):
        targetListBase = list(multiset_permutations(mainList))
        start2 = time.perf_counter()
        targetList = []
        for i in range(len(targetListBase)):
            if(not singleEndList == None):
                for j in range(len(singleEndList)):
                    tempArr = np.insert(np.array(targetListBase[i],dtype=np.int8),0,singleEndList[j])
                    targetList.append(tempArr)
                    tempArr = np.append(np.array(targetListBase[i],dtype=np.int8),singleEndList[j])
                    targetList.append(tempArr)
            if(not doubleEndList == None):
                for j in range(len(doubleEndList)):
                    tempArr = np.insert(np.array(targetListBase[i],dtype=np.int8),0,doubleEndList[j])
                    tempArr = np.append(tempArr,doubleEndList[j])
                    targetList.append(tempArr)
            if(singleEndList == None and doubleEndList == None):
                tempArr = np.array(targetListBase[i],dtype=np.int8)
                targetList.append(tempArr)
        targetList = np.asarray(targetList,dtype=np.int8)
        print("         Target List time: ", (time.perf_counter()-start2)*1000)

        return targetList
    
    @classmethod
    def _duplicateArrInOppDir(self,arrList):
        initiallen = len(arrList)
        for i in range(initiallen):
            arrList.append(np.flip(arrList[i]))

        arr2D = np.asarray(arrList,np.int8)
        return arr2D
    
    def _getCheckArr(self,arr,pos):
        checkArr = np.array(arr) # make a copy, instead of asarray
        checkArr[pos] = Board.__CURPOS
        return checkArr
    
    @classmethod
    def _prepAllTargetList(self):
        # Four
        four0TargetList = Board._findTargetList([0,0,0,0,Board.__CURPOS])
        four1TargetList = Board._findTargetList([1,1,1,1,Board.__CURPOS])
        Board._fourTargetList = [four0TargetList,four1TargetList]

        # Open three
        threeOpen0targetList = Board._findTargetList([0,0,0,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        threeOpen1targetList = Board._findTargetList([1,1,1,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        Board._threeOpentargetList = [threeOpen0targetList,threeOpen1targetList]
        
        # Special block three opp
        #   1. x_ooo_p or B_ooo_p
        threeSpOppBl0targetList = [np.asarray([0,Board.__EMPTY,1,1,1,Board.__EMPTY,Board.__CURPOS],dtype=np.int8),    
                                   np.asarray([Board.__BORDER,Board.__EMPTY,1,1,1,Board.__EMPTY,Board.__CURPOS],dtype=np.int8)]
        threeSpOppBl0targetList = Board._duplicateArrInOppDir(threeSpOppBl0targetList)
        threeSpOppBl1targetList = [np.asarray([1,Board.__EMPTY,0,0,0,Board.__EMPTY,Board.__CURPOS],dtype=np.int8),
                                   np.asarray([Board.__BORDER,Board.__EMPTY,0,0,0,Board.__EMPTY,Board.__CURPOS],dtype=np.int8)]
        threeSpOppBl1targetList = Board._duplicateArrInOppDir(threeSpOppBl1targetList)
        #   2. _oo_op or _o_oop
        threeSpOppBl0targetList2 = [np.asarray([Board.__EMPTY,1,1,Board.__EMPTY,1,Board.__CURPOS],dtype=np.int8),
                                    np.asarray([Board.__EMPTY,1,Board.__EMPTY,1,1,Board.__CURPOS],dtype=np.int8)]
        threeSpOppBl0targetList2 = Board._duplicateArrInOppDir(threeSpOppBl0targetList2)
        threeSpOppBl1targetList2 = [np.asarray([Board.__EMPTY,0,0,Board.__EMPTY,0,Board.__CURPOS],dtype=np.int8),
                                    np.asarray([Board.__EMPTY,0,Board.__EMPTY,0,0,Board.__CURPOS],dtype=np.int8)]
        threeSpOppBl1targetList2 = Board._duplicateArrInOppDir(threeSpOppBl1targetList2)
        Board._threeSpOppBltargetList = [threeSpOppBl0targetList,threeSpOppBl1targetList]
        Board._threeSpOppBltargetList2 = [threeSpOppBl0targetList2,threeSpOppBl1targetList2]

        # Block three
        threeBl0TargetList = Board._findTargetList([0,0,0,Board.__CURPOS,Board.__EMPTY],singleEndList=[1,Board.__BORDER])
        threeBl1TargetList = Board._findTargetList([1,1,1,Board.__CURPOS,Board.__EMPTY],singleEndList=[0,Board.__BORDER])
        Board._threeBlTargetList = [threeBl0TargetList,threeBl1TargetList]

        # Special block three player
        #   1. _xxx_p
        threeSpPlyBl0targetList = [np.asarray([Board.__EMPTY,0,0,0,Board.__EMPTY,Board.__CURPOS],dtype=np.int8)]
        threeSpPlyBl0targetList = Board._duplicateArrInOppDir(threeSpPlyBl0targetList)
        threeSpPlyBl1targetList = [np.asarray([Board.__EMPTY,1,1,1,Board.__EMPTY,Board.__CURPOS],dtype=np.int8)]
        threeSpPlyBl1targetList = Board._duplicateArrInOppDir(threeSpPlyBl1targetList)
        #   2. xx_xp or x_xxp
        threeSpPlyBl0targetList2 = [np.asarray([0,0,Board.__EMPTY,0,Board.__CURPOS],dtype=np.int8),
                                    np.asarray([0,Board.__EMPTY,0,0,Board.__CURPOS],dtype=np.int8)]
        threeSpPlyBl0targetList2 = Board._duplicateArrInOppDir(threeSpPlyBl0targetList2)
        threeSpPlyBl1targetList2 = [np.asarray([1,1,Board.__EMPTY,1,Board.__CURPOS],dtype=np.int8),
                                    np.asarray([1,Board.__EMPTY,1,1,Board.__CURPOS],dtype=np.int8)]
        threeSpPlyBl1targetList2 = Board._duplicateArrInOppDir(threeSpPlyBl1targetList2)
        Board._threeSpPlyBltargetList = [threeSpPlyBl0targetList,threeSpPlyBl1targetList]
        Board._threeSpPlyBltargetList2 = [threeSpPlyBl0targetList2,threeSpPlyBl1targetList2]

        # Open two 
        #   1. _xxp_
        twoOpen0targetList = Board._findTargetList([0,0,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        twoOpen1targetList = Board._findTargetList([1,1,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        #   2. _xx_p_ or _xp_x_ or _px_x_
        twoOpen0targetList2 = [np.asarray([Board.__EMPTY,0,0,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY],dtype=np.int8),
                               np.asarray([Board.__EMPTY,0,Board.__CURPOS,Board.__EMPTY,0,Board.__EMPTY],dtype=np.int8),
                               np.asarray([Board.__EMPTY,Board.__CURPOS,0,Board.__EMPTY,0,Board.__EMPTY],dtype=np.int8)]
        twoOpen0targetList2 = Board._duplicateArrInOppDir(twoOpen0targetList2)
        twoOpen1targetList2 = [np.asarray([Board.__EMPTY,1,1,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY],dtype=np.int8),
                               np.asarray([Board.__EMPTY,1,Board.__CURPOS,Board.__EMPTY,1,Board.__EMPTY],dtype=np.int8),
                               np.asarray([Board.__EMPTY,Board.__CURPOS,1,Board.__EMPTY,1,Board.__EMPTY],dtype=np.int8)]
        twoOpen1targetList2 = Board._duplicateArrInOppDir(twoOpen1targetList2)
        Board._twoOpentargetList = [twoOpen0targetList,twoOpen1targetList]
        Board._twoOpentargetList2 = [twoOpen0targetList2,twoOpen1targetList2]

        # Block two
        twoBl0TargetList = Board._findTargetList([0,0,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY],singleEndList=[1,Board.__BORDER])
        twoBl1TargetList = Board._findTargetList([1,1,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY],singleEndList=[0,Board.__BORDER])
        Board._twoBlTargetList = [twoBl0TargetList,twoBl1TargetList]

        # Open one
        #   1. _(xp_)_ and  2. _x_p_
        oneOpen0targetList = Board._findTargetList([0,Board.__CURPOS,Board.__EMPTY],doubleEndList=[Board.__EMPTY])
        oneOpen0targetListTemp = [np.asarray([Board.__EMPTY,0,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY],dtype=np.int8)]
        Board._duplicateArrInOppDir(oneOpen0targetListTemp)
        oneOpen0targetList = np.vstack((oneOpen0targetList, oneOpen0targetListTemp))
        oneOpen1targetList = Board._findTargetList([1,Board.__CURPOS,Board.__EMPTY],doubleEndList=[Board.__EMPTY])
        oneOpen1targetListTemp = [np.asarray([Board.__EMPTY,1,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY],dtype=np.int8)]
        Board._duplicateArrInOppDir(oneOpen1targetListTemp)
        oneOpen1targetList = np.vstack((oneOpen1targetList, oneOpen1targetListTemp))
        #   3. _x_ _p_
        oneOpen0targetList2 = [np.asarray([Board.__EMPTY,0,Board.__EMPTY,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY],dtype=np.int8)]
        oneOpen0targetList2 = Board._duplicateArrInOppDir(oneOpen0targetList2)
        oneOpen1targetList2 = [np.asarray([Board.__EMPTY,1,Board.__EMPTY,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY],dtype=np.int8)]
        oneOpen1targetList2 = Board._duplicateArrInOppDir(oneOpen1targetList2)
        Board._oneOpentargetList = [oneOpen0targetList,oneOpen1targetList]
        Board._oneOpentargetList2 = [oneOpen0targetList2,oneOpen1targetList2]

        # Block one
        oneBl0TargetList = Board._findTargetList([0,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY,Board.__EMPTY],singleEndList=[1,Board.__BORDER])
        oneBl1TargetList = Board._findTargetList([1,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY,Board.__EMPTY],singleEndList=[0,Board.__BORDER])
        Board._oneBlTargetList = [oneBl0TargetList,oneBl1TargetList]

        return
    
    def _connectCheck(self,arr,pos,playerId,checkName,checkArrList):
        if(Board.__PRINTTIME):
            start = time.perf_counter()

        checkArr = self._getCheckArr(arr,pos)

        match = False
        for i in range(len(checkArrList)):
            match = match or self._checkAnyMatch(checkArr,checkArrList[i][playerId])

        if(Board.__PRINTTIME):
            timeMs = (time.perf_counter()-start)*1000
            timeStr = checkName + " time(ms):"
            print(f"{timeStr:<40}{timeMs:<20}")
            
        if(Board.__PRINTMSG and match):
            print(checkName, "match")
        return match
    
# main game logics 
    def isPlayerWon(self,playerId,lastPlayCoord):
        # Check 4 directions, each direction check +/- self.winTarget-1, total 2*self.winTarget-2 cells        
        for dir in Board.Direction:
            arr,pos = self._getDirArrayAndPos(dir,lastPlayCoord,0)
            found,_ = Board._isNConnected(arr,pos,playerId,self.winTarget)
            if(found):  
                return True
      
        return False   
    
    def isPosEmpty(self,x,y):
        return (self.at(x,y)==Board.__EMPTY)
    
    def ruleRenjuBoard(self):
        # prohibit black 3-and-3, 4-and-4, overline

        return
    
    def ruleSwap2Board(self):

        return

# computer player (for connecting 5 stones for now)
    def getNextMove(self, playerId, opponentId, isRecordTime):
        f = open("check.txt","w")

        # computer player next move
        scoreBoard = np.zeros([self.size,self.size])
        selectedPos = None
        start = time.perf_counter()

        # check whole board
        score = 0
        bestScore = -1 # for debug
        bestConnect = None # for debug
        for y in range(self.size):
            for x in range(self.size):
                connectResult = np.zeros((4,14))
                weight = np.asarray([5000,4000,3500,1000,1000,1000,600,600,100,100,10,10,5,4])
                if(self.at(x,y)==Board.__EMPTY):
                    for dir in Board.Direction:
                        if(Board.__PRINTTIME):
                            print("\n\n")
                        if(Board.__PRINTTIME):
                            start2 = time.perf_counter()

                        arr,pos = self._getDirArrayAndPos(dir,[x,y],2)
                        #print(arr.size,pos)

                        # next play win, highest score
                        if(self._connectCheck(arr,pos,playerId,"Four Player",[Board._fourTargetList])):
                            if(Board.__PRINTMSG):
                                print("Four Player",x,y)
                            score = score + 1000000
                        # need to block opponent win
                        elif(self._connectCheck(arr,pos,opponentId,"Four Opponent",[Board._fourTargetList])):
                            if(Board.__PRINTMSG):
                                print("Four Opp",x,y)
                            score = score + 100000
                        else:
                            connectResult[int(dir),:] = [
                                # almost win with open three
                                self._connectCheck(arr,pos,playerId,    "Open Three Player",            [Board._threeOpentargetList]),
                                # block opponent open three
                                self._connectCheck(arr,pos,opponentId,  "Open Three Opponent",          [Board._threeOpentargetList]),          
                                self._connectCheck(arr,pos,opponentId,  "Special Block Three Opponent", [Board._threeSpOppBltargetList,
                                                                                                         Board._threeSpOppBltargetList2]),
                                # force opponent to block
                                self._connectCheck(arr,pos,playerId,    "Block Three Player",           [Board._threeBlTargetList]),
                                self._connectCheck(arr,pos,playerId,    "Special Block Three Player",   [Board._threeSpPlyBltargetList,
                                                                                                         Board._threeSpPlyBltargetList2]),
                                self._connectCheck(arr,pos,playerId,    "Open Two Player",              [Board._twoOpentargetList,
                                                                                                         Board._twoOpentargetList2]),
                                # prevent threat
                                self._connectCheck(arr,pos,opponentId,  "Block Three Opponent",         [Board._threeBlTargetList]),
                                self._connectCheck(arr,pos,opponentId,  "Open Two Opponent",            [Board._twoOpentargetList,                        
                                                                                                         Board._twoOpentargetList2]),
                                # create a bit threat 
                                self._connectCheck(arr,pos,playerId,    "Block Two Player",             [Board._twoBlTargetList]),
                                self._connectCheck(arr,pos,playerId,    "Open One Player",              [Board._oneOpentargetList,
                                                                                                         Board._oneOpentargetList2]),
                                # prevent threat (conservative)
                                self._connectCheck(arr,pos,opponentId,  "Block Two Opponent",           [Board._twoBlTargetList]),   
                                self._connectCheck(arr,pos,opponentId,  "Open One Opponent",            [Board._oneOpentargetList,
                                                                                                         Board._oneOpentargetList2]),
                                # better than random
                                self._connectCheck(arr,pos,playerId,    "Block One Player",             [Board._oneBlTargetList]),
                                self._connectCheck(arr,pos,opponentId,  "Block One Opponent",           [Board._oneBlTargetList]),   
                            ]
                            #weight = np.asarray([5000,  4000,3500,  1000,1000,1000,  600,600,  100,100,  10,10,  5,4])

                            if(Board.__PRINTMSG): 
                                if(np.sum(connectResult[int(dir),:]) > 0): 
                                    print(x,y,"\n")
                        
                        if(Board.__PRINTTIME):
                            print("Each step time (ms): ", (time.perf_counter()-start2)*1000)

                addScore = np.sum(connectResult.dot(weight))

                if((score+addScore)>bestScore):
                    bestScore = score+addScore
                    bestConnect = connectResult.copy()
                scoreBoard[y][x] = score + addScore
                score = 0 

        # better to place closer to existing stones
        beforeDilate = self.board[1:-1,1:-1] > -1
        mask = ndimage.generate_binary_structure(2, 2)
        for i in range(Board.__DILATE_RANGE):
            afterDilate = ndimage.binary_dilation(beforeDilate,structure=mask).astype(int)
            scoreBoard = scoreBoard + (afterDilate-beforeDilate)*(Board.__DILATE_RANGE-i)
            beforeDilate = afterDilate        

        overallTime = time.perf_counter()-start
        print("Overall time: ", overallTime)
                
        selectedPos = np.unravel_index(scoreBoard.argmax(),scoreBoard.shape)
        selectedPos = np.flip(selectedPos)
        print("Done",selectedPos[0],selectedPos[1],scoreBoard[selectedPos[1]][selectedPos[0]])
        print(scoreBoard)
        
        # write in file for score checking (debug)
        np.set_printoptions(suppress=True,threshold=np.inf,linewidth=np.inf)
        a = scoreBoard.copy() - (self.board[1:-1,1:-1] > -1)
        a = np.insert(np.insert(a,0,np.arange(15)+1,0),0,np.arange(16),1)
        f.write("[4p,4o,3sbo,3bp,3sbp,2op,2oo,3bo,2bp,1op,1oo,2bo,1bp,1bo], [Vert,Hori,Down,Up]\n")
        f.write(np.array2string(bestConnect))
        f.write("\n")
        f.write(np.array2string(a))
        f.close()
        if(isRecordTime):
            fTime = open("time.txt","a")
            fTime.write(f"{overallTime:.6f} ")
            print(f"{overallTime:.6f} ")
            f.close()
        return selectedPos
    