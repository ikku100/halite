# Goes in MyBot.py

from hlt import *
from networking import *
import time
timestr = time.strftime("%Y%m%d-%H%M%S")

myID, gameMap = getInit()
from os import path
botName = path.splitext(__file__)[0]

sendInit(botName)
logFile = open(botName + "game" + timestr + ".log", 'w')


def getMoveAwayFromCenter(location, myX, myY):
    dX = myX - location.x 
    if dX < -1 * gameMap.width:
        dX += gameMap.width
    dY = myY - location.y
    if dY < -1 * gameMap.height:
        dY += gameMap.height

    if abs(dY) > abs(dX):
        return NORTH if dY > 0 else SOUTH
    else:
        return EAST if dX > 0 else WEST

        
def move(location, myX, myY):
    site = gameMap.getSite(location)
    for d in CARDINALS:
        neighbour_site = gameMap.getSite(location, d)
        if neighbour_site.owner != myID and neighbour_site.strength < site.strength:
            return Move(location, d)
    if site.strength < site.production * 5:
        return Move(location, STILL)
    
    moveAwayFromCenter = getMoveAwayFromCenter(location, myX, myY)
    targetSite = gameMap.getSite(location, moveAwayFromCenter)
    if targetSite.strength < site.strength:
        return Move(location, moveAwayFromCenter)
    return Move(location, STILL)


def myCenter():
    # find center by adding up sum of strenght of x and y separately
    sumX = 0
    sumY = 0
    count = 0
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            site = gameMap.getSite(location)
            if gameMap.getSite(location).owner == myID:
                count += 1
                logFile.write(str(x) + "," + str(y) + ", += " + str(location.x + gameMap.width ) + ", " + str(location.y + gameMap.height) + "\n")
                sumX += location.x + gameMap.width #site.strength
                sumY += location.y + gameMap.height # site.strength
    return sumX/count - gameMap.width, sumY/count - gameMap.height

while True:
    moves = []
    gameMap = getFrame()
    myX, myY = myCenter()
    logFile.write("my center is: " + str(myX) + ", " + str(myY) + "\n")
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                moves.append(move(location, myX, myY))
    sendFrame(moves)