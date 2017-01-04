import gzip
import glob
import shutil

file_index_old = int(max(glob.glob('submit*'))[6:8])
file_index = file_index_old + 1
filename = "submit" + "%02d" % file_index + ".zip"
print(filename)



import zipfile

print('creating archive ' + filename)
zf = zipfile.ZipFile(filename, mode='w')
try:
    input_files = ["array_geographic_utils.py", "array_hlt.py", "MyBot.py"]
    for input_file in input_files:
        zf.write(input_file)
finally:
    print('closing')
    zf.close()

