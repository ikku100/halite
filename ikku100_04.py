import random
import time

import array_hlt
from array_hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
timestr = time.strftime("%Y%m%d-%H%M%S")

from os import path
bot_name = path.splitext(__file__)[0]
logFile = open(bot_name + "game" + timestr + ".log", 'w')


myID, game_map = array_hlt.get_init()
array_hlt.send_init(bot_name)


while True:
    game_map.get_frame()
    moves = [Move(square, random.choice((NORTH, EAST, SOUTH, WEST, STILL))) for square in game_map if square.owner == myID]
    array_hlt.send_frame(moves)


def never():
    from geographic_utils import moveToString, createMove, myCenter, find_optimal_moves


    turn = 0
    while True:
        turn += 1
        moves = []
        gameMap = getFrame()
        my_center = myCenter(gameMap, myID)
        myX, myY = my_center.x, my_center.y
        logFile.write("\nTurn " + str(turn) + ". My center is: " + str(myX) + ", " + str(myY) + "\n")
        for y in range(gameMap.height):
            for x in range(gameMap.width):
                location = Location(x, y)
                if gameMap.getSite(location).owner == myID:
                    aMove = createMove(gameMap, location, gameMap.getSite(location), myX, myY)
                    logFile.write(moveToString(aMove))
                    moves.append(aMove)
        sendFrame(moves)