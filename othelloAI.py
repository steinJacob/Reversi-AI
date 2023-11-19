######################################
## Name: Jacob Stein
## CWID: 10391595
## Class: CSC 475 001
## Assignment #3
## Date: 11/7/2023
## Description: An Othello (Reversi) program which supports both player vs. player and player vs. computer gameplay.
##              The artificial intelligence relies on the miniMax algorithm to make decisions on what move to make. In the source code, the settings can be changed to
##              show how many game states the algorithm considered, and how many layers deep into possible moves the algorithm will go. It is also possible to turn on
##              or off alpha-beta pruning.
######################################

#Used to copy the game board without changing the original
from copy import copy, deepcopy
DEBUG = False

#The board class. This creates an 8x8 board, and has functions to initiate the board to the starting set, and calculate scores. It also contains functions which
#depend on the moves made by the players, including inserting the move, and changing the pieces after said move. It also assists the player (and AI) by finding
#possible moves for the player (or AI) to make.
class Board:
    def __init__(self, board=[[0 for i in range(8)] for j in range(8)]):
        self.rows = 8
        self.cols = 8
        self.board = board
    
    #Initiates the board to the starting setup.
    def initiateBoard(self):
        self.board[3][3] = 1
        self.board[4][4] = 1
        self.board[3][4] = -1
        self.board[4][3] = -1
    
    #This function finds a list of possible moves for the player to make and returns it.
    def findPossibleMoves(self, playerNum, opponentNum):
        #Find all of the player's pieces currently on the board.
        arrayOfPieces = self.findAllPieces(playerNum)
        possibleMoveSet = []
        #For each of the player's pieces:
        for piece in arrayOfPieces:
            #Creates a range to search around the piece. The default area is the immediate 3x3 square around the piece, but account for edges
            x, y = piece
            xMin = x - 1
            xMax = x + 2
            yMin = y - 1
            yMax = y + 2
            if(x == 0):
                xMin = x
            elif(x == 7):
                xMax = x + 1
            if(y == 0):
                yMin = y
            elif(y == 7):
                yMax = y + 1
            
            #For each space surrounding the player's piece:
            for row in range(xMin, xMax):
                for col in range(yMin, yMax):
                    #If an opponents piece is next to the player's piece, continue in that direction to see if a piece can be placed in that direction
                    if(self.board[row][col] == opponentNum):
                        possibleMoveSet = self.continueInDirection(playerNum, opponentNum, piece, (row, col), possibleMoveSet)
        #Return the list of possible moves
        return possibleMoveSet

    #This function finds all of the player's pieces currently on the board and compiles them into a list and returns it.
    def findAllPieces(self, playerNum):
        allPieces = []
        for row in range(self.rows):
            for col in range(self.cols):
                if(self.board[row][col] == playerNum):
                    allPieces.append((row, col))
        return allPieces

    #Takes the coordinates of the player's piece and the opponent's piece and continues in the direction of the opponent's piece until
    #it reaches an empty space or the edge of the board. If it reaches an empty space, it adds the coordinates of that space to the possible moves list.
    def continueInDirection(self, playerNum, opponentNum, currTuple, directionTuple, possibleMoveSet):
        #Break the coordinates of the player's and opponent's pieces into rows and columns
        cX, cY = currTuple
        dX, dY = directionTuple

        #Find the difference between the x- and y-coordinates of the pieces
        xChange = dX - cX
        yChange = dY - cY

        #Starting at the opponent's piece, if the space at the current coordinate contains an opponent's piece, keep traveling in the direction
        xIter, yIter = directionTuple
        while(self.board[xIter][yIter] == opponentNum):
            xIter += xChange
            yIter += yChange
            #If the edge of the board is reached, there is no possible move, so return the current list back.
            if((xIter == -1 or xIter == 8) or (yIter == -1 or yIter == 8)):
                return possibleMoveSet
        #If the space at the end of the line of opponent's pieces is empty, add that space to the possible moves list.
        if(self.board[xIter][yIter] == 0):
            possibleMoveSet.append((xIter, yIter))
        #Return the list of possible moves.
        return possibleMoveSet
    
    #Insert the player's piece at the coordinates provided and switch the opponent's pieces that it flanks.
    def insertMove(self, playerNum, opponentNum, moveTuple):
        row, col = moveTuple
        self.board[row][col] = playerNum
        #Change the opponent's pieces that this move flanks.
        self.generateMoveResults(playerNum, opponentNum, moveTuple)
    
    #Change the opponent's pieces that are flanked by the previous move.
    def generateMoveResults(self, playerNum, opponentNum, moveTuple):
        x, y = moveTuple
        #Creates a range to search around the piece. The default area is the immediate 3x3 square around the piece, but account for edges
        xMin = x - 1
        xMax = x + 2
        yMin = y - 1
        yMax = y + 2
        if(x == 0):
            xMin = x
        elif(x == 7):
            xMax = x + 1
        if(y == 0):
            yMin = y
        elif(y == 7):
            yMax = y + 1

        #For each space next to the space of the player's move:
        for row in range(xMin, xMax):
            for col in range(yMin, yMax):
                #If the space contains an opponent's piece.
                if(self.board[row][col] == opponentNum):
                    directionTuple = row, col
                    #Find if the piece is flanked by the player. If it is, continue in the direction, keeping track of every space visited
                    #until you reach the player's piece or an edge/empty space. If a player's piece is found, change all the opponent's piece in the list.
                    outFlanks = self.directionFlanks(playerNum, moveTuple, directionTuple)
                    if(outFlanks):
                        indicesToSwap = self.indicesInDirection(playerNum, moveTuple, directionTuple)
                        for index in indicesToSwap:
                            i,o = index
                            self.board[i][o] = playerNum
    
    #Finds if the opponent's pieces touching the player's piece in a direction are flanked by another of the player's piece.
    def directionFlanks(self, playerNum, moveTuple, directionTuple):
        #Break the player's move and the opponent's piece into x and y components and find the difference between them.
        mX, mY = moveTuple
        dX, dY = directionTuple

        xChange = dX - mX
        yChange = dY - mY

        #Starting at the opponent's piece, keep following that direction until reaching a space that doesn't have an opponent's piece.
        #If the space has a player's piece, them return true.
        xIter, yIter = directionTuple
        while(self.board[xIter][yIter] != playerNum):
            xIter += xChange
            yIter += yChange
            if((xIter == -1 or xIter == 8) or (yIter == -1 or yIter == 8)):
                return False
        return True

    #Makes a list of all of the opponent's pieces that need to be changed because of the player's move.
    def indicesInDirection(self, playerNum, moveTuple, directionTuple):
        #Break the player's move and the opponent's piece into x and y components and find the difference between them.
        mX, mY = moveTuple
        dX, dY = directionTuple

        xChange = dX - mX
        yChange = dY - mY

        indicesToChange = [directionTuple]

        #Starting at the first opponent's piece, keep following that direction until reaching the player's piece, adding each space visited to the list
        #of spaces needed to become the player's piece.
        xIter, yIter = directionTuple
        while(self.board[xIter][yIter] != playerNum):
            indicesToChange.append((xIter, yIter))
            xIter += xChange
            yIter += yChange
        return indicesToChange
    
    #Finds if the game board is full.
    def isFull(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if(self.board[row][col] == 0):
                    return False
        return True
    
    #Calculates the score of the player. One player is counted positively while the other negatively. This setting is to assist in the miniMax algorithm.
    def calcScore(self, playerNum):
        score = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if(self.board[row][col] == playerNum):
                    score += self.board[row][col]
        return score

    #Prints the board. Black's pieces are represented as a 'B', white's pieces as a 'W', and empty spaces as empty.
    def printBoard(self):
        print("\t", end="")
        for col in range(self.cols):
            print(f"| C{col}\t", end="")
        print("\n")

        for row in range(self.rows):
            print(f"R{row}\t", end="")
            for col in range(self.cols):
                playerLetter = ' '
                if(self.board[row][col] == 1):
                    playerLetter = 'B'
                elif(self.board[row][col] == -1):
                    playerLetter = 'W'
                print(f"| {playerLetter}\t", end="")
            print()
            print("\t", end="")
            for col in range(self.cols):
                print("|-------", end="")
            print()
    
    #Prints the game board similar to printBoard(), but includes the list of spaces where the currently player could make possible moves.
    def printPossibleMoveBoard(self, possibleMoveSet, playerNum, blackIsPlayer):
        tempBoard = deepcopy(self.board)
        for posMove in possibleMoveSet:
            x, y = posMove
            tempBoard[x][y] = '*'
        
        print("\t", end="")
        for col in range(self.cols):
            print(f"| C{col}\t", end="")
        print("\n")

        #Changes the symbols to account for the player vs. computer game where the player uses white tokens.
        for row in range(self.rows):
            print(f"R{row}\t", end="")
            for col in range(self.cols):
                playerLetter = ' '
                if(blackIsPlayer):
                    if(tempBoard[row][col] == 1):
                        playerLetter = 'B'
                    elif(tempBoard[row][col] == -1):
                        playerLetter = 'W'
                    elif(tempBoard[row][col] == '*' and playerNum == 1):
                        playerLetter = '*'
                    elif(tempBoard[row][col] == '*' and playerNum == -1):
                        playerLetter = '+'
                else:
                    if(tempBoard[row][col] == 1):
                        playerLetter = 'W'
                    elif(tempBoard[row][col] == -1):
                        playerLetter = 'B'
                    elif(tempBoard[row][col] == '*' and playerNum == 1):
                        playerLetter = '+'
                    elif(tempBoard[row][col] == '*' and playerNum == -1):
                        playerLetter = '*'
                print(f"| {playerLetter}\t", end="")
            print()
            print("\t", end="")
            for col in range(self.cols):
                print("|-------", end="")
            print()

#Player class. Keeps track of the player's number of pieces, the number to identify his pieces, and score.
class Player:
    def __init__(self, number):
        self.number = number
        self.piecesLeft = 32
        self.score = number * 2

#The AI class, which plays as the computer. Also tracks pieces left, score, and number to identify its pieces. Also includes the algorithm and heuristic
#to decide which move to make on its turn.
class OthelloAI:
    #Constructor. Tracks identfying number, pieces left, and score just like a player.
    def __init__(self, number):
        self.number = number
        self.piecesLeft = 32
        self.score = number * 2
    
    #Algorithm used to determine moves. Relies on the miniMax algorithm. Recursively calls itself and tests moves until a set depth and returns the score of the deepest
    #move recursively up to the first call. Accounts for both players playing optimally and using the same heuristic. 
    #Also allows for Alpha-Beta pruning to improve performance without changing the algorithms result.
    def miniMax(self, board, depth, alpha, beta, playerNum, consideredMoves, abON):
        #Creates a deepcopy of the board to test different move choices.
        tempBoard = deepcopy(board)
        testGame = Board(tempBoard)
        #Finds the possible moves of the player. The player alternates for each recursive call of the function.
        availableMoves = testGame.findPossibleMoves(playerNum, playerNum * -1)

        #If at the deepest level of the function or there are no more available moves, return the heuristic score of the move and the number of considered moves.
        if((depth == 0) or (len(availableMoves) == 0)):
            bestMove = None
            #Heuristic
            score = self.heuristic(testGame, playerNum)
            return bestMove, score, consideredMoves
        
        #If it is the minimizing player (always the AI)
        if(playerNum < 0):
            bestScore = 64
            bestMove = None
        
            #For each possible move:
            for moveTuple in availableMoves:
                #Insert the move into the board. The call this function again with the new testing board.
                testGame.insertMove(playerNum, playerNum * -1, moveTuple)
                #If debug mode is activated, print the testing board and how many mvoes have been considered so far.
                if(DEBUG):
                    print(f"TESTING CASE. DEPTH: {depth}, CONSIDERED MOVES: {consideredMoves}")
                    testGame.printBoard()
                #Call the function again with the adjusted testing board.
                rMove, rScore, consideredMoves = self.miniMax(testGame.board, depth -1, alpha, beta, playerNum * -1, consideredMoves + 1, abON)

                #If the returned score is less than the best score (least score), replace the current score and move with the new (better) ones.
                if(rScore < bestScore):
                    bestScore = rScore
                    bestMove = moveTuple

                #If alpha-beta pruning is active, take the minimum of the beta and the best score. If the beta becomes less than the alpha, break the loop.
                if(abON):
                    beta = min(beta, bestScore)
                    if(beta <= alpha):
                        break
                
                #Return the testGame board to where it was.
                testGame = Board(tempBoard)
        
        #If the player is the maximizing player:
        if(playerNum > 0):
            bestScore = -64
            bestMove = None

            #For each possible move:
            for moveTuple in availableMoves:
                #Insert the move into the board. The call this function again with the new testing board.
                testGame.insertMove(playerNum, playerNum * -1, moveTuple)
                #If debug mode is activated, print the testing board and how many mvoes have been considered so far.
                if(DEBUG):
                    print(f"TESTING CASE. DEPTH: {depth}, CONSIDERED MOVES: {consideredMoves}")
                    testGame.printBoard()
                #Call the function again with the adjusted testing board.
                rMove, rScore, consideredMoves = self.miniMax(testGame.board, depth -1, alpha, beta, playerNum * -1, consideredMoves + 1, abON)
            
                #If the returned score is greater than the best score (highest score), replace the current score and move with the new (better) ones.
                if(rScore > bestScore):
                    bestScore = rScore
                    bestMove = moveTuple

                #If alpha-beta pruning is active, take the maximum of the alpha and the best score. If the alpha becomes greater than the beta, break the loop.
                if(abON):
                    alpha = max(alpha, bestScore)
                    if(beta <= alpha):
                        break
            
                #Return the testGame board to where it was.
                testGame = Board(tempBoard)
        
        if(bestMove == None):
            bestMove = availableMoves[0]
        return bestMove, bestScore, consideredMoves
    
    #Heuristic used to score each game state for miniMax algorithm to choose its move. 
    #Heuristics found at website: https://kartikkukreja.wordpress.com/2013/03/30/heuristic-function-for-reversiothello/
    def heuristic(self, testGame, playerNum):
        #Heuristic comparing player's pieces to opponent's pieces * 100
        playerScore = testGame.calcScore(playerNum)
        opponentScore = testGame.calcScore(playerNum * -1)
        scoreCompH = 100 * ((playerScore + opponentScore) / (abs(playerScore) + abs(opponentScore)))

        #Heuristic comparing # of player's moves to # of opponent's moves * 100
        playerNumMoves = len(testGame.findPossibleMoves(playerNum, playerNum * -1))
        opponentNumMoves = len(testGame.findPossibleMoves(playerNum * -1, playerNum))
        if(not (playerNumMoves + opponentNumMoves == 0)):
            movesNumH = 50 * ((playerNumMoves - opponentNumMoves) / (playerNumMoves + opponentNumMoves))
        else:
            movesNumH = 0
        #Heuristic comparing player's corners captured to opponent's * 100
        cornersArray = [(0, 0), (7, 0), (0, 7), (7, 7)]
        playerCorScore = 0
        opponentCorScore = 0
        for corner in cornersArray:
            x, y = corner
            if(testGame.board[x][y] == playerNum):
                playerCorScore += 1
            elif(testGame.board[x][y] == (playerNum * -1)):
                opponentCorScore += 1
        if(not (playerCorScore + opponentCorScore == 0)):
            cornerScore = 100 * (playerCorScore - opponentCorScore) / (playerCorScore + opponentCorScore)
        else:
            cornerScore = 0
        
        #Compares the amount of side spaces each player occupies
        sideCompH = 0
        playerSidePieces = 0
        opponentSidePieces = 0
        for row in range(len(testGame.board)):
            for col in range(len(testGame.board[row])):
                if(row == 0 or row == 7) or (col == 0 or col == 7):
                    if(testGame.board[row][col] == playerNum):
                        playerSidePieces += 1
                    elif(testGame.board[row][col] == (playerNum * -1)):
                        opponentSidePieces += 1
        if(not (playerSidePieces + opponentSidePieces == 0)):
            sideCompH = 100 * (playerSidePieces - opponentSidePieces) / (opponentSidePieces + playerSidePieces)
        #Average all heuristics together and return
        return (scoreCompH + movesNumH + cornerScore + sideCompH) / 4


###MAIN###
#DEFAULT VALUES:
miniMaxDepth = 4
alpha = -64
beta = 64

print("Welcome to Othello (Reversi)!")
response = input("If you would like to play against a person, press 1. Otherwise, enter any other key.")
#2-player version of the game.
if(response == "1"):
    black = Player(1)
    white = Player(-1)

    #Initiates the board and prints it out.
    game = Board()
    game.initiateBoard()
    game.printBoard()

    #Starts with black's turn.
    blacksTurn = True
    #Game loop. Continues until one player runs out of pieces or the entire board is full.
    while((black.piecesLeft != 0 and white.piecesLeft != 0) and (not game.isFull())):
        possibleMoves = []
        print()
        #Finds the possible moves of the current player and puts them into a list. Also prints out a board with a visual aid showing the current player's possible moves.
        if(blacksTurn):
            print("Possible moves are indicated by a '*'")
            possibleMoves = game.findPossibleMoves(black.number, white.number)
            game.printPossibleMoveBoard(possibleMoves, black.number, True)
            print(f"Score: Black: {black.score} White: {white.score}; Black's turn.")
        else:
            print("Possible moves are indicated by a '+'")
            possibleMoves = game.findPossibleMoves(white.number, black.number)
            game.printPossibleMoveBoard(possibleMoves, white.number, True)
            print(f"Score: Black: {black.score} White: {white.score}; White's turn.")
        print("\n")
        
        #If the list of possible moves is not empty, continue with the current player's turn.
        if(not (possibleMoves == [])):
            #Loop continues until the player enters a move present in the list of possible moves.
            validMove = False
            while(not validMove):
                try:
                    moveRow = int(input("Your move's row: "))
                    moveCol = int(input("Your move's column: "))
                except ValueError:
                    print("Invalid input. Please input an integer.")
                moveT = moveRow, moveCol
                for possible in possibleMoves:
                    if(possible == moveT):
                        validMove = True
                if(not validMove):
                    print("Please enter a valid move.")
            
            #If it is black's turn: insert the player's move choice, take away a piece from black's pool, and calculate the score.
            if(blacksTurn):
                game.insertMove(black.number, white.number, moveT)
                black.piecesLeft -= 1
                black.score = game.calcScore(black.number)
                white.score = game.calcScore(white.number)
            #If it is white's turn: insert the player's move choice, take away a piece from white's pool, and calculate the score.
            else:
                game.insertMove(white.number, black.number, moveT)
                white.piecesLeft -= 1
                white.score = game.calcScore(white.number)
                black.score = game.calcScore(black.number)
        #Switch the current player's turn.
        blacksTurn = not blacksTurn
    #If the board is full or a player runs out of pieces, print the final board, calculate the final score, and print the winner.
    game.printBoard()
    if(abs(black.score) > abs(white.score)):
        print("Game Over. Black wins!")
    else:
        print("Game Over. White wins!")
#If the user chose to play against the computer (AI)
else:
    colorChoice = input("Please pick a color, black or white. Black goes first. ")
    #If the user chooses to play as black.
    if(colorChoice == "black" or colorChoice == "Black" or colorChoice == "BLACK"):
        #Black is initiated as a player, while white becomes an AI object. Initiate the board and print it out.
        black = Player(1)
        white = OthelloAI(-1)
        game = Board()
        game.initiateBoard()
        game.printBoard()

        #Begins on black's turn. DEBUG and alphaBetaON are False by default.
        blacksTurn = True
        alphaBetaON = False
        #Game loop. Continues until a player runs out of pieces or the entire board is filled.
        while((black.piecesLeft != 0 and white.piecesLeft != 0) and (not game.isFull())):
            possibleMoves = []
            print()
            #Finds the possible moves of the current player and puts them into a list. Also prints out a board with a visual aid showing the current player's possible moves.
            if(blacksTurn):
                print("Possible moves are indicated by a '*'")
                possibleMoves = game.findPossibleMoves(black.number, white.number)
                game.printPossibleMoveBoard(possibleMoves, black.number, True)
                #Gives the player the choice before each turn to turn OFF/ON Debug mode and alpha-beta pruning
                print(f"Score: Black: {abs(black.score)} White: {abs(white.score)}; Black's turn.")
                if(not DEBUG):
                    debugChoice = input("If you would like to turn on DEBUG mode, enter any key. If not, press enter.")
                    if(not(debugChoice == "")):
                        DEBUG = True
                else:
                    debugChoice = input("If you would like to turn off DEBUG mode, enter any key. If not, press enter.")
                    if(not(debugChoice == "")):
                        DEBUG = False
                
                if(not alphaBetaON):
                    abChoice = input("If you would like to turn on Alpha-Beta Pruning, enter any key. If not, press enter.")
                    if(not(abChoice == "")):
                        alphaBetaON = True
                else:
                    abChoice = input("If you would like to turn off Alpha-Beta Pruning, enter any key. If not, press enter.")
                    if(not(abChoice == "")):
                        alphaBetaON = False
            else:
                print("Possible moves are indicated by a '+'")
                possibleMoves = game.findPossibleMoves(white.number, black.number)
                game.printPossibleMoveBoard(possibleMoves, white.number, True)
                print(f"Score: Black: {abs(black.score)} White: {abs(white.score)}; White's turn.")
            print("\n")

            if(blacksTurn):
                #If the list of possible moves is not empty, continue with the current player's turn.
                if(not (possibleMoves == [])):
                    #Loop continues until the player insert a move present in the list of possible moves.
                    validMove = False
                    while(not validMove):
                        try:
                            moveRow = int(input("Your move's row: "))
                            moveCol = int(input("Your move's column: "))
                        except ValueError:
                            print("Invalid input. Please input an integer.")
                        moveT = moveRow, moveCol
                        for possible in possibleMoves:
                            if(possible == moveT):
                                validMove = True
                        if(not validMove):
                            print("Please enter a valid move.")
                    
                    #Insert's the player's move choice, takes away a piece from their pool, and calculates the new score.
                    game.insertMove(black.number, white.number, moveT)
                    black.piecesLeft -= 1
                    black.score = game.calcScore(black.number)
                    white.score = game.calcScore(white.number)
            #The AI's turn.
            else:
                if(not (possibleMoves == [])):
                    print("Computer is thinking...")
                    #Receives the results from the miniMax algorithm of the current board and possible moves. Depth, Alpha, Beta, and the alphaBetaON switch is passed in.
                    moveT, moveScore, consideredMoves = white.miniMax(game.board, miniMaxDepth, alpha, beta, white.number, 0, alphaBetaON)
                    #Prints out how many moves were considered and the heuristic score of the move chosen by the algorithm.
                    print(f"Number of moves considered: {consideredMoves}")
                    print(f"Heuristic score of computer's move: {moveScore}")
                    #Inserts the AI's chosen move, takes a piece away from the AI's pool, and calculates the new score.
                    game.insertMove(white.number, black.number, moveT)
                    white.piecesLeft -= 1
                    black.score = game.calcScore(black.number)
                    white.score = game.calcScore(white.number)
            #Switches the current player's move.
            blacksTurn = not blacksTurn
        #After the game loop ends, print out the final board and reveal the winner.
        game.printBoard()
        if(abs(black.score) > abs(white.score)):
            print("Game Over. Black wins!")
        else:
            print("Game Over. White wins!")
    #The player chose to play as white.
    else:
        #Black is initiated as an AI object and white becomes a player. The board is initiated and printed out.
        black = OthelloAI(-1)
        white = Player(1)
        game = Board()
        game.initiateBoard()
        game.printBoard()

        #Black goes first. Debug mode and alpha-beta pruning is off by default.
        blacksTurn = True
        alphaBetaON = False
        #Game loop. Continues until a player runs out of pieces or the entire board is filled.
        while((black.piecesLeft != 0 and white.piecesLeft != 0) and (not game.isFull())):
            possibleMoves = []
            print()
            if(not blacksTurn):
                #Finds all possible moves for the current player and puts them into a list.
                print("Possible moves are indicated by a '*'")
                possibleMoves = game.findPossibleMoves(white.number, black.number)
                game.printPossibleMoveBoard(possibleMoves, white.number, False)
                print(f"Score: Black: {abs(black.score)} White: {abs(white.score)}; White's turn.")
                #Allows the player to turn ON/OFF debug mode and alpha-beta pruning before each turn.
                if(not DEBUG):
                    debugChoice = input("If you would like to turn on DEBUG mode, enter any key. If not, press enter.")
                    if(not(debugChoice == "")):
                        DEBUG = True
                else:
                    debugChoice = input("If you would like to turn off DEBUG mode, enter any key. If not, press enter.")
                    if(not(debugChoice == "")):
                        DEBUG = False
                
                if(not alphaBetaON):
                    abChoice = input("If you would like to turn on Alpha-Beta Pruning, enter any key. If not, press enter.")
                    if(not(abChoice == "")):
                        alphaBetaON = True
                else:
                    abChoice = input("If you would like to turn off Alpha-Beta Pruning, enter any key. If not, press enter.")
                    if(not(abChoice == "")):
                        alphaBetaON = False
            else:
                print("Possible moves are indicated by a '+'")
                possibleMoves = game.findPossibleMoves(black.number, white.number)
                game.printPossibleMoveBoard(possibleMoves, black.number, False)
                print(f"Score: Black: {abs(black.score)} White: {abs(white.score)}; Black's turn.")
            print("\n")

            #The player's (white's) turn.
            if(not blacksTurn):
                #If there are possible moves.
                if(not (possibleMoves == [])):
                    #Loop continues until the player inserts a move present in the list of possible moves.
                    validMove = False
                    while(not validMove):
                        try:
                            moveRow = int(input("Your move's row: "))
                            moveCol = int(input("Your move's column: "))
                        except ValueError:
                            print("Invalid input. Please input an integer.")
                        moveT = moveRow, moveCol
                        for possible in possibleMoves:
                            if(possible == moveT):
                                validMove = True
                        if(not validMove):
                            print("Please enter a valid move.")
                    
                    #Insert's the player move, removes a piece from their pool, and calculates the new score.
                    game.insertMove(white.number, black.number, moveT)
                    white.piecesLeft -= 1
                    black.score = game.calcScore(black.number)
                    white.score = game.calcScore(white.number)
            #Computer's turn.
            else:
                if(not (possibleMoves == [])):
                    print("Computer is thinking...")
                    #Receives the results from the miniMax algorithm of the current board and possible moves. Depth, Alpha, Beta, and the alphaBetaON switch is passed in.
                    moveT, moveScore, consideredMoves = black.miniMax(game.board, miniMaxDepth, alpha, beta, black.number, 0, alphaBetaON)
                    #Prints the number of moves considered by the algorithm and the heuristic score of the chosen move.
                    print(f"Number of moves considered: {consideredMoves}")
                    print(f"Heuristic score of computer's move: {moveScore}")
                    #Insert's the AI's move, removes a piece from its pool, and calculates the new score.
                    game.insertMove(black.number, white.number, moveT)
                    black.piecesLeft -= 1
                    black.score = game.calcScore(black.number)
                    white.score = game.calcScore(white.number)
            #Switches the current player's turn.
            blacksTurn = not blacksTurn
        #At the end of the game, print the final board and reveal the winner.
        game.printBoard()
        if(abs(black.score) > abs(white.score)):
            print("Game Over. Black wins!")
        else:
            print("Game Over. White wins!")