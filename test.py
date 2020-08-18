from sqlitedict import SqliteDict
from shove import Shove
import time
import random
import numpy as np
from tqdm import tqdm

mydict = SqliteDict('./my_db.sqlite')
shove_tb = Shove("lite://test.db")

keys = np.array([],dtype=np.int64)
while 1:
    size = 1000
    new_keys = np.random.randint(0,1<<63,size=size)
    vals = np.random.randint(0,1<<63,size=size)
    zippola = list(zip(new_keys,vals))
    start = time.perf_counter()
    for key,value in tqdm(zippola):
        mydict[key]=value
    mydict.commit()
    print(f"sqlite insert: {time.perf_counter()-start}")
    keys = np.concatenate((keys,new_keys))
    np.random.shuffle(keys)
    start = time.perf_counter()
    for key in keys[:size]:
        val = mydict[key]
    print(f"sqlite lookup: {time.perf_counter()-start}")