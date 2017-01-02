import itertools
import math
import time
import numpy as np
from array_hlt import NORTH, SOUTH, WEST, EAST, Move, STILL, Location, GameMap, MOVES, MOVES_STRINGS
from enum import IntEnum

MAX_SMALL_INT = np.iinfo(np.int16).max
timestr = time.strftime("%Y%m%d-%H%M%S")
# logFile = open("geographic_utils_" + timestr + ".log", 'w')


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
    # logFile.write("\nmove (" + str(location.x) + ", " + str(location.y) + ").\t")
    # logFile.write(xYToString(*distanceToCenter(location, myX, myY)))
    # logFile.write("moveAwayFromCenterUsingDistance:" + MOVES_STRINGS[moveAwayFromCenterUsingDistance(location, myX, myY, *distanceToCenter(location, myX, myY))])
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
            distanceSum = calculate_distance_sum(gameMap, myID, newCenter)
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
    # all_my_sites = list(all_my_sites)  # I'm going to reuse all_my_sites so either need to recreate the generator
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
    for moves in create_all_next_moves(start_game_map.my_locations_list()):
        game_map = start_game_map.__deepcopy__()
        # print(game_map)
        game_map.evolve_assuming_no_enemy(moves)
        # print(game_map)
        score = game_map.my_total_production() + game_map.my_total_strength() * 0.5
        if score > max_score:
            best_moves = moves
            max_score = score
    return [best_moves], max_score


def find_optimal_moves(start_game_map, n_steps):
    if n_steps == 1:
        return find_optimal_moves_for_this_turn(start_game_map)
    max_score = 0
    best_moves = None
    for moves in create_all_next_moves(start_game_map.my_locations_list()):
        game_map = start_game_map.__deepcopy__()  # copy.deepcopy(start_game_map)
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


def nearest_empty_fields(gamemap):
    res = set()
    my_locations = gamemap.my_locations_list()
    for my_field in my_locations:
        neighbours = gamemap.neighbours(my_field.x, my_field.y, n=1)
        for neighbour in neighbours:
            if neighbour not in my_locations:
                res.add(neighbour)
    return res


class ScoringGeoMap:
    class Status(IntEnum):
        INNER_TERRITORY = 0
        MY_BOUNDARY = 1
        NEW_BOUNDARY = 2
        OLD_BOUNDARY = 3
        DONE = 4
        UNKNOWN = 999

    def __init__(self, width, height):
        self.prod_to_str_ratio = 5
        self.score = np.zeros((height, width), dtype=np.int16)
        self.step_distances = np.full((height, width), MAX_SMALL_INT, dtype=np.int16)
        # self.square_stati = np.full((height, width), "unknown", dtype=np.dtype(np.str_, 8))
        self.square_stati = np.full((height, width), self.Status.UNKNOWN, dtype=np.int16)

    def mark_borders_and_get_potential_territory(self, gamemap: GameMap):
        grow_from_to_squares = []
        for square in gamemap.my_locations_list():
            # for neighbour in gamemap.neighbours(square[0], square[1]):
            for move in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                # [(y + dy) % self.height][(x + dx) % self.width]
                neighbour = ((square[0] + move[0]) % gamemap.height, (square[1] + move[1]) % gamemap.width)
                if not gamemap.is_mine(neighbour):
                    grow_from_to_squares.append((square, neighbour))
                    self.step_distances[square] = 0
                    self.square_stati[square] = self.Status.MY_BOUNDARY
                    self.square_stati[neighbour] = self.Status.NEW_BOUNDARY
        return grow_from_to_squares

    def get_next_potential_neighbours(self, gamemap: GameMap):
        self.square_stati[self.square_stati == self.Status.OLD_BOUNDARY] = self.Status.DONE
        self.square_stati[self.square_stati == self.Status.NEW_BOUNDARY] = self.Status.OLD_BOUNDARY
        grow_from_to_squares = []
        for square in np.argwhere(self.square_stati == self.Status.OLD_BOUNDARY):
            for move in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                neighbour = ((square[0] + move[0]) % gamemap.height, (square[1] + move[1]) % gamemap.width)
                if not gamemap.is_mine(neighbour) and \
                        (self.square_stati[neighbour] == self.Status.UNKNOWN
                         or self.square_stati[neighbour] == self.Status.NEW_BOUNDARY):
                    grow_from_to_squares.append((tuple(square), neighbour))
                    self.square_stati[neighbour] = self.Status.NEW_BOUNDARY
        return grow_from_to_squares

    def calculate_scores(self, gamemap: GameMap, cost_moving=1):
        """"First round give all squares a score based on nearest neighbour.
            Second round update all squares with best score of next nearest neighbour
            Do this a couple of times?
        """
        self.step_distances[gamemap.owners == gamemap.playerID] = 9999
        grow_from_to_squares = self.mark_borders_and_get_potential_territory(gamemap)
        while len(grow_from_to_squares) > 0:
            for from_to_sq in grow_from_to_squares:
                from_sq, to_sq = from_to_sq
                self.step_distances[to_sq] = min(self.step_distances[from_sq] + 1, self.step_distances[to_sq])
                self.score[from_sq] += self.prod_to_str_ratio * gamemap.prod[to_sq] - gamemap.strength[to_sq]
                self.square_stati[to_sq] = self.Status.NEW_BOUNDARY
                self.square_stati[from_sq] = self.Status.DONE
            grow_from_to_squares = self.get_next_potential_neighbours(gamemap)

        self.update_step_distances_inside(gamemap)
        # Now get the best scores going from outside to inside
        self.update_scores_from_out_to_inside(gamemap)

    def update_scores_from_out_to_inside(self, gamemap: GameMap):
        max_distance = np.amax(self.step_distances)
        max_distance = gamemap.fog_of_war_distance()
        min_distance = np.amin(self.step_distances)
        for distance in range (max_distance - 1, min_distance - 1, -1): # skip first outer layer as that doesn't have a NEXT nearest n.
            # from_squares = np.argwhere(self.step_distances == distance)
            from_squares = np.where(self.step_distances == distance)
            for square in zip(*from_squares):
                optimal_score = -9999
                for move in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    neighbour = ((square[0] + move[0]) % gamemap.height, (square[1] + move[1]) % gamemap.width)
                    if self.step_distances[neighbour] == distance + 1:
                        if self.score[neighbour] > optimal_score:
                            optimal_score = self.score[neighbour]
                # do inner area differently, we don't want everything to move inwards!
                if distance < 0:
                    self.score[square] += np.int16(optimal_score) - 1
                else:
                    self.score[square] += np.int16(0.5 * optimal_score)

    def calculate_best_moves(self, gamemap: GameMap):
        moves = []
        my_total_str = gamemap.my_total_strength()
        my_locations_list = gamemap.my_locations_list()
        num_my_location = len(my_locations_list)
        for square in my_locations_list:
            my_str = gamemap.strength[square]
            best_move = STILL
            optimal_score = -9999
            for step, move in zip([(0, -1), (1, 0), (0, 1), (-1, 0)], [WEST, SOUTH, EAST, NORTH]):
                neighbour = ((square[0] + step[0]) % gamemap.height, (square[1] + step[1]) % gamemap.width)
                # do inner area differently, but only if strength is less than half the max (if bigger, just gogo!)
                # also check for insignificance str of this square (compare it to average str)
                if self.step_distances[square] < 0 and my_str < 256/2 and my_str < my_total_str / my_locations_list:
                    pass # for now just don't do anything
                elif self.score[neighbour] > optimal_score and my_str >= gamemap.strength[neighbour]:
                    # only move if target has better score or target isn't mine
                    if gamemap.owners[neighbour] != gamemap.playerID or self.score[square] < self.score[neighbour]:
                        optimal_score = self.score[neighbour]
                        best_move = move
                        gamemap.log("updating best move to score " +
                                    str(optimal_score) + ", move: " + MOVES_STRINGS[move] + '\n')
            moves.append((square, best_move))
        return moves

    def post_process_moves(self, gamemap, moves):
        # find if its useful at all to move:
        # if the target site has more str than my total str, don't bother
        # what's the target site??
        minimum_target_str = min(gamemap.strength[self.step_distances == 1])
        gamemap.log("minimum_target_str = " + str(minimum_target_str) + '\n')
        if minimum_target_str < gamemap.my_total_strength():
            return moves
        else:
            return [(location, STILL) for location, move in moves]

    def update_step_distances_inside(self, gamemap):
        my_boundary = np.where(self.step_distances == 0)
        step_distance = 0
        while len(my_boundary) > 0 and len(my_boundary[0]) > 0:
            step_distance -= 1
            for square in zip(*my_boundary):
                for move in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                    neighbour = ((square[0] + move[0]) % gamemap.height, (square[1] + move[1]) % gamemap.width)
                    if self.square_stati[neighbour] == self.Status.UNKNOWN:
                        self.square_stati[neighbour] = self.Status.INNER_TERRITORY
                        self.step_distances[neighbour] = step_distance
            my_boundary = np.where(self.step_distances == step_distance)


def play_my_moves(game_map, moves_per_turn):
    turn = 0
    print("Turn " + str(turn))
    print(game_map)
    for moves in moves_per_turn:
        turn += 1
        game_map.evolve_assuming_no_enemy(moves)
        print("Turn " + str(turn))
        print("Moves: " + str(moves))
        print(game_map)
