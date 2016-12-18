# import timeit
import unittest
# from datetime import datetime
# from unittest.mock import Mock

import array_hlt
from array_hlt import Location as Location, MoveSimple as MoveSimple
import array_geographic_utils
# import yappi
# import sys
import numpy as np

class TestArrayHlt(unittest.TestCase):

    def setUp(self):
        self.start_gamemap = array_hlt.GameMap.make_gamemap_from_strings(1337, "5 5",
                                                                 "1 1 1 2 2 1 1 1 2 2 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1",
                                                                 "12 0 1 1337 12 0 " + "1 1 1 1 1 1 1 1 1 1 1 1 2 1 1 1 1 1 1 1 1 1 1 1 1")

    def test_gamemap_construction(self):
        id = 1337
        size_string = "10 10 "
        gamemap_production_str = "8 8 3 2 6 14 8 6 3 4 7 7 2 2 7 10 4 2 3 7 8 6 3 4 8 8 3 2 6 14 4 2 3 7 7 7 2 2 7 10 3 2 6 14 8 6 3 4 8 8 2 2 7 10 4 2 3 7 7 7 3 4 8 8 3 2 6 14 8 6 3 7 7 7 2 2 7 10 4 2 6 14 8 6 3 4 8 8 3 2 7 10 4 2 3 7 7 7 2 2 "
        first_frame = "15 0 1 1 15 0 1 2 25 0 1 3 15 0 1 4 25 0 1 5 97 96 95 97 82 106 176 112 107 80 79 80 95 77 73 96 168 121 114 98 82 106 176 112 107 80 97 96 95 97 73 96 168 121 114 98 79 80 95 77 107 80 97 96 95 97 82 106 176 112 114 98 79 80 95 77 73 96 168 121 95 97 82 106 176 112 107 80 97 96 95 77 73 96 168 121 114 98 79 80 176 112 107 80 97 96 95 97 82 106 168 121 114 98 79 80 95 77 73 96 "
        # print(list(map(int, row)) for row in array_hlt.grouper(gamemap_production_str.split(), 10))

        m = array_hlt.GameMap.make_gamemap_from_strings(id, size_string, gamemap_production_str, first_frame)
        # self.assertEquals(1,2)

    def test_totals(self):
        # print(str(self.start_gamemap))
        self.assertEquals(self.start_gamemap.my_total_strength(), 2)
        self.assertEquals(self.start_gamemap.my_total_production(), 1)

    def test_evolve_no_enemies(self):
        moves = [MoveSimple(Location(2,2), array_hlt.NORTH)]
        self.start_gamemap.evolve_assuming_no_enemy(moves)
        self.assertEquals(self.start_gamemap.my_locations_list(), [(1, 2), (2, 2)])
        # print(str(self.start_gamemap))

    def test_my_locations_list(self):
        self.assertEquals(self.start_gamemap.my_locations_list(), [(2, 2)])
        self.start_gamemap.owners[1,2] = self.start_gamemap.playerID
        # print(self.start_gamemap)
        self.assertEquals(self.start_gamemap.my_locations_list(), [(1, 2), (2, 2)])

    def test_create_all_next_moves(self):
        # geographic_utils.every_site_i_own = Mock(return_value=['a', 'b'])
        # geographic_utils.every_site_i_own.
        # print (str(list(geographic_utils.create_all_next_moves())))
        self.assertEquals(len(list(array_geographic_utils.create_all_next_moves((s for s in ['a', 'b'])))), 25)

    def test_create_step_tree_depth_1(self):
        optimal_moves, best_score = array_geographic_utils.find_optimal_moves(self.start_gamemap, 1)
        self.assertEquals(best_score, 2.5)

    def test_create_step_tree_depth_2(self):
        optimal_moves, best_score = array_geographic_utils.find_optimal_moves(self.start_gamemap, 2)
        array_geographic_utils.play_my_moves(self.start_gamemap, optimal_moves)
        self.assertEquals(best_score, 4.5)
        self.assertEquals(optimal_moves, [[((2, 2), 1)], [((2, 1), 2), ((2, 2), 0)]])
        # print(geographic_utils.moves_multiple_turns_to_string(optimal_moves))
        # print(best_score)

    #     def test_create_step_tree_depth_3(self):
    #         optimal_moves, best_score = geographic_utils.find_optimal_moves(self.start_gamemap, 3)
    #         # print(*map(str, optimal_moves), best_score)
    #         # i have to write equals operators for Move and Location...
    #         self.assertEquals(best_score, 6.5)
    #         self.assertEquals(optimal_moves,  [[((2, 2), 1)], [((2, 1), 2), ((2, 2), 0)], [((2, 1), 0), ((3, 1), 0), ((2, 2), 0)]])
    #         print(geographic_utils.moves_multiple_turns_to_string(optimal_moves))
    #         print(best_score)
    #         geographic_utils.play_my_moves(self.start_gamemap, optimal_moves)
    #
    #
    #     def measure_speed_optimal_solution(self, n):
    #         start = datetime.now()
    #         geographic_utils.find_optimal_moves(self.start_gamemap, n)
    #         end = datetime.now()
    #         return str(end - start)
    #
    #     def test_speed_search(self):
    #         for n in range(1,4):
    #             yappi.start()
    #             print("Time needed for " + str(n) + ": " + self.measure_speed_optimal_solution(n))
    #             yappi.stop()
    #             yappi.get_func_stats().print_all(columns= {0:("name",60), 1:("ncall", 8),
    #                     2:("tsub", 8), 3: ("ttot", 8), 4:("tavg",8)})
    #             # yappi.get_thread_stats().print_all()
    #             yappi.clear_stats()
    #         # print("time for 2: ", timeit.timeit(geographic_utils.find_optimal_moves(self.start_gamemap, 2)))
    #         # print("time for 3: ", timeit.timeit(geographic_utils.find_optimal_moves(self.start_gamemap, 3)))
    #
    #     def dont_test_create_many_steps(self):
    #         optimal_moves, best_score = geographic_utils.find_optimal_moves(self.start_gamemap, 5)
    #         print(geographic_utils.moves_multiple_turns_to_string(optimal_moves))
    #         print(best_score)
    #         geographic_utils.play_my_moves(self.start_gamemap, optimal_moves)


    def dont_test_numpy_element_reference(self):
        a = np.array([1,2,3,2])
        e1 = a[1]
        e1 += 10
        print(a)
        e1 = 100
        print(a)
        a[1] += 20
        print(a)
        e2 = a[1:2]
        e2[:] = 30
        print(a)

    def dont_test_numpy_ordinality(self):
        a = np.array([1,2,3,4])
        a = a.reshape(2,2)
        print(a)
        a[0,1] = 10
        a[1,0] = 20
        print(a)


    def dont_test_numpy_find_and_multiply(self):
        a = np.array([1,2,3,2])
        b = np.array([10, 100, 1000, 10000])
        print("test")
        print(b[a==2])

# if __name__ == '__main__':
#     unittest.main()

