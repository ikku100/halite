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


def play_a_turn(gamemap: array_hlt.GameMap):
    dijkstra_map = array_geographic_utils.ScoringGeoMap(gamemap.width, gamemap.height)
    dijkstra_map.calculate_scores(gamemap=gamemap)
    moves = dijkstra_map.calculate_best_moves(gamemap)
    # gamemap.log(str(moves) + '\n')
    moves = dijkstra_map.post_process_moves(gamemap, moves)
    gamemap.evolve_assuming_no_enemy_and_get_origin_and_target_and_move(moves)
    return gamemap


gamemap_filename = "gamemap.dill"
gamemap = restore_gamemap(gamemap_filename)


def play_game(gamemap: array_hlt.GameMap, turns):
    for turn in range(0, turns):
        play_a_turn(gamemap)
        sys.stdout.write(str(turn) + "\t")
        print(gamemap.my_total_production())
    print(gamemap)


play_game(gamemap, 100)

print(gamemap)
print("done")
