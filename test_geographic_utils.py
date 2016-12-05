import timeit
import unittest
from datetime import datetime
from unittest.mock import Mock

import geographic_utils
import hlt


class TestGeographicUtils(unittest.TestCase):

    def setUp(self):
        heigth = 5
        width = 5
        self.start_game_map = hlt.GameMap(height=heigth, width=width, numberOfPlayers=1)
        # self.start_game_map.contents[]
        upper_left = hlt.make_range(1, 1)
        self.start_game_map.change_portion_of_map(ranghe=upper_left, change_type=hlt.SiteValueTypes.strength, value=2)
        # self.start_game_map.change_portion_of_map(ranghe=upper_left, change_type=hlt.SiteValueTypes.production, value=2)

        whole = hlt.make_range(width - 1, heigth - 1)
        self.start_game_map.change_portion_of_map(ranghe=whole, change_type=hlt.SiteValueTypes.production, value=1)
        self.start_game_map.change_portion_of_map(ranghe=whole, change_type=hlt.SiteValueTypes.strength, value=1)

        upper_rigth = hlt.Range(3, 0, 4, 1)
        self.start_game_map.change_portion_of_map(ranghe=upper_rigth, change_type=hlt.SiteValueTypes.production, value=2)

        self.my_id = 1
        self.start_game_map.set_my_id(self.my_id)
        self.start_game_map.change_portion_of_map(ranghe=hlt.Range(2,2,2,2,), change_type=hlt.SiteValueTypes.owner, value=self.my_id)
        self.start_game_map.change_portion_of_map(ranghe=hlt.Range(2,2,2,2,), change_type=hlt.SiteValueTypes.strength, value=2)

    def test_print_map(self):
        # print(self.start_game_map)
        pass #works!

    def test_create_all_next_moves(self):
        # geographic_utils.every_site_i_own = Mock(return_value=['a', 'b'])
        # geographic_utils.every_site_i_own.
        # print (str(list(geographic_utils.create_all_next_moves())))
        self.assertEquals(len(list(geographic_utils.create_all_next_moves((s for s in ['a', 'b'])))), 25)

    def test_my_total_production(self):
        self.start_game_map.change_portion_of_map(hlt.SiteValueTypes.production, 3, hlt.Range(3,0,4,1))
        self.start_game_map.change_portion_of_map(hlt.SiteValueTypes.owner, self.my_id, hlt.Range(3, 0, 4, 1))
        self.assertEquals(self.start_game_map.my_total_production(), 13)

    def test_evolve_some_simple_steps(self):
        # print(self.start_game_map)
        me = hlt.Location(2,2)
        self.assertEquals(self.start_game_map.getSite(me).strength, 2)
        dont_move = hlt.Move(direction=hlt.STILL, loc=me)
        self.start_game_map.evolve_assuming_no_enemy([dont_move])
        self.assertEquals(self.start_game_map.getSite(me).strength, 3)
        # print(self.start_game_map)
        self.assertEquals(self.start_game_map.my_number_of_sites(), 1)
        move_up = hlt.Move(me, hlt.NORTH)
        self.start_game_map.evolve_assuming_no_enemy([move_up])
        # print(self.start_game_map)
        self.assertEquals(self.start_game_map.my_number_of_sites(), 2)

    def test_create_step_tree_depth_1(self):
        optimal_moves, best_score = geographic_utils.find_optimal_moves(self.start_game_map, 1)
        self.assertEquals(best_score, 2.5)

    def test_create_step_tree_depth_2(self):
        optimal_moves, best_score = geographic_utils.find_optimal_moves(self.start_game_map, 2)
        # print(*map(str, optimal_moves), best_score)
        # i have to write equals operators for Move and Location...
        # self.assertEquals(optimal_moves[0][0].direction, hlt.NORTH)
        # self.assertListEqual(optimal_moves[1], [hlt.Move(hlt.Location(2, 1), hlt.EAST), hlt.Move(hlt.Location(2, 2),  hlt.STILL)])
        print(geographic_utils.moves_multiple_turns_to_string(optimal_moves))
        print(best_score)
        geographic_utils.play_my_moves(self.start_game_map, optimal_moves)

    def measure_speed_optimal_solution(self, n):
        start = datetime.now()
        geographic_utils.find_optimal_moves(self.start_game_map, n)
        end = datetime.now()
        return str(end - start)

    def test_speed_search(self):
        for n in range(1,4):
            print("Time needed for " + str(n) + ": " + self.measure_speed_optimal_solution(n))
        # print("time for 2: ", timeit.timeit(geographic_utils.find_optimal_moves(self.start_game_map, 2)))
        # print("time for 3: ", timeit.timeit(geographic_utils.find_optimal_moves(self.start_game_map, 3)))

    def dont_test_create_many_steps(self):
        optimal_moves, best_score = geographic_utils.find_optimal_moves(self.start_game_map, 5)
        print(geographic_utils.moves_multiple_turns_to_string(optimal_moves))
        print(best_score)
        geographic_utils.play_my_moves(self.start_game_map, optimal_moves)


if __name__ == '__main__':
    unittest.main()