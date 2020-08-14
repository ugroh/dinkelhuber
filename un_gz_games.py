import gzip
import shutil
import os

for pid in os.listdir("games"):
    for gname in os.listdir(os.path.join("games",pid)):
        if gname.endswith(".gz"):
            full_path = os.path.join("games",pid,gname)
            with gzip.open(full_path, 'rb') as f_in:
                with open(full_path.replace(".gz",""), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(pid)
            os.remove(full_path)