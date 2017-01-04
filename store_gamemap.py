import glob
import dill
import array_hlt
from os import path


def get_gamemap():
    bot_name = path.splitext(__file__)[0]
    myID, gamemap = array_hlt.get_init()
    array_hlt.send_init(bot_name)
    gamemap.get_frame()
    return gamemap

def restore_gamemap(gamemap_filename):
    gamemap_file = open(gamemap_filename, "rb")
    data = gamemap_file.read()
    gamemap = dill.loads(data)
    return gamemap

def find_new_file_index(filename_prefix):
    last_found_matching_filennames = glob.glob(filename_prefix + '*')
    if len(last_found_matching_filennames) > 0:
        last_found_matching_filenname = max(last_found_matching_filennames)
        file_index_old = int(last_found_matching_filenname[-8:-5])
        return file_index_old + 1
    else:
        return 0

gamemap = get_gamemap()
# gamemap_filename = "gamemap.dill"
# gamemap = restore_gamemap()

filename_prefix = "gamemaps\\gamemap_" + str(gamemap.height) + "_" + str(gamemap.starting_player_count) + "_"
file_index = find_new_file_index(filename_prefix)
filename = filename_prefix + "%03d" % file_index + ".dill"

with open(filename, 'wb') as out_strm:
    dill.dump(gamemap, out_strm)
# gamemap_file = open("gamemap.dill", "wb")
# gamemap_file.write(dill.dumps(gamemap))
# gamemap_file.close()
# dill.loads(dill.dumps(gamemap))
# pickle.dump(gamemap, open("gamemap.p", "wb"))

