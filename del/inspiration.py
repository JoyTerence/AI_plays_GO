from copy import deepcopy
import math
import random

boardSize = 5

'''
Below segment is copied from read.py/write.py
'''
def readInput(n, path="input.txt"):

    with open(path, 'r') as f:
        lines = f.readlines()
        piece_type = int(lines[0])
        previous_board = [[int(x) for x in line.rstrip('\n')] for line in lines[1:n+1]]
        board = [[int(x) for x in line.rstrip('\n')] for line in lines[n+1: 2*n+1]]
        return piece_type, previous_board, board

'''
Below segment is copied from read.py/write.py
'''
def writeOutput(result, path="output.txt"):
    res = ""
    if result == "PASS":
        res = "PASS"
    else:
        res += str(result[0]) + ',' + str(result[1])

    with open(path, 'w') as f:
        f.write(res)



def resetMoveCount():
    with open("movecount.txt","w") as f:
        f.write("0")

def getMoveCount():
    count = 0
    with open("movecount.txt") as f:
        count = int(f.read())
    return count

def updateMoveCount(count):
    #print("move count = ",count)
    with open("movecount.txt","w") as f:
        f.write(str(count))
    f.close()

def isBoardEmpty(board):
    for i in range(boardSize):
        for j in range(boardSize):
            if board[i][j]!=0:
                return False
    return True

def getNeighbourPositions(i,j):
    neighbors = []
    if i > 0: neighbors.append((i-1, j))
    if i < boardSize - 1: neighbors.append((i+1, j))
    if j > 0: neighbors.append((i, j-1))
    if j < boardSize - 1: neighbors.append((i, j+1))
    return neighbors

def getOpponentNeighbourCount(board,i,j,piece_type):
    neighbors = getNeighbourPositions(i,j)
    count=0
    for i,j in neighbors:
        if board[i][j]==3-piece_type:
            count+=1
    return count

def getLibertyCount(board, k,l,piece_type, visited ):
    #print("Liberty check at ",k,l)
    current_pos_string= str(k)+"_"+str(l)
    neighbs = getNeighbourPositions(k,l)
    opponent_piece_type = 3-piece_type
    opponent_neighbs_count = 0
    friend_neighbs=[]
    c=0
    for i,j in neighbs :
        if board[i][j]==0:
            c+=1
        elif board[i][j]==opponent_piece_type:
            opponent_neighbs_count+=1
        elif str(i)+"_"+str(j) not in visited:
            friend_neighbs.append([i,j])
    if c:
        return c, visited

    # surrounded by opponents
    if opponent_neighbs_count == len(neighbs):
        return 0,visited

    visited.append(current_pos_string)
    neigbhsLibertyCount = 0
    neighbsVisited = []
    for i,j in friend_neighbs:
        currLib,neighbVisited = getLibertyCount(board,i,j,piece_type, visited )
        #print("at neighb ",i,j, "liberty = ",currLib)
        neigbhsLibertyCount = neigbhsLibertyCount + currLib
        neighbsVisited = visited + neighbVisited
        if neigbhsLibertyCount :
            return neigbhsLibertyCount,list(set(neighbsVisited ))

    return neigbhsLibertyCount,list(set(neighbsVisited ))

def removePiecesAtPositions(board, positions):
    for piece in positions:
        board[piece[0]][piece[1]] = 0
    return board

def getDeadPieces(board, piece_type):
    died_pieces = []
    allVisited = []
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == piece_type:
                if str(i)+"_"+str(j) in allVisited:
                    died_pieces.append((i,j))
                else:
                    hasLiberty, visited = getLibertyCount(board,i,j, piece_type,[])
                    if not hasLiberty:
                        allVisited = allVisited + visited
                        died_pieces.append((i,j))
    return died_pieces

def removeDeadPieces(board, piece_type):
    died_pieces = getDeadPieces(board,piece_type)
    if not died_pieces: return [],board
    board=removePiecesAtPositions(board,died_pieces)
    return died_pieces,board

def areBoardsEqual( board1, board2):
    for i in range(boardSize):
        for j in range(boardSize):
            if board1[i][j] != board2[i][j]:
                return False
    return True

