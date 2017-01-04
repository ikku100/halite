import glob
import dill
import sys

import array_geographic_utils
import array_hlt


def restore_gamemap(gamemap_filename):
    gamemap_file = open(gamemap_filename, "rb")
    data = gamemap_file.read()
    gamemap = dill.loads(data)
    return gamemap


def play_a_turn(gamemap: array_hlt.GameMap, prod_to_str_ratio):
    scoring_geo_map = array_geographic_utils.ScoringGeoMap(gamemap.width, gamemap.height, prod_to_str_ratio)
    scoring_geo_map.calculate_scores(gamemap=gamemap)
    moves = scoring_geo_map.calculate_best_moves(gamemap)
    # gamemap.log(str(moves) + '\n')
    moves = scoring_geo_map.post_process_moves(gamemap, moves)
    gamemap.evolve_assuming_no_enemy_and_get_origin_and_target_and_move(moves)
    return gamemap


def play_game(gamemap: array_hlt.GameMap, turns, prod_to_str_ratio):
    prods = []
    strs = []
    for turn in range(0, turns):
        play_a_turn(gamemap, prod_to_str_ratio)
        prods.append(gamemap.my_total_production())
        strs.append(gamemap.my_total_strength())
        # sys.stdout.write(str(turn) + "\t")
    print(str(prod_to_str_ratio) + "\t" + str(gamemap.my_total_production()))
    print(gamemap)
    return prods, strs


def play_range_of_games(gamemap: array_hlt.GameMap):
    res = []
    for prod_to_str_ratio in range(1, 20):
        prods, strs = play_game(gamemap.__deepcopy__(), 100, prod_to_str_ratio)
        res.append((prod_to_str_ratio, prods, strs))
    return res


height = 30
starting_player_count = 2
filename_prefix = "gamemaps\\gamemap_" + str(height) + "_" + str(starting_player_count) + "_"
found_matching_filennames = glob.glob(filename_prefix + '*')
output_file = open("measurements.csv", "a")
for gamemap_filename in found_matching_filennames:
    gamemap = restore_gamemap(gamemap_filename)
    results = play_range_of_games(gamemap)
    for res in results:
        prod_to_str_ratio, prods, strs = res
        for turn in range(prods):
            output_file.write(prod_to_str_ratio + "," + turn + "," + prods[turn] + "," + strs[turn] + "\n")

output_file.close()



print(gamemap)
print("done")
