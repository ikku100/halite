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


def opposite_cardinal(direction):
    "Returns the opposing cardinal direction."
    return (direction + 2) % 4 if direction != STILL else STILL


Square = namedtuple('Square', 'x y owner strength production')


Move = namedtuple('Move', 'square direction')


class GameMap:
    def __init__(self, playerID, size_string, production_string, map_string=None):
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

        assert len(split_string) == self.width * self.height
        self.strength = np.array(split_string, dtype=np.int16)# fromstring(split_string, dtype=int, sep=' ')
        self.strength = self.strength.reshape(self.height, self.width)

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
    m = GameMap(playerID, get_string(), get_string())
    return playerID, m


def send_init(name):
    send_string(name)


def translate_cardinal(direction):
    "Translate direction constants used by this Python-based bot framework to that used by the official Halite game environment."
    # Cardinal indexing used by this bot framework is
    #~ NORTH = 0, EAST = 1, SOUTH = 2, WEST = 3, STILL = 4
    # Cardinal indexing used by official Halite game environment is
    #~ STILL = 0, NORTH = 1, EAST = 2, SOUTH = 3, WEST = 4
    #~ >>> list(map(lambda x: (x+1) % 5, range(5)))
    #~ [1, 2, 3, 4, 0]
    return (direction + 1) % 5


def send_frame(moves):
    send_string(' '.join(str(move.square.x) + ' ' + str(move.square.y) + ' ' + str(translate_cardinal(move.direction)) for move in moves))