'''
Below segment is copied from host.py
'''
def isPositionValid(board, i, j, piece_type):
    if not (i >= 0 and i < len(board)):
        return False
    if not (j >= 0 and j < len(board)):
        return False
    
    if board[i][j] != 0:
        return False
    test_board = deepcopy(board)
    test_board[i][j] = piece_type

    liberty_exists,_ = getLibertyCount(test_board,i,j,piece_type,[])
    #print("First liberty check : ",liberty_exists)
    if liberty_exists:
        return True

    opponent_piece_type = 3-piece_type
    dead_pieces,test_board = removeDeadPieces(test_board,opponent_piece_type)
    #visualize_board(test_board)
    liberty_exists,_ = getLibertyCount(test_board,i,j,piece_type,[])
    if not liberty_exists:
        return False
    else:
        if dead_pieces and areBoardsEqual(board, test_board):
            return False
    return True

'''
Below segment is copied from host.py
'''

def displayBoard(board):
    for i in range(boardSize):
        for j in range(boardSize):
            if board[i][j] == 0:
                print(' ', end=' ')
            elif board[i][j] == 1:
                print('X', end=' ')
            else:
                print('O', end=' ')
        print()
    print('-' * boardSize * 2)

def isLocInCenter(i,j):
    return i>0 and i<boardSize-1 and j>0 and j<boardSize-1



def getPositionsOfPiece(board,piece_type):
    my_piece_locs = []
    n = len(board)
    for i in range(n):
        for j in range(n):
            if board[i][j] == piece_type:
                my_piece_locs.append([i,j])
    return my_piece_locs

def getFirstOrderLibertyCount(board,piece_type):
    locs = getPositionsOfPiece(board,piece_type)
    totalLiberty = 0
    marked=[]
    for i,j in locs:
        neighbs = getNeighbourPositions(i,j)
        for k,l in neighbs:
            if board[k][l]==0:
                neighb_string = str(k)+"_"+str(l)
                if neighb_string not in marked:
                    totalLiberty+=1
                    marked.append(neighb_string)
    return totalLiberty

def getMaxDeadInNextStepPossible(board,piece):
    opp = 3-piece
    maxDead = 0
    for i in range(0,boardSize):
        for j in range(0,boardSize):
            if board[i][j]==0 and isPositionValid(board,i,j,opp):
                dp,_ = getResultBoard(board,[i,j],opp)
                if len(dp)>maxDead:
                    maxDead = len(dp) 
    return maxDead
    

def getSecondOrderLibertyCount(board,piece):
    locs = getPositionsOfPiece(board,piece)
    locsWithNoEmptyNeighb=[]
    for i,j in locs:
        neighbs = getNeighbourPositions(i,j)
        neighbNotEmptyCount = 0
        for k,l in neighbs:
            if board[k][l]!=0:
                neighbNotEmptyCount+=1
        if  neighbNotEmptyCount == len(neighbs):
            locsWithNoEmptyNeighb.append([i,j])
    
    return getTotalLibertyCountForPieceType(board,piece,locsWithNoEmptyNeighb) 

def getTotalLibertyCountForPieceType(board,piece, locs=[]):
    if not locs:
        locs = getPositionsOfPiece(board,piece)
    totalLiberty = 0
    Visted = []
    for i,j in locs:
        curr = str(i)+"_"+str(j)
        if  curr not in Visted:
            libCount,vis = getLibertyCount(board,i,j,piece,[])
            #print(i,j,libCount,visited)
            totalLiberty+=libCount
            for v in vis:
                if v!=curr and v not in Visted:
                    totalLiberty+=libCount
                    Visted.append(v)
    return totalLiberty

def getCountOfPiece(board,piece):
    count = 0
    n = len(board)
    for i in range(n):
        for j in range(n):
            if board[i][j] == piece:
                count+=1
    return count

def getEulerNumbberQuadType(board,i,j, piece_type): #quad till (i,j) = (i-1,j-1) (i-1,j) (i,j-1) (i,j)
    one = 0 if i-1 < 0 or j-1 <0 or board[i-1][j-1]!=piece_type else 1
    two = 0 if i-1 < 0 or j <0 or j>=boardSize or board[i-1][j]!=piece_type else 1
    three = 0 if i < 0 or i>=boardSize or j-1 <0  or board[i][j-1]!=piece_type else 1
    four = 0 if i < 0 or i>=boardSize or j<0 or j>=boardSize  or board[i][j]!=piece_type else 1
    sum = one+two+three+four
    if sum==1:
        return "q1"
    elif sum==2 and (\
         (  i-1>=0 and j-1>=0 and board[i-1][j-1]==piece_type and i<boardSize and j<boardSize and  board[i][j]==piece_type ) \
             or\
         ( i<boardSize and  j-1>=0 and  board[i][j-1]==piece_type and i-1>=0 and j<boardSize and board[i-1][j]==piece_type ) ):
        return "qd"
    elif sum==3:
        return "q3"
    return "none"
        
