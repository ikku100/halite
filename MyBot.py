import random
import time

import array_geographic_utils
import array_hlt
from array_hlt import NORTH, EAST, SOUTH, WEST, STILL, Move, Square
timestr = time.strftime("%Y%m%d-%H%M%S")

from os import path
bot_name = path.splitext(__file__)[0]
logFile = open(bot_name + "game" + timestr + ".log", 'w')


def get_init():
    i = 0
    first_string = array_hlt.get_string()
    playerID = int(first_string)
    logFile.write(first_string)
    logFile.write("gamemap is constructed with:\n" +  array_hlt.get_string() + "\nand\n" + array_hlt.get_string())
    logFile.write("and first frame part 0:\n" + array_hlt.get_string())
    logFile.write("and first frame part 1:\n" + array_hlt.get_string())


# get_init()
# logFile.close()
# raise ("stop maar")

myID, gamemap = array_hlt.get_init()
array_hlt.send_init(bot_name)
gamemap.set_logfile(logFile)

turn = 0
while True:
    turn += 1
    gamemap.get_frame()
    # gamemap.log("\nturn: " + str(turn) + '\n')
    dijkstra_map = array_geographic_utils.ScoringGeoMap(gamemap.width, gamemap.height)
    dijkstra_map.calculate_scores(gamemap=gamemap)
    moves = dijkstra_map.calculate_best_moves(gamemap)
    # gamemap.log(str(moves) + '\n')
    moves = dijkstra_map.post_process_moves(gamemap, moves)
    # gamemap.log(str(moves) + '\n')
    array_hlt.send_moves(moves)
