import time
from networking import *

myID, gameMap = getInit()
from os import path
botName = path.splitext(__file__)[0]
sendInit(botName)

MOVES = ["STILL","NORTH","EAST","SOUTH","WEST"]
timestr = time.strftime("%Y%m%d-%H%M%S")
logFile = open("geographic_utils_" + timestr + ".log", 'w')

def moveToString(move):
    return move.loc.toString() + MOVES[move.direction]


def xYToString(x, y):
    return "(" + str(x) + ", " + str(y) + ")"


def getMoveAwayFromCenter(location, myX, myY):
    dX = myX - location.x
    dXInv = location.x - myX
    useDXInverted = False if abs(dXInv) < abs(dX) else True
    # if dX < -1 * gameMap.width:
    #     dX += gameMap.width

    dY = myY - location.y
    dYInv = myY - location.y
    useDYInverted = False if abs(dYInv) < abs(dY) else True
    # if dY < -1 * gameMap.height:
    #     dY += gameMap.height

    if abs(dY) > abs(dX):
        if useDYInverted:
            return NORTH if dY > 0 else SOUTH
        else:
            return SOUTH if dY > 0 else NORTH
    else:
        if useDXInverted:
            return WEST if dX > 0 else EAST
        else:
            return EAST if dX > 0 else WEST


def moveAwayFromCenterUsingDistance(location, myX, myY, dX, dY):
    if abs(dY) > abs(dX):
        return SOUTH if dY > 0 else NORTH
    else:
        return EAST if dX > 0 else WEST


def createMove(location, myX, myY):
    logFile.write("\nmove (" + str(location.x) + ", " + str(location.y) + ").\t")
    logFile.write(xYToString(*distanceToCenter(location, myX, myY)))
    logFile.write("moveAwayFromCenterUsingDistance:" + MOVES[moveAwayFromCenterUsingDistance(location, myX, myY, *distanceToCenter(location, myX, myY))])
    site = gameMap.getSite(location)
    # for d in CARDINALS:
    #     neighbour_site = gameMap.getSite(location, d)
    #     if neighbour_site.owner != myID and neighbour_site.strength < site.strength:
    #         return Move(location, d)
    if site.strength < site.production * 5:
        return Move(location, STILL)

    # moveAwayFromCenter = getMoveAwayFromCenter(location, myX, myY)
    moveAwayFromCenter = moveAwayFromCenterUsingDistance(location, myX, myY, *distanceToCenter(location, myX, myY))
    targetSite = gameMap.getSite(location, moveAwayFromCenter)
    if targetSite.strength < site.strength:
        return Move(location, moveAwayFromCenter)
    return Move(location, STILL)


def distanceToCenter(location, myX, myY):
    dX = myX - location.x
    dXInv = location.x - myX
    realDX = dX if abs(dXInv) < abs(dX) else dXInv
    dY = myY - location.y
    dYInv = myY - location.y
    realDY = dY if abs(dYInv) < abs(dY) else dYInv
    return realDX, realDY


def distance(a, b):
    return math.sqrt((a.y - b.y) * (a.y - b.y) + (a.x - b.x) * (a.x - b.x))


def myCenter():
    # find center by adding up sum of strenght of x and y separately
    sumX = 0
    sumY = 0
    count = 0
    minDistanceSum = 999999999999999999999999999999999999
    for yC in range(gameMap.height):
        for xC in range(gameMap.width):
            newCenter = Location(xC, yC)
            if gameMap.getSite(newCenter).owner != myID:
                continue
            distanceSum = calculate_distance_sum(newCenter)
            if distanceSum < minDistanceSum:
                bestCenter = newCenter
    return bestCenter


def calculate_distance_sum(newCenter):
    distance_sum = 0
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                # logFile.write(str(x) + "," + str(y) + ", += " + str(location.x + gameMap.width ) + ", " + str(location.y + gameMap.height) + "\n")
                distance_sum += gameMap.getDistance(location, newCenter)
    return distance_sum


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