def getEulerNumberQuadDict(board,piece_type):
    quad_dict={"q1":0,"q3":0,"qd":0,"none":0}
    for i in range(0,boardSize+1):
        for j in range(0,boardSize+1):
            quad_dict[getEulerNumbberQuadType(board,i,j,piece_type)]+=1
    return quad_dict

def getEulerNumber(board,piece):
    quad_dict = getEulerNumberQuadDict(board,piece)
    euler =  (quad_dict["q1"]-quad_dict["q3"] + (2*quad_dict["qd"]))/4
    return euler
    
def getHolesCoveredByPiece(board,piece):
    total=0
    for i in range(boardSize):
        for j in range(boardSize):
            if board[i][j]==0:
                count = 0
                neighbs = getNeighbourPositions(i,j)
                for k,l in neighbs:
                    if board[k][l]==piece:
                        count+=1
                if count==len(neighbs):
                    total+=1
    return total

def calculateUtilityOfBoard(previous_board,board,my_piece, move_count, verbose = False):
    blackFirstOrderLiberty = getFirstOrderLibertyCount(board,1)
    blackSecondOrderLiberty = getSecondOrderLibertyCount(board,1)
    whiteFirstOrderLiberty = getFirstOrderLibertyCount(board,2)
    whiteSecondOrderLiberty = getSecondOrderLibertyCount(board,2)

    blackCount = getCountOfPiece(board,1)
    whiteCount = getCountOfPiece(board,2)

    blackEuler = getEulerNumber(board,1)
    whiteEuler = getEulerNumber(board,2)

    blackScore = blackCount
    whiteScore = whiteCount + 2.5

    blackPreviousCount = getCountOfPiece(previous_board,1)
    whitePreviousCount = getCountOfPiece(previous_board,2)
    
    deadBlack = 0 if blackPreviousCount<blackCount else blackPreviousCount-blackCount
    deadWhite = 0 if whitePreviousCount<whiteCount else whitePreviousCount-whiteCount

    if verbose:
        print("blackFirstOrderLiberty ",blackFirstOrderLiberty ,"whiteFirstOrderLiberty ",whiteFirstOrderLiberty)
        print("deadBlack ",deadBlack ,"deadWhite ",deadWhite)
        print("blackEuler ",blackEuler ,"whiteEuler ",whiteEuler)


    f1 = blackFirstOrderLiberty - whiteFirstOrderLiberty if my_piece==1 else  whiteFirstOrderLiberty - blackFirstOrderLiberty

    f2 = blackSecondOrderLiberty - whiteSecondOrderLiberty if my_piece==1 else  whiteSecondOrderLiberty - blackSecondOrderLiberty

    f4 = blackEuler - whiteEuler if my_piece==1 else  whiteEuler - blackEuler

    countDiff = blackCount-whiteCount if my_piece==1 else whiteCount - blackCount
    countDiffFactor = 4 if my_piece==1 else 2

    myScore = blackScore if my_piece==1 else whiteScore

    deadFactor = 2 if my_piece==1 else 1
    deadOppCount = deadWhite if my_piece==1 else deadBlack
    deadMyCount = deadBlack if my_piece==1 else deadWhite

    myPotentialDead = getMaxDeadInNextStepPossible(board,my_piece)
    # holesCoveredByMyPiece = getHolesCoveredByPiece(board,my_piece)

    if verbose:
        print("f1 ",f1," f4 ",f4,"(countDiffFactor*countDiff)",(countDiffFactor*countDiff),"myScore",myScore, "myPotentialDead",myPotentialDead)

    utility =  max(f1 , -4) - (4*f4)  + (countDiffFactor*countDiff)  + myScore 

    if my_piece==1:
        utility-=(0.5*myPotentialDead)

    return utility

