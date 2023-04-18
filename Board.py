import numpy as np
from tkinter import PhotoImage
from enum import Enum
import time

from sympy.utilities.iterables import multiset_permutations

class Board:
    """
    A class to represent the gameboard

    Attributes
    ----------




    Methods
    -------

    
    

    
    """

    class Direction(Enum):
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
        self._board = np.ones([self._actualSize,self._actualSize],dtype='i')*Board.__EMPTY
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
            arr = np.empty(arrSize)
            for i in range(arrSize):
                arr[i] = self._board[startY+i][startX+i]
            pos = actualPos[0] - startX
        elif (dir == Board.Direction.UPHILL):
            yDiff = size - 1 - actualPos[1]
            startX = max(0,actualPos[0] - yDiff)
            startY = min(size-1,actualPos[0]+actualPos[1])
            arrSize = abs(startX-startY)+1
            arr = np.empty(arrSize)
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
        loopSize = arr.size - targetSize + 1
        # for i in range(loopSize):
        #     for j in range(len(targetList)):
        #         a = arr[i:(i+targetSize)]
        #         b = targetList[j]
        #         if(np.array_equal(arr[i:(i+targetSize)], targetList[j])):
        #             return True
        for i in range(loopSize):
            a = arr[i:(i+targetSize)]
            b = np.where((targetList == a).all(axis=1))
            if(b[0].size > 0):
                return True

        return False
    
    @classmethod
    def _findTargetList(self,mainList,singleEndList=None,doubleEndList=None):
        targetListBase = list(multiset_permutations(mainList))
        start2 = time.perf_counter()
        targetList = []
        for i in range(len(targetListBase)):
            if(not singleEndList == None):
                for j in range(len(singleEndList)):
                    tempArr = np.insert(np.array(targetListBase[i],dtype='i'),0,singleEndList[j])
                    targetList.append(tempArr)
                    tempArr = np.append(np.array(targetListBase[i],dtype='i'),singleEndList[j])
                    targetList.append(tempArr)
            if(not doubleEndList == None):
                for j in range(len(doubleEndList)):
                    tempArr = np.insert(np.array(targetListBase[i],dtype='i'),0,doubleEndList[j])
                    tempArr = np.append(tempArr,doubleEndList[j])
                    targetList.append(tempArr)
            if(singleEndList == None and doubleEndList == None):
                tempArr = np.array(targetListBase[i],dtype='i')
                targetList.append(tempArr)
        targetList = np.asarray(targetList)
        print("         Target List time: ", (time.perf_counter()-start2)*1000)

        return targetList
    
    @classmethod
    def _duplicateArrInOppDir(self,arrList):
        initiallen = len(arrList)
        for i in range(initiallen):
            arrList.append(np.flip(arrList[i]))

        arr2D = np.asarray(arrList)
        return arr2D
    
    def _getCheckArr(self,arr,pos):
        checkArr = np.array(arr)
        checkArr[pos] = Board.__CURPOS
        return checkArr
    
    @classmethod
    def _prepAllTargetList(self):
        four0TargetList = Board._findTargetList([0,0,0,0,Board.__CURPOS])
        four1TargetList = Board._findTargetList([1,1,1,1,Board.__CURPOS])
        Board._fourTargetList = [four0TargetList,four1TargetList]

        threeOpen0targetList = Board._findTargetList([0,0,0,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        threeOpen1targetList = Board._findTargetList([1,1,1,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        Board._threeOpentargetList = [threeOpen0targetList,threeOpen1targetList]
        
        threeSpOppBl0targetList = [np.asarray([0,Board.__EMPTY,1,1,1,Board.__EMPTY,Board.__CURPOS]),
                                            np.asarray([Board.__BORDER,Board.__EMPTY,1,1,1,Board.__EMPTY,Board.__CURPOS])]
        threeSpOppBl0targetList = Board._duplicateArrInOppDir(threeSpOppBl0targetList)
        threeSpOppBl1targetList = [np.asarray([1,Board.__EMPTY,0,0,0,Board.__EMPTY,Board.__CURPOS]),
                                            np.asarray([Board.__BORDER,Board.__EMPTY,0,0,0,Board.__EMPTY,Board.__CURPOS])]
        threeSpOppBl1targetList = Board._duplicateArrInOppDir(threeSpOppBl1targetList)
        threeSpOppBl0targetList2 = [np.asarray([Board.__EMPTY,1,1,Board.__EMPTY,1,Board.__CURPOS]),
                                            np.asarray([Board.__EMPTY,1,Board.__EMPTY,1,1,Board.__CURPOS])]
        threeSpOppBl0targetList2 = Board._duplicateArrInOppDir(threeSpOppBl0targetList2)
        threeSpOppBl1targetList2 = [np.asarray([Board.__EMPTY,0,0,Board.__EMPTY,0,Board.__CURPOS]),
                                            np.asarray([Board.__EMPTY,0,Board.__EMPTY,0,0,Board.__CURPOS])]
        threeSpOppBl1targetList2 = Board._duplicateArrInOppDir(threeSpOppBl1targetList2)
        Board._threeSpOppBltargetList = [threeSpOppBl0targetList,threeSpOppBl1targetList]
        Board._threeSpOppBltargetList2 = [threeSpOppBl0targetList2,threeSpOppBl1targetList2]

        threeBl0TargetList = Board._findTargetList([0,0,0,Board.__CURPOS,Board.__EMPTY],singleEndList=[1,Board.__BORDER])
        threeBl1TargetList = Board._findTargetList([1,1,1,Board.__CURPOS,Board.__EMPTY],singleEndList=[0,Board.__BORDER])
        Board._threeBlTargetList = [threeBl0TargetList,threeBl1TargetList]

        threeSpPlyBl0targetList = [np.asarray([Board.__EMPTY,0,0,0,Board.__EMPTY,Board.__CURPOS])]
        threeSpPlyBl0targetList = Board._duplicateArrInOppDir(threeSpPlyBl0targetList)
        threeSpPlyBl1targetList = [np.asarray([Board.__EMPTY,1,1,1,Board.__EMPTY,Board.__CURPOS])]
        threeSpPlyBl1targetList = Board._duplicateArrInOppDir(threeSpPlyBl1targetList)
        threeSpPlyBl0targetList2 = [np.asarray([0,0,Board.__EMPTY,0,Board.__CURPOS]),
                                            np.asarray([0,Board.__EMPTY,0,0,Board.__CURPOS])]
        threeSpPlyBl0targetList2 = Board._duplicateArrInOppDir(threeSpPlyBl0targetList2)
        threeSpPlyBl1targetList2 = [np.asarray([1,1,Board.__EMPTY,1,Board.__CURPOS]),
                                            np.asarray([1,Board.__EMPTY,1,1,Board.__CURPOS])]
        threeSpPlyBl1targetList2 = Board._duplicateArrInOppDir(threeSpPlyBl1targetList2)
        Board._threeSpPlyBltargetList = [threeSpPlyBl0targetList,threeSpPlyBl1targetList]
        Board._threeSpPlyBltargetList2 = [threeSpPlyBl0targetList2,threeSpPlyBl1targetList2]

        twoOpen0targetList = Board._findTargetList([0,0,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        twoOpen1targetList = Board._findTargetList([1,1,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        twoOpen0targetList2 = [np.asarray([Board.__EMPTY,0,0,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY]),
                                  np.asarray([Board.__EMPTY,0,Board.__CURPOS,Board.__EMPTY,0,Board.__EMPTY]),
                                  np.asarray([Board.__EMPTY,Board.__CURPOS,0,Board.__EMPTY,0,Board.__EMPTY])]
        twoOpen0targetList2 = Board._duplicateArrInOppDir(twoOpen0targetList2)
        twoOpen1targetList2 = [np.asarray([Board.__EMPTY,1,1,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY]),
                                  np.asarray([Board.__EMPTY,1,Board.__CURPOS,Board.__EMPTY,1,Board.__EMPTY]),
                                  np.asarray([Board.__EMPTY,Board.__CURPOS,1,Board.__EMPTY,1,Board.__EMPTY])]
        twoOpen1targetList2 = Board._duplicateArrInOppDir(twoOpen1targetList2)
        Board._twoOpentargetList = [twoOpen0targetList,twoOpen1targetList]
        Board._twoOpentargetList2 = [twoOpen0targetList2,twoOpen1targetList2]

        twoBl0TargetList = Board._findTargetList([0,0,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY],singleEndList=[1,Board.__BORDER])
        twoBl1TargetList = Board._findTargetList([1,1,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY],singleEndList=[0,Board.__BORDER])
        Board._twoBlTargetList = [twoBl0TargetList,twoBl1TargetList]

        oneOpen0targetList = Board._findTargetList([0,Board.__CURPOS,Board.__EMPTY],doubleEndList=[Board.__EMPTY])
        oneOpen0targetListTemp = [np.asarray([Board.__EMPTY,0,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY])]
        Board._duplicateArrInOppDir(oneOpen0targetListTemp)
        oneOpen0targetList = np.vstack((oneOpen0targetList, oneOpen0targetListTemp))
        oneOpen1targetList = Board._findTargetList([1,Board.__CURPOS,Board.__EMPTY],doubleEndList=[Board.__EMPTY])
        oneOpen1targetListTemp = [np.asarray([Board.__EMPTY,1,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY])]
        Board._duplicateArrInOppDir(oneOpen1targetListTemp)
        oneOpen1targetList = np.vstack((oneOpen1targetList, oneOpen1targetListTemp))
        oneOpen0targetList2 = [np.asarray([Board.__EMPTY,0,Board.__EMPTY,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY])]
        oneOpen0targetList2 = Board._duplicateArrInOppDir(oneOpen0targetList2)
        oneOpen1targetList2 = [np.asarray([Board.__EMPTY,1,Board.__EMPTY,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY])]
        oneOpen1targetList2 = Board._duplicateArrInOppDir(oneOpen1targetList2)
        Board._oneOpentargetList = [oneOpen0targetList,oneOpen1targetList]
        Board._oneOpentargetList2 = [oneOpen0targetList2,oneOpen1targetList2]

        oneBl0TargetList = Board._findTargetList([0,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY,Board.__EMPTY],singleEndList=[1,Board.__BORDER])
        oneBl1TargetList = Board._findTargetList([1,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY,Board.__EMPTY],singleEndList=[0,Board.__BORDER])
        Board._oneBlTargetList = [oneBl0TargetList,oneBl1TargetList]

        return
    
    def _connectFour(self,arr,pos,playerId):
        start = time.perf_counter()
        # check cases that need only 1 stone to connect five or more stones
        # required array size: 1 +/- (winTarget-1)
        checkArr = self._getCheckArr(arr,pos)
        # 3 cases: (current pos denote as p)
        #targetList = self._findTargetList([playerId,playerId,playerId,playerId,Board.__CURPOS])
        if(self._checkAnyMatch(checkArr,Board._fourTargetList[playerId])):
            return True
        
        print("Four time: ", (time.perf_counter()-start)*1000)
        return False
    
    def _connectOpenThree(self,arr,pos,playerId):
        start = time.perf_counter()
        # check cases that need 1 stone to have unblocked connected four
        # required array size: 1 +/- (winTarget-1)
        checkArr = self._getCheckArr(arr,pos)
        # 2 cases:
        #targetList = self._findTargetList([playerId,playerId,playerId,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        if(self._checkAnyMatch(checkArr,Board._threeOpentargetList[playerId])):
            return True

        print("Open Three time: ", (time.perf_counter()-start)*1000)
        return False
    
    def _connectSpecialBlockThreeOpp(self,arr,pos,playerId,opponentId):
        start = time.perf_counter()
        # check special case of blocking opponent with an open three to make it a block four
        # required array size: 1 +/- (winTarget-1 + 2)
        checkArr = self._getCheckArr(arr,pos)

        # 2 cases: (current pos denote as p)
        # #   1. x_ooo_p or B_ooo_p
        # targetList = []
        # targetList.append(np.asarray([playerId,Board.__EMPTY,opponentId,opponentId,opponentId,Board.__EMPTY,Board.__CURPOS]))
        # targetList.append(np.asarray([Board.__BORDER,Board.__EMPTY,opponentId,opponentId,opponentId,Board.__EMPTY,Board.__CURPOS]))
        # self._duplicateArrInOppDir(targetList)
        # if(self._checkAnyMatch(checkArr,targetList)):
        #     return True
        
        # #   2. _xx_xp or _x_xxp or (flip) px_xx_ or pxx_x_
        # targetList = []
        # targetList.append(np.asarray([Board.__EMPTY,opponentId,opponentId,Board.__EMPTY,opponentId,Board.__CURPOS]))
        # targetList.append(np.asarray([Board.__EMPTY,opponentId,Board.__EMPTY,opponentId,opponentId,Board.__CURPOS]))
        # self._duplicateArrInOppDir(targetList)
        if(self._checkAnyMatch(checkArr,Board._threeSpOppBltargetList[playerId])):
            return True
        
        if(self._checkAnyMatch(checkArr,Board._threeSpOppBltargetList2[playerId])):
            return True

        print("Special Block Three Opp time: ", (time.perf_counter()-start)*1000)
        return False

    def _connectBlockThree(self,arr,pos,playerId,opponentId):
        start = time.perf_counter()
        # check cases that can create block 4 (only have 1 position can make to connect 5)
        # required array size: 1 +/- (winTarget-1 + 1)
        checkArr = self._getCheckArr(arr,pos)
        # n cases: (current pos denote as p)
        #   1 block with unique multiset of 3 stones and 2 spaces (1 space is the current position) in both directions
        #targetList = self._findTargetList([playerId,playerId,playerId,Board.__CURPOS,Board.__EMPTY],singleEndList=[opponentId,Board.__BORDER])
        if(self._checkAnyMatch(checkArr,Board._threeBlTargetList[playerId])):
            return True

        print("Block Three time: ", (time.perf_counter()-start)*1000)
        return False
    
    def _connectSpecialBlockThreePlayer(self,arr,pos,playerId):
        start = time.perf_counter()
        # check special case of reaching block four as player, that is not considered in normal block three
        # or not applicable to blocking opponent
        checkArr = self._getCheckArr(arr,pos)

        # 2 cases: (current pos denote as p)
        #   1. _xxx_p or p_xxx_
        # targetList = []
        # targetList.append(np.asarray([Board.__EMPTY,playerId,playerId,playerId,Board.__EMPTY,Board.__CURPOS]))
        # targetList.append(np.asarray([Board.__CURPOS,Board.__EMPTY,playerId,playerId,playerId,Board.__EMPTY]))
        # if(self._checkAnyMatch(checkArr,targetList)):
        #     return True

        # #   2. xx_xp or x_xxp or px_xx or pxx_x
        # targetList = []
        # targetList.append(np.asarray([playerId,playerId,Board.__EMPTY,playerId,Board.__CURPOS]))
        # targetList.append(np.asarray([playerId,Board.__EMPTY,playerId,playerId,Board.__CURPOS]))
        # targetList.append(np.asarray([Board.__CURPOS,playerId,Board.__EMPTY,playerId,playerId]))
        # targetList.append(np.asarray([Board.__CURPOS,playerId,playerId,Board.__EMPTY,playerId]))
        if(self._checkAnyMatch(checkArr,Board._threeSpPlyBltargetList[playerId])):
            return True
        if(self._checkAnyMatch(checkArr,Board._threeSpPlyBltargetList2[playerId])):
            return True

        print("Special Block Three Player time: ", (time.perf_counter()-start)*1000)
        return False
    
    def _connectOpenTwo(self,arr,pos,playerId):
        start = time.perf_counter()
        # check cases that need 1 stone to have unblocked connected four
        # required array size: 1 +/- (winTarget-1)
        checkArr = self._getCheckArr(arr,pos)
        # 2 cases:
        #   1. _xxp_
        # targetList = self._findTargetList([playerId,playerId,Board.__CURPOS],doubleEndList=[Board.__EMPTY])
        # if(self._checkAnyMatch(checkArr,targetList)):
        #     return True
        
        # #   2. _xx_p_ or _xp_x_ or _px_x_ or (flip) 
        # targetList = []
        # targetList.append(np.asarray([Board.__EMPTY,playerId,playerId,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY]))
        # targetList.append(np.asarray([Board.__EMPTY,playerId,Board.__CURPOS,Board.__EMPTY,playerId,Board.__EMPTY]))
        # targetList.append(np.asarray([Board.__EMPTY,Board.__CURPOS,playerId,Board.__EMPTY,playerId,Board.__EMPTY]))
        # self._duplicateArrInOppDir(targetList)
        if(self._checkAnyMatch(checkArr,Board._twoOpentargetList[playerId])):
            return True
        if(self._checkAnyMatch(checkArr,Board._twoOpentargetList2[playerId])):
            return True

        print("Open Two time: ", (time.perf_counter()-start)*1000)
        return False
    
    def _connectBlockTwo(self,arr,pos,playerId,opponentId):
        start = time.perf_counter()
        # check cases that can create block 4 (only have 1 position can make to connect 5)
        # required array size: 1 +/- (winTarget-1 + 1)
        checkArr = self._getCheckArr(arr,pos)
        # n cases: (current pos denote as p)
        #   1 block with unique multiset of 3 stones and 2 spaces (1 space is the current position) in both directions
        #targetList = self._findTargetList([playerId,playerId,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY],singleEndList=[opponentId,Board.__BORDER])

        if(self._checkAnyMatch(checkArr,Board._twoBlTargetList[playerId])):
            return True

        print("Block Two time: ", (time.perf_counter()-start)*1000)
        return False
    
    def _connectOpenOne(self,arr,pos,playerId):
        start = time.perf_counter()
        # check cases that need 1 stone to have unblocked connected four
        # required array size: 1 +/- (winTarget-1)
        checkArr = self._getCheckArr(arr,pos)
        # 3 cases:
        # #   1. _(xp_)_
        # targetList = self._findTargetList([playerId,Board.__CURPOS,Board.__EMPTY],doubleEndList=[Board.__EMPTY])
        # if(self._checkAnyMatch(checkArr,targetList)):
        #     return True
        
        # #   2. _x_p_ or (flip)
        # targetList = []
        # targetList.append(np.asarray([Board.__EMPTY,playerId,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY]))
        # self._duplicateArrInOppDir(targetList)
        # if(self._checkAnyMatch(checkArr,targetList)):
        #     return True
        
        # #   3. _x_ _p_ or (flip) 
        # targetList = []
        # targetList.append(np.asarray([Board.__EMPTY,playerId,Board.__EMPTY,Board.__EMPTY,Board.__CURPOS,Board.__EMPTY]))
        # self._duplicateArrInOppDir(targetList)
        if(self._checkAnyMatch(checkArr,Board._oneOpentargetList[playerId])):
            return True
        if(self._checkAnyMatch(checkArr,Board._oneOpentargetList2[playerId])):
            return True
        
        print("Open One time: ", (time.perf_counter()-start)*1000)
        return False

    def _connectBlockOne(self,arr,pos,playerId,opponentId):
        start = time.perf_counter()
        # check cases that can create block 4 (only have 1 position can make to connect 5)
        # required array size: 1 +/- (winTarget-1 + 1)
        checkArr = self._getCheckArr(arr,pos)
        # n cases: (current pos denote as p)
        #   1 block with unique multiset of 3 stones and 2 spaces (1 space is the current position) in both directions
        #targetList = self._findTargetList([playerId,Board.__CURPOS,Board.__EMPTY,Board.__EMPTY,Board.__EMPTY],singleEndList=[opponentId,Board.__BORDER])
        if(self._checkAnyMatch(checkArr,Board._oneBlTargetList[playerId])):
            return True
        
        print("Block One time: ", (time.perf_counter()-start)*1000)

        return False

    
# main game logics 
    def isPlayerWon(self,playerId,lastPlayCoord):
        # Check 4 directions, each direction check +/- self.winTarget-1, total 2*self.winTarget-2 cells        
        for dir in Board.Direction:
            arr,pos = self._getDirArrayAndPos(dir,lastPlayCoord,0)
            found,_ = Board._isNConnected(arr,pos,playerId,self.winTarget)
            if(found):  
                return True
      
        return False   
    
    def ruleRenjuBoard(self):
        # prohibit black 3-and-3, 4-and-4, overline

        return
    
    def ruleSwap2Board(self):

        return

# computer player (for connecting 5 stones for now)
    def getNextMove(self, playerId, opponentId):
        # computer player next move
        scoreBoard = np.zeros([self.size,self.size])
        selectedPos = None

        # check whole board
        score = 0
        for y in range(self.size):
            for x in range(self.size):
                if(self.at(x,y)==Board.__EMPTY):
                    for dir in Board.Direction:
                        print()
                        print()
                        print()
                        arr,pos = self._getDirArrayAndPos(dir,[x,y],2)
                        #print(arr.size,pos)

                        # next play win, highest score
                        if(self._connectFour(arr,pos,playerId)):
                            print("Four Player",x,y)
                            score = score + 1000000

                        # need to block opponent win
                        elif(self._connectFour(arr,pos,opponentId)):
                            print("Four Opp",x,y)
                            score = score + 100000
                        else:
                            # almost win with open three
                            if(self._connectOpenThree(arr,pos,playerId)):
                                print("Open Three Player",x,y)
                                score = score + 5000

                            # block opponent open three
                            if(self._connectOpenThree(arr,pos,opponentId)):
                                print("Open Three Opp",x,y)
                                score = score + 4000
                            if(self._connectSpecialBlockThreeOpp(arr,pos,playerId,opponentId)):
                                print("Special Block Three Opp",x,y)
                                score = score + 3500

                            # force opponent to block
                            if(self._connectBlockThree(arr,pos,playerId,opponentId)):
                                print("Block 3 Player",x,y)
                                score = score + 1000
                            if(self._connectSpecialBlockThreePlayer(arr,pos,playerId)):
                                print("Special Block Three Player",x,y)
                                score = score + 1000
                            if(self._connectOpenTwo(arr,pos,playerId)):
                                print("Open Two Player",x,y)
                                score = score + 1000

                            # prevent threat
                            if(self._connectOpenTwo(arr,pos,opponentId)):
                                print("Open Two Opp",x,y)
                                score = score + 500
                            if(self._connectBlockThree(arr,pos,opponentId,playerId)):
                                print("Block 3 Opp",x,y)
                                score = score + 500

                            # create a bit threat 
                            if(self._connectBlockTwo(arr,pos,playerId,opponentId)):
                                print("Block Two Player",x,y)
                                score = score + 100
                            if(self._connectOpenOne(arr,pos,playerId)):
                                print("Open One Player",x,y)
                                score = score + 100

                            
                            # prevent threat (conservative)
                            if(self._connectOpenOne(arr,pos,opponentId)):
                                print("Open One Player",x,y)
                                score = score + 10
                            if(self._connectBlockTwo(arr,pos,opponentId,playerId)):
                                print("Block Two Opp",x,y)
                                score = score + 10

                            # better than random
                            if(self._connectBlockOne(arr,pos,playerId,opponentId)):
                                print("Block One Player",x,y)
                                score = score + 2
                            if(self._connectBlockOne(arr,pos,opponentId,playerId)):
                                print("Block One Opp",x,y)
                                score = score + 1
                        



                    #score = score + 1 #temp


                scoreBoard[y][x] = score
                score = 0    

        selectedPos = np.unravel_index(scoreBoard.argmax(),scoreBoard.shape)
        selectedPos = np.flip(selectedPos)
        print("Done",selectedPos[0],selectedPos[1],scoreBoard[selectedPos[1]][selectedPos[0]])
        print(scoreBoard)
        return selectedPos
    