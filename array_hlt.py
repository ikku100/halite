"""
A Python-based Halite starter-bot framework.

This module contains a Pythonic implementation of a Halite starter-bot framework.
In addition to a class (GameMap) containing all information about the game world
and some helper methods, the module also imeplements the functions necessary for
communicating with the Halite game environment.
"""

import sys
from collections import namedtuple
from itertools import chain, zip_longest
import numpy
import numpy as np
import time

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

Location = namedtuple('Location', 'x y')
Range = namedtuple('Range', "x1 y1 x2 y2")

# Because Python uses zero-based indexing, the cardinal directions have a different mapping in this Python starterbot
# framework than that used by the Halite game environment.  This simplifies code in several places.  To accommodate
# this difference, the translation to the indexing system used by the game environment is done automatically by
# the send_frame function when communicating with the Halite game environment.

NORTH, EAST, SOUTH, WEST, STILL = range(5)
# MOVES = (STILL, NORTH, EAST, SOUTH, WEST)
MOVES = (NORTH, EAST, SOUTH, WEST, STILL)
MOVES_STRINGS = ["NORTH", "EAST", "SOUTH", "WEST", "STILL"]


def opposite_cardinal(direction):
    "Returns the opposing cardinal direction."
    return (direction + 2) % 4 if direction != STILL else STILL


Square = namedtuple('Square', 'x y owner strength production')


Move = namedtuple('Move', 'square direction')
MoveSimple = namedtuple("MoveSimple", "location direction")

class GameMap:

    def __init__(self):
        pass

    @classmethod
    def make_gamemap_from_strings(cls, playerID, size_string, production_string, map_string=None):
        self = cls()
        self.playerID = playerID
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.logfile = open(str(playerID) + "array_hlt" + timestr + ".log", 'w')

        self.width, self.height = tuple(map(int, size_string.split()))

        # self.production = tuple(tuple(map(int, substring)) for substring in grouper(production_string.split(), self.width))
        self.get_frame(map_string)
        # o = []
        # for e in np.nditer(self.owners):
        #     o.append( e)
        # print(set(o))
        self.starting_player_count = len(np.unique(self.owners)) - 1

        # self.str = numpy.empty()
        self.prod = np.fromstring(production_string, dtype=int, sep=' ')
        self.prod = self.prod.reshape(self.height, self.width)
        self.log(self.prod)
        return self

    def __copy__(self):
        newone = type(self)()
        newone.playerID = self.playerID
        newone.logfile = self.logfile
        newone.width = self.width
        newone.height = self.height
        newone.prod = self.prod
        newone.owners = self.owners
        newone.strength = self.strength
        return newone

    def __deepcopy__(self, memo={}):
        result = self.__copy__()
        result.strength = self.strength.copy()
        result.owners = self.owners.copy()
        return result


    def log(self, obj):
        self.logfile.write(str(obj))

    def set_logfile(self, logfile):
        self.logfile = logfile

    def get_frame(self, map_string=None):
        "Updates the map information from the latest frame provided by the Halite game environment."
        if map_string is None:
            map_string = get_string()
        split_string = map_string.split()
        owners = list()
        while len(owners) < self.width * self.height:
            counter = int(split_string.pop(0))
            owner = int(split_string.pop(0))
            owners.extend([owner] * counter)
        assert len(owners) == self.width * self.height
        self.owners = np.array(owners, dtype=np.int16)
        self.owners = self.owners.reshape(self.height, self.width)
        self.owners = np.ndarray.swapaxes(self.owners, 0, 1)


        assert len(split_string) == self.width * self.height
        self.strength = np.array(split_string, dtype=np.int16)# fromstring(split_string, dtype=int, sep=' ')
        self.strength = self.strength.reshape(self.height, self.width)
        self.strength = np.ndarray.swapaxes(self.strength, 0, 1)

    def neighbors(self, x, y, n=1, include_self=False):
        "Iterable over the n-distance neighbors of a given square.  For single-step neighbors, the enumeration index provides the direction associated with the neighbor."
        assert isinstance(include_self, bool)
        assert isinstance(n, int) and n > 0
        if n == 1:
            combos = ((0, -1), (1, 0), (0, 1), (-1, 0), (0, 0))   # NORTH, EAST, SOUTH, WEST, STILL ... matches indices provided by enumerate(game_map.neighbors(square))
        else:
            combos = ((dx, dy) for dy in range(-n, n+1) for dx in range(-n, n+1) if abs(dx) + abs(dy) <= n)
        return (self.owners[(y + dy) % self.height][(x + dx) % self.width] for dx, dy in combos if include_self or dx or dy)

    def get_distance(self, sq1, sq2):
        "Returns Manhattan distance between two squares."
        dx = min(abs(sq1.x - sq2.x), sq1.x + self.width - sq2.x, sq2.x + self.width - sq1.x)
        dy = min(abs(sq1.y - sq2.y), sq1.y + self.height - sq2.y, sq2.y + self.height - sq1.y)
        return dx + dy

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
        result = "Owners:\n"
        result += np.array_str(self.owners)
        result += "\nStrength:\n"
        # for site in self.iterator():
        #     if site.owner is self.my_id:
        #         result += colors.OKGREEN + colors.UNDERLINE
        #     result += str(site.strength) + colors.ENDC + " "
        #     new_line_counter += 1
        #     if new_line_counter is self.width:
        #         result += '\n'
        #         new_line_counter = 0
        result += np.array_str(self.strength)
        result += "\nProduction:\n"
        result += np.array_str(self.prod)
        result += "\n"
        return result

    def my_total_strength(self):
        # sum = 0
        # for x, y in self.my_coordinates_list():
        #     sum += self.get_site(x, y).strength
        return sum(self.strength[self.owners == self.playerID])

    def my_total_production(self):
        # sum = 0
        # for x, y in self.my_coordinates_list():
        #     sum += self.get_site(x, y).production
        # return sum
        return sum(self.prod[self.owners == self.playerID])

    def get_new_coordinates(self, x, y, direction):
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

    def get_location(self, location, direction=STILL):
        if direction == STILL:
            return location
        x, y = self.get_new_coordinates(location.x, location.y, direction)
        return Location(x, y)

    def my_locations_list(self):
        my_locs_in_array = numpy.argwhere(self.owners == self.playerID)
        my_locs = list(map(tuple, my_locs_in_array))
        # for e in my_locs_in_array:

        return my_locs

    def evolve_assuming_no_enemy(self, moves_as_coordinates_direction_list):
        for location, direction in moves_as_coordinates_direction_list:
            x, y = location
            if direction is STILL:
                self.strength[y, x] += self.prod[y, x]
                continue
            new_x, new_y = self.get_new_coordinates(x, y, direction)
            if self.strength[y, x] < self.strength[new_y, new_x]:
                self.strength[new_y, new_x] -= self.strength[y, x]
            else:  # site gets overtaken!
                self.strength[new_y, new_x] = self.strength[y, x] - self.strength[new_y, new_x]
                self.owners[new_y, new_x] = self.playerID
                self.strength[y, x] = 0


#####################################################################################################################
# Functions for communicating with the Halite game environment (formerly contained in separate module networking.py #
#####################################################################################################################

def send_string(s):
    sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()


def get_string():
    return sys.stdin.readline().rstrip('\n')


def get_init():
    playerID = int(get_string())
    m = make_gamemap_from_strings(playerID, get_string(), get_string())
    return playerID, m


def send_init(name):
    send_string(name)


def translate_cardinal(direction):
    "Translate direction constants used by this Python-based bot framework to that used by the official Halite game environment."
    # Cardinal indexing used by this bot framework is
    # ~ NORTH = 0, EAST = 1, SOUTH = 2, WEST = 3, STILL = 4
    # Cardinal indexing used by official Halite game environment is
    # ~ STILL = 0, NORTH = 1, EAST = 2, SOUTH = 3, WEST = 4
    # ~ >>> list(map(lambda x: (x+1) % 5, range(5)))
    # ~ [1, 2, 3, 4, 0]
    return (direction + 1) % 5


def send_frame(moves):
    send_string(' '.join(str(move.square.x) + ' ' + str(move.square.y) + ' ' + str(translate_cardinal(move.direction))
                         for move in moves))