def getResultBoard(board,action,piece_type):
    test_board = deepcopy(board)
    #print(action)
    test_board[action[0]][action[1]] = piece_type
    opponent = 3-piece_type
    dead_opponents, test_board = removeDeadPieces(test_board,opponent)
    return dead_opponents,test_board

def getOpponentDeathCountForAction(board,action,piece_type):
    dead_opponents,_ = getResultBoard(board,action,piece_type)
    return len(dead_opponents)

def sortMoves(board,moves,piece_type):
    d_moves=[]
    for move in moves:
        dead_opp = getOpponentDeathCountForAction(board,move,piece_type)
        opp_neighbs = getOpponentNeighbourCount(board,move[0],move[1],piece_type)
        d_moves.append([dead_opp,move,opp_neighbs])
    d_moves.sort(key=lambda x : (x[0],x[2]),reverse=True)
    moves = [x[1] for x in d_moves]
    return moves

def generateAllMoves(board,my_piece, moveCount):
        prioritizeCenterMoves = True if  moveCount<=10 else False
        #print(prioritizeCenterMoves)
        if prioritizeCenterMoves : 
            stable_center_moves = [[1,2],[2,1],[2,2],[2,3],[3,1]]
            corner_center_moves=[[1,1],[1,3],[3,1],[3,3]]
            stable_center_moves = sortMoves(board,stable_center_moves,my_piece)
            corner_center_moves = sortMoves(board,corner_center_moves,my_piece)

        moves=[]
        for i in range(0,boardSize):
            for j in range(0,boardSize):
                if board[i][j]==0:
                    moves.append([i,j])
        random.shuffle(moves)

        if prioritizeCenterMoves:
            n_moves= stable_center_moves+corner_center_moves
            for m in moves:
                if m not in n_moves:
                    n_moves.append(m)
            n_moves = sortMoves(board,n_moves,my_piece)
            return n_moves,(stable_center_moves or corner_center_moves)

        moves = sortMoves(board,moves,my_piece)
        return moves,False

def equalUtilityReplace(board,old_action, i, j,current_piece):

    return old_action =="PASS" or (not isLocInCenter(old_action[0],old_action[1]) and isLocInCenter(i,j))

def actionHasHigherUtility(board,action1,action2,piece,move_count):
    _,board1 = getResultBoard(board,action1,piece)
    _,board2 = getResultBoard(board,action2,piece)
    u1 = calculateUtilityOfBoard(board, board1,piece,move_count)
    u2 = calculateUtilityOfBoard(board,board2,piece,move_count)
    #print(action1, u1,action2, u2)
    return u1>u2

def actionCreatesMoreHoles(board,action1,action2,piece):
    _,board1 = getResultBoard(board,action1,piece)
    _,board2 = getResultBoard(board,action2,piece)
    h1 = getHolesCoveredByPiece(board1,piece)
    h2 = getHolesCoveredByPiece(board2,piece)
    return h1>h2

class MyPlayer():
    def __init__(self, piece_type):
        self.piece_type = piece_type
        self.minmax_depth = 3
        self.boardSize = 5

    def get_next_move(self,previous_board, board, moveCount):
        if self.piece_type==1 and moveCount==1:
            return [1,1]
        action = self.AlphaBetaSearch(previous_board,board, moveCount)
        return action

    

    def AlphaBetaSearch(self,previous_board,board, moveCount):
        value,action = self.MaxValue(board, previous_board, board,0,self.piece_type,0,-math.inf,math.inf,moveCount)
        print(action,value)
        return action
    
    def checkMinMaxLeafNode(self,depth,consecutive_pass_count,moveCount):
        if moveCount>24 or depth>=self.minmax_depth or consecutive_pass_count==2 :
            return True
        return False

    def getValidMoves(self,board,moves, piece_type):
        valid_moves=[]
        for i,j in moves:
            if isPositionValid(board,i, j, piece_type):
                valid_moves.append([i,j])
        return valid_moves

    def MaxValue(self, start_board, previous_board, board, depth,current_piece,consecutive_pass_count,alpha, beta,moveCount):

        action = "PASS"
        if self.checkMinMaxLeafNode(depth,consecutive_pass_count,moveCount):
            utility = calculateUtilityOfBoard(previous_board,board,self.piece_type,moveCount)
            return utility,action
        next_piece = 3-current_piece
        v = -math.inf

        moves, hasCenterMoves = generateAllMoves(board,self.piece_type, moveCount)
        valid_moves = self.getValidMoves(board,moves,current_piece)

        if not valid_moves:
            utility = calculateUtilityOfBoard(previous_board,board,self.piece_type,moveCount)
            return utility,action

        my_count = getCountOfPiece(board,self.piece_type)
        opponent_count = getCountOfPiece(board,3-self.piece_type)

        for i,j in valid_moves:

            dead_pieces,result_board = getResultBoard(board,[i,j],current_piece)
            # print(i,j,len(dead_pieces),areBoardsEqual(previous_board,result_board), not(dead_pieces and areBoardsEqual(previous_board,result_board)))
            if not(dead_pieces and areBoardsEqual(previous_board,result_board)):
                #print(i,j)
                my_new_count = getCountOfPiece(result_board,self.piece_type)
                dead_mine = 0 if my_count<my_new_count else my_count-my_new_count

                opponent_new_count = getCountOfPiece(result_board,3-self.piece_type)
                dead_opponents = 0 if opponent_count<opponent_new_count else opponent_count-opponent_new_count

                currval,minAction = self.MinValue(start_board, board,result_board,depth+1,next_piece,0,alpha, beta,moveCount+1)
                currval+=dead_opponents

                if (currval==v):
                    # if minAction!="PASS" and depth<=1:
                    #     print("opp action",minAction,"my old ",action,[i,j], dead_mine, dead_opponents,currval)
                    if equalUtilityReplace( result_board, action,i,j, current_piece):
                        v = currval
                        action=[i,j]
                elif currval>v :
                    v = currval
                    action = [i,j]

                #print("MaxValue depth = ", depth, "currval = ",currval,"v = ",v,i,j)

                if v>=beta:
                    return v,action
                
                alpha = max(alpha,v)
                
        return v,action

    def MinValue(self, start_board, previous_board, board, depth,current_piece,consecutive_pass_count,alpha, beta,moveCount):

        action = "PASS"
        if self.checkMinMaxLeafNode(depth,consecutive_pass_count,moveCount):
            utility = calculateUtilityOfBoard(previous_board,board,self.piece_type,moveCount)
            return utility,action
        next_piece = 3-current_piece
        v = +math.inf

        moves, hasCenterMoves = generateAllMoves(board,self.piece_type, moveCount)
        valid_moves = self.getValidMoves(board,moves,current_piece)

        if not valid_moves:
            utility = calculateUtilityOfBoard(previous_board,board,self.piece_type,moveCount)
            return utility,action

        my_count = getCountOfPiece(board,self.piece_type)
        opponent_count = getCountOfPiece(board,3-self.piece_type)
        #print(current_piece,valid_moves)
        for i,j in valid_moves:
            dead_pieces,result_board = getResultBoard(board,[i,j],current_piece)
            if not(dead_pieces and areBoardsEqual(previous_board,result_board)):

                opponent_new_count = getCountOfPiece(result_board,3-self.piece_type)
                dead_opponents = 0 if opponent_count<opponent_new_count else opponent_count-opponent_new_count

                currval,maxAction = self.MaxValue(start_board, board,result_board,depth+1,next_piece,0,alpha, beta,moveCount+1)

                currval+=dead_opponents

                if (currval==v): 
                    # if maxAction!="PASS" and depth<=1:
                    #     print("maxAction",maxAction)
                    if equalUtilityReplace( result_board, action,i,j, current_piece):
                        v = currval
                        action=[i,j]
                elif currval<v :
                    v = currval
                    action = [i,j]

                #print("MinValue depth = ", depth, "currval = ",currval,"v = ",v,i,j)

                if v<=alpha:
                    return v,action
                
                beta = min(beta,v)


        return v,action
 

'''
Below segment is copied from random_player 
'''

if __name__ == "__main__":
    N = 5   
    piece_type, previous_board, board = readInput(N)
    player = MyPlayer( piece_type)
    if(isBoardEmpty(previous_board)):
        resetMoveCount()
        moveCount = 1 if isBoardEmpty(board) else 2
    else:
        moveCount = getMoveCount()+2

    updateMoveCount(moveCount)

    print("move : ",moveCount)
    next_move = player.get_next_move(previous_board,board,moveCount)
    writeOutput(next_move)

    