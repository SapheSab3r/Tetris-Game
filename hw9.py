#################################################
# hw9.py: Tetris!
#
# Your name: Anqi Chen 
# Your andrew id: aac2 
#
# Your partner's name: Guotong Sun & Minseo(Hailey) Kwon
# Your partner's andrew id: guotongs & minseok
#################################################

import cs112_n21_week4_linter
import math, copy, random

from cmu_112_graphics import *

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################################################
# Functions for you to write
#################################################

def appStarted(app):
    app.rows, app.cols, app.cellSize, app.margin = gameDimensions()
    app.emptyColor = 'royalBlue'
    app.board = [([app.emptyColor] * app.cols) for row in range(app.rows)]
    app.tetrisPieces = []
    app.tetrisPieceColors = []
    app.fallingPiece = []
    app.fallingColor = ''
    app.score = 0

    fallingPieces(app)
    newFallingPiece(app)

    app.fallingPieceRow = 0
    app.fallingPieceCol = app.cols // 2 - len(app.fallingPiece[0]) // 2
    
    app.isGameOver = False
    app.paused = False
    app.timerDelay = 400

#get the top-left and bottom-right of a rectangle 
def getCellBounds(app, row, col):
    boardWidth = app.width - app.margin * 2
    boardHeight = app.height - app.margin * 2 

    x0 = app.margin + boardWidth  * col / app.cols
    y0 = app.margin + boardHeight * row / app.rows 
    x1 = app.margin + boardWidth * (col + 1) / app.cols
    y1 = app.margin + boardHeight * (row + 1) / app.rows
    return x0, y0, x1, y1

#store all the shapes of the falling pieces 
def fallingPieces(app):
    sPiece = [
        [ False,  True,  True ],
        [ True,  True, False ]
    ]

    iPiece = [
        [  True,  True,  True,  True ]
    ]

    jPiece = [
        [  True, False, False ],
        [  True,  True,  True ]
    ]

    lPiece = [
        [ False, False,  True ],
        [  True,  True,  True ]
    ]

    oPiece = [
        [  True,  True ],
        [  True,  True ]
    ]

    tPiece = [
        [ False,  True, False ],
        [  True,  True,  True ]
    ]

    zPiece = [
        [  True,  True, False ],
        [ False,  True,  True ]
    ]
    app.tetrisPieces = [iPiece, jPiece, lPiece, oPiece, sPiece, tPiece, zPiece]
    app.tetrisPieceColors = ['red', 'yellow', 'magenta', 'pink', 'cyan', 
                                'green', 'orange']
    
#select a random piece from the falling piece each time 
def newFallingPiece(app):
    pieceIndex = random.randint(0, len(app.tetrisPieces) - 1)
    colorIndex = random.randint(0, len(app.tetrisPieceColors) - 1)

    #update the falling piece and its color 
    app.fallingPiece = app.tetrisPieces[pieceIndex]
    app.fallingColor = app.tetrisPieceColors[colorIndex]

    #reset the new piece's falling position 
    app.fallingPieceRow = 0
    app.fallingPieceCol = app.cols // 2 - len(app.fallingPiece[0]) // 2

    if fallingPieceIsLegal(app) == False:
        app.isGameOver = True
            
#rotate the current falling piece (counterclockwise)
def rotateFallingPiece(app):
    currPiece = app.fallingPiece
 
    #old piece rows and cols
    numOldRows, numOldCols = len(app.fallingPiece), len(app.fallingPiece[0])

    #new piece rows and cols (old rows = new cols, old cols = new rows)
    numNewRows, numNewCols = len(app.fallingPiece[0]), len(app.fallingPiece)

    #make a new 2d-list for the rotated piece 
    newPiece = []
    newPiece = [([None] * numNewCols) for row in range(numNewRows)]

    #creating the new piece from rotation
    #replacing newPiece col and row with 'True'
    for r in range(numOldRows):
        for c in range(numOldCols):
            if app.fallingPiece[r][c] == True:
                newRow = numNewRows - 1 - c
                newCol = r
                newPiece[newRow][newCol] = True
    app.fallingPiece = newPiece
    
    if not fallingPieceIsLegal(app):
        app.fallingPiece = currPiece


def timerFired(app):
    if app.isGameOver == True or app.paused == True:
        return 

    #place a new piece each time an old piece is placed 
    # (also checking if it is legal)
    takeStep(app)
    
#rotate or move the piece 
def takeStep(app):
    if moveFallingPiece(app, +1, 0) == False:
        placeFallingPiece(app)
        newFallingPiece(app)
        fallingPieceIsLegal(app)

def keyPressed(app, event):  
    #restart the game
    if event.key == 'r':
        appStarted(app)

    elif app.isGameOver == True:
        return 

    #key presses change piece direction 
    elif event.key == 'Left':
        moveFallingPiece(app, 0, -1)

    elif event.key == 'Right':
        moveFallingPiece(app, 0, +1)

    elif event.key == 'Down':
        moveFallingPiece(app, +1, 0)

    #key press that rotates the piece 
    elif event.key == 'Up':
        rotateFallingPiece(app)

    #hard-drop 
    elif event.key == 'Space':
        while moveFallingPiece(app, +1, 0):
            moveFallingPiece(app, +1, 0)

    #pause the game 
    elif event.key == 'p':
        app.paused = not app.paused

    #make steps(can check/ move to the next step of the game) after pausing 
    elif event.key == 's' and app.paused == True:
        takeStep(app)


#move the falling piece a given number of rows and cols 
def moveFallingPiece(app, drow, dcol): # drow means change in row; 
                                       # dcol is change in col
    currRow = app.fallingPieceRow
    currCol = app.fallingPieceCol
    
    app.fallingPieceRow += drow
    app.fallingPieceCol += dcol

    if not fallingPieceIsLegal(app):
        app.fallingPieceRow = currRow
        app.fallingPieceCol = currCol
        return False
    return True 

#place the piece on the board 
def placeFallingPiece(app):
    for row in range(len(app.fallingPiece)):
        for col in range(len(app.fallingPiece[0])):
            if app.fallingPiece[row][col] == True: 
                placeRow = row + app.fallingPieceRow 
                placeCol = col + app.fallingPieceCol
                placeColor = app.fallingColor
                app.board[placeRow][placeCol] = placeColor

    removeFullRows(app)

#check if the piece move outside the grid or overlap with the four boxes
def fallingPieceIsLegal(app):
    rows, cols = len(app.fallingPiece), len(app.fallingPiece[0])
          
    for row in range(rows):
        for col in range(cols):
            newCellRow = app.fallingPieceRow + row 
            newCellCol = app.fallingPieceCol + col 

            #first check if the piece is in the board
            if (app.fallingPiece[row][col] == True and 
                    newCellRow < 0 or newCellRow > app.rows - 1
                    or newCellCol < 0 or newCellCol > app.cols - 1): 
                return False 

            #if the piece is in the board then check if it overlaps with the 
            #filled cells
            elif (app.fallingPiece[row][col] == True and 
                (app.board[newCellRow][newCellCol] != app.emptyColor)):
                return False
    return True

#remove the row if it is full 
def removeFullRows(app):
    newBoard = []
    count = 0 
    numFullRows = 0

    #going through the orginal board and see if any cell is not blue color 
    for row in range(len(app.board)):
        for col in range(len(app.board[0])):
            if app.board[row][col] != app.emptyColor:
                count += 1
        #after going through one row and check the count with columns/row 
        if count != app.cols:
            newBoard.append(app.board[row])
            count = 0
        else:
            numFullRows += 1
            count = 0
            
    #adding empty row to the new board 
    while len(newBoard) < len(app.board):
        for r in range(numFullRows):
            newBoard.insert(0, [app.emptyColor] * app.cols)

    app.board = newBoard
    app.score += numFullRows ** 2

#draw the Tetris Game 
def drawBackground(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, outline = 'orange', 
                            fill ='orange')

def drawBoard(app, canvas):
    rows, cols = len(app.board), len(app.board[0])
    for row in range(rows):
        for col in range(cols):
            drawCell(app, canvas, row, col, app.board[row][col])

def drawScore(app, canvas):
    canvas.create_text(app.width / 2, app.margin, 
                        font = 'aerial 16 bold',
                        text = f'Score: {app.score}', 
                        fill = app.emptyColor, anchor = 's')

def drawCell(app, canvas, row, col, color):
    x0, y0, x1, y1 = getCellBounds(app, row, col)
    canvas.create_rectangle(x0, y0, x1, y1, fill = color, width = 3)

def drawFallingPiece(app, canvas):
    rows, cols = len(app.fallingPiece), len(app.fallingPiece[0])

    for r in range(rows):
        for c in range(cols):
            if app.fallingPiece[r][c] == True: 
                drawCell(app, canvas, r + app.fallingPieceRow, 
                            c + app.fallingPieceCol, app.fallingColor)

def drawGameOver(app, canvas):
    Xcell = (app.width - app.margin * 2) / app. cols
    Ycell = (app.height - app.margin * 2) / app.rows

    if app.isGameOver == True:
        canvas.create_rectangle(app.margin, Ycell * 2 + app.margin,
                                    app.margin + app.cols * Xcell,
                                    app.margin + 4 * Ycell, 
                                fill = 'black')


        canvas.create_text(app.width / 2, app.margin + 2 * Ycell + Ycell, 
                            font = 'aerial 24 bold', fill = 'orange',
                            text = 'Game Over!', anchor = 'center')

def redrawAll(app, canvas):
    drawBackground(app, canvas)
    drawBoard(app, canvas)
    drawScore(app, canvas)
    drawFallingPiece(app, canvas)
    drawGameOver(app, canvas)

def gameDimensions():
    rows = 15
    cols = 10
    cellSize = 20
    margin = 25
    return (rows, cols, cellSize, margin)

def playTetris():
    rows, cols, cellSize, margin = gameDimensions()

    width = 2 * margin + cellSize * cols
    height = 2 * margin + cellSize * rows 
    runApp(width=width, height=height)


#################################################
# main
#################################################

def main():
    cs112_n21_week4_linter.lint()
    playTetris()

if __name__ == '__main__':
    main()
