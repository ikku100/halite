import random
import math
import copy
from enum import Enum

#
# To find optimal opening moves, just scan the state space till I run out of time? Or at least figure out how many
# moves deep I can calculate, as a function of grid size. Maybe make it easier by choosing sub grid (up to where
# opponent is)
#
# To do this, I need to branch into each potential set of moves, and update the game map! I guess this is why Thomas
# used deep copy
#

STILL = 0
NORTH = 1
EAST = 2
SOUTH = 3
WEST = 4

MOVES = (STILL, NORTH, SOUTH, WEST, EAST)
MOVES_STRINGS = ["STILL", "NORTH", "EAST", "SOUTH", "WEST"]

DIRECTIONS = [a for a in range(0, 5)]
CARDINALS = [a for a in range(1, 5)]

ATTACK = 0
STOP_ATTACK = 1

class Range:
    def __init__(self, x0, y0, x1, y1):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1


def make_range(x1, y1):
    return Range(0, 0, x1, y1)


class Location:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        # for k, v in self.__dict__.items():
        #     setattr(result, k, deepcopy(v, memo))
        result.x = self.x
        result.y = self.y
        return result

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class SiteValueTypes(Enum):
    owner = 0,
    strength = 1,
    production = 2

class Site:
    def __init__(self, owner=0, strength=0, production=0):
        self.owner = owner
        self.strength = strength
        self.production = production


class Move:
    def __init__(self, loc=0, direction=0):
        self.loc = loc
        self.direction = direction

    def __str__(self):
        return str(self.loc) + ": " + MOVES_STRINGS[self.direction]

    def __eq__(self, other):
        return self.loc == other.loc and self.direction == other.direction


class GameMap:
    def __init__(self, width = 0, height = 0, numberOfPlayers = 0):
        self.width = width
        self.height = height
        self.contents = []
        self.my_id = ""

        for y in range(0, self.height):
            row = []
            for x in range(0, self.width):
                row.append(Site(0, 0, 0))
            self.contents.append(row)

    def set_my_id(self, id):
        self.my_id = id

    def inBounds(self, l):
        return l.x >= 0 and l.x < self.width and l.y >= 0 and l.y < self.height

    def getDistance(self, l1, l2):
        dx = abs(l1.x - l2.x)
        dy = abs(l1.y - l2.y)
        if dx > self.width / 2:
            dx = self.width - dx
        if dy > self.height / 2:
            dy = self.height - dy
        return dx + dy

    def getAngle(self, l1, l2):
        dx = l2.x - l1.x
        dy = l2.y - l1.y

        if dx > self.width - dx:
            dx -= self.width
        elif -dx > self.width + dx:
            dx += self.width

        if dy > self.height - dy:
            dy -= self.height
        elif -dy > self.height + dy:
            dy += self.height
        return math.atan2(dy, dx)

    def getLocation(self, loc, direction):
        l = copy.deepcopy(loc)
        if direction != STILL:
            if direction == NORTH:
                if l.y == 0:
                    l.y = self.height - 1
                else:
                    l.y -= 1
            elif direction == EAST:
                if l.x == self.width - 1:
                    l.x = 0
                else:
                    l.x += 1
            elif direction == SOUTH:
                if l.y == self.height - 1:
                    l.y = 0
                else:
                    l.y += 1
            elif direction == WEST:
                if l.x == 0:
                    l.x = self.width - 1
                else:
                    l.x -= 1
        return l

    def getCoords(self, x, y, direction):
        if direction != STILL:
            if direction == NORTH:
                if y == 0:
                    y = self.height - 1
                else:
                    y -= 1
            elif direction == EAST:
                if x == self.width - 1:
                    x = 0
                else:
                    x += 1
            elif direction == SOUTH:
                if y == self.height - 1:
                    y = 0
                else:
                    y += 1
            elif direction == WEST:
                if x == 0:
                    x = self.width - 1
                else:
                    x -= 1
        return x, y

    def getLocationFewerCopies(self, loc, direction):
        if direction != STILL:
            l = copy.deepcopy(loc)
            if direction == NORTH:
                if l.y == 0:
                    l.y = self.height - 1
                else:
                    l.y -= 1
            elif direction == EAST:
                if l.x == self.width - 1:
                    l.x = 0
                else:
                    l.x += 1
            elif direction == SOUTH:
                if l.y == self.height - 1:
                    l.y = 0
                else:
                    l.y += 1
            elif direction == WEST:
                if l.x == 0:
                    l.x = self.width - 1
                else:
                    l.x -= 1
        return loc

    def getSite(self, l, direction = STILL):
        if direction == STILL:
            return self.contents[l.y][l.x]
        l = self.getLocation(l, direction)
        return self.contents[l.y][l.x]

    # todo cache this function! (does that even work with yield?)
    # @cache
    def players_sites(self, id):
        for y in range(self.height):
            for x in range(self.width):
                if self.contents[y][x].owner == id:
                    yield Location(x, y)

    def my_sites(self):
        return self.players_sites(self.my_id)

    def my_number_of_sites(self):
        return sum(1 for x in self.my_sites())

    def evolve_assuming_no_enemy(self, moves):
        for move in moves:
            if move.direction is STILL:
                self.getSite(move.loc).strength += self.getSite(move.loc).production
                continue
            target_site = self.getSite(move.loc, move.direction)
            if self.getSite(move.loc).strength < target_site.strength:
                target_site.strength -= self.getSite(move.loc).strength
            else: # site gets overtaken!
                target_site.strength = self.getSite(move.loc).strength - target_site.strength
                target_site.owner = self.my_id
                self.getSite(move.loc).strength = 0

    def change_portion_of_map(self, change_type: SiteValueTypes, value, ranghe: Range):
        for x in range(ranghe.x0, ranghe.x1 + 1):
            for y in range(ranghe.y0, ranghe.y1 + 1):
                if change_type is SiteValueTypes.strength:
                    self.contents[y][x].strength = value
                elif change_type is SiteValueTypes.production:
                    self.contents[y][x].production = value
                else:
                    self.contents[y][x].owner = value

    def iterator(self):
        for y in range(self.height):
            for x in range(self.width):
                yield self.contents[y][x]



    def __str__(self):
        class colors:
            HEADER = '\033[95m'
            OKBLUE = '\033[94m'
            OKGREEN = '\033[92m'
            WARNING = '\033[93m'
            FAIL = '\033[91m'
            ENDC = '\033[0m'
            BOLD = '\033[1m'
            UNDERLINE = '\033[4m'

        new_line_counter = 0
        result = "Strength:\n"
        for site in self.iterator():
            if site.owner is self.my_id:
                result += colors.OKGREEN + colors.UNDERLINE
            result += str(site.strength) + colors.ENDC + " "
            new_line_counter += 1
            if new_line_counter is self.width:
                result += '\n'
                new_line_counter = 0
        result += "Production:\n"
        for site in self.iterator():
            if site.owner is self.my_id:
                result += colors.OKGREEN + colors.UNDERLINE
            result += str(site.production) + colors.ENDC + " "
            new_line_counter += 1
            if new_line_counter is self.width:
                result += '\n'
                new_line_counter = 0
        return result

    def my_total_strength(self):
        sum = 0
        for site in self.my_sites():
            sum += self.getSite(site).strength
        return sum

    def my_total_production(self):
        sum = 0
        for site in self.my_sites():
            sum += self.getSite(site).production
        return sum
        # return sum(self.getSite(next(self.my_sites(), None)).production)

