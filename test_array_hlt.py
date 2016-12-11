# import timeit
import unittest
# from datetime import datetime
# from unittest.mock import Mock

import array_hlt
# import yappi
# import sys


class TestArrayHlt(unittest.TestCase):

    def setUp(self):
        pass

    def test_gamemap_construction(self):
        id = 1337
        size_string = "10 10 "
        gamemap_production_str = "8 8 3 2 6 14 8 6 3 4 7 7 2 2 7 10 4 2 3 7 8 6 3 4 8 8 3 2 6 14 4 2 3 7 7 7 2 2 7 10 3 2 6 14 8 6 3 4 8 8 2 2 7 10 4 2 3 7 7 7 3 4 8 8 3 2 6 14 8 6 3 7 7 7 2 2 7 10 4 2 6 14 8 6 3 4 8 8 3 2 7 10 4 2 3 7 7 7 2 2 "
        first_frame = "15 0 1 1 15 0 1 2 25 0 1 3 15 0 1 4 25 0 1 5 97 96 95 97 82 106 176 112 107 80 79 80 95 77 73 96 168 121 114 98 82 106 176 112 107 80 97 96 95 97 73 96 168 121 114 98 79 80 95 77 107 80 97 96 95 97 82 106 176 112 114 98 79 80 95 77 73 96 168 121 95 97 82 106 176 112 107 80 97 96 95 77 73 96 168 121 114 98 79 80 176 112 107 80 97 96 95 97 82 106 168 121 114 98 79 80 95 77 73 96 "
        # print(list(map(int, row)) for row in array_hlt.grouper(gamemap_production_str.split(), 10))

        m = array_hlt.GameMap(id, size_string, gamemap_production_str, first_frame)
        self.assertEquals(1,2)

# if __name__ == '__main__':
#     unittest.main()

