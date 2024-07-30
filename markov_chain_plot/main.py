# modules from this repository
import numpy as np
from markovchain import MarkovChain

P = np.array([
    [0.5, 0.0, 0.5, 0.0], # 664,
    [1.0, 0.0, 0.0, 0.0], # 571,
    [0.0, 0.5, 0.5, 0.0], # 802,
    [0.0, 0.0, 1.0, 0.0], # 962,
])
mc = MarkovChain(P, ['664*', '571', '802', '962'])
mc.draw("t1.svg")
