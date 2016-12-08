import copy
import itertools
import math
import time

from hlt import NORTH, SOUTH, WEST, EAST, Move, STILL, Location, GameMap, MOVES, MOVES_STRINGS

# from ikku100_02 import gameMap, myID

timestr = time.strftime("%Y%m%d-%H%M%S")
logFile = open("geographic_utils_" + timestr + ".log", 'w')

def moveToString(move):
    return str(move.loc) + MOVES_STRINGS[move.direction]


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


def createMove(gameMap, location, site, myX, myY):
    logFile.write("\nmove (" + str(location.x) + ", " + str(location.y) + ").\t")
    logFile.write(xYToString(*distanceToCenter(location, myX, myY)))
    logFile.write("moveAwayFromCenterUsingDistance:" + MOVES_STRINGS[moveAwayFromCenterUsingDistance(location, myX, myY, *distanceToCenter(location, myX, myY))])
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


def myCenter(gameMap, myID):
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
            distanceSum = calculate_distance_sum(myID, newCenter)
            if distanceSum < minDistanceSum:
                bestCenter = newCenter
    return bestCenter


def calculate_distance_sum(gameMap, myID, newCenter):
    distance_sum = 0
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                # logFile.write(str(x) + "," + str(y) + ", += " + str(location.x + gameMap.width ) +
                # ", " + str(location.y + gameMap.height) + "\n")
                distance_sum += gameMap.getDistance(location, newCenter)
    return distance_sum


def every_site_i_own():
    return ['a', 'b']


def get_all_moves_for_n_locations(n):
    return itertools.product(MOVES, repeat=n)


def create_all_next_moves(all_my_sites):
    # return zip(itertools.repeat(all_my_sites), get_all_moves_for_n_locations(sum(1 for x in all_my_sites)))
    # return map(Move, zip(itertools.repeat(all_my_sites), get_all_moves_for_n_locations(sum(1 for x in all_my_sites))))
    all_my_sites = list(all_my_sites)  # I'm going to reuse all_my_sites so either need to recreate the generator
    # (not an option here) or get its contents
    moves_sets = []
    for moves in get_all_moves_for_n_locations(sum(1 for x in all_my_sites)):
        new_moves = []
        for site, move in zip(all_my_sites, moves):
            new_moves.append((site, move))
        moves_sets.append(new_moves)
    return moves_sets
    # return map(Move, zip(itertools.repeat(all_my_sites), get_all_moves_for_n_locations(sum(1 for x in all_my_sites))))



def find_optimal_moves_for_this_turn(start_game_map: GameMap):
    """' Returns the pair best_moves, score. best_moves is a tuple of ((x,y), direction) pairs"""
    max_score = 0
    best_moves = None
    # for moves in create_all_next_moves(start_game_map.my_sites()):
    for moves in create_all_next_moves(start_game_map.my_coordinates_list()):
        game_map = start_game_map.__deepcopy__()
        # print(game_map)
        game_map.evolve_assuming_no_enemy(moves)
        # print(game_map)
        score = game_map.my_total_production() + game_map.my_total_strength() * 0.5
        if score > max_score:
            # print("found something better in end state:")
            # print(game_map)
            best_moves = moves
            max_score = score
    return [best_moves], max_score


def find_optimal_moves(start_game_map, n_steps):
    if n_steps == 1:
        return find_optimal_moves_for_this_turn(start_game_map)
    max_score = 0
    best_moves = None
    for moves in create_all_next_moves(start_game_map.my_coordinates_list()):
        game_map = start_game_map.__deepcopy__()#copy.deepcopy(start_game_map)
        # game_map = copy.deepcopy(start_game_map)
        # print(game_map)
        game_map.evolve_assuming_no_enemy(moves)
        # print(game_map)
        future_moves_per_turn, end_score = find_optimal_moves(game_map, n_steps - 1)
        if end_score > max_score:
            max_score = end_score
            best_moves = [moves] + future_moves_per_turn
    return best_moves, max_score


def moves_multiple_turns_to_string(moves_per_turn):
    result = ""
    for turn in moves_per_turn:
        for move in turn:
            result += str(move) + ", "
        result += '\n'
    return result


def play_my_moves(game_map, moves_per_turn):
    turn = 0
    print ("Turn " + str(turn))
    print(game_map)
    for moves in moves_per_turn:
        turn += 1
        game_map.evolve_assuming_no_enemy(moves)
        print("Turn " + str(turn))
        print(game_map)