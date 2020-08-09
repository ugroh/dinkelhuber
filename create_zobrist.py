import numpy as np
zobrist = np.random.randint(0,1<<61,(3,9,9))
np.save("zobrist.npy",zobrist)