import time

from networking import *

timestr = time.strftime("%Y%m%d-%H%M%S")

myID, gameMap = getInit()
from os import path
botName = path.splitext(__file__)[0]

sendInit(botName)
logFile = open(botName + "game" + timestr + ".log", 'w')

from geographic_utils import moveToString, createMove, myCenter


turn = 0
while True:
    turn += 1
    moves = []
    gameMap = getFrame()
    my_center = myCenter()
    myX, myY = my_center.x, my_center.y
    logFile.write("\nTurn " + str(turn) + ". My center is: " + str(myX) + ", " + str(myY) + "\n")
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                aMove = createMove(location, myX, myY)
                logFile.write(moveToString(aMove))
                moves.append(aMove)
    sendFrame(moves)