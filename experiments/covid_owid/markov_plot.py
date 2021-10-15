import numpy as np
import matplotlib.pyplot as plt

# modules from this repository
from markovchain import MarkovChain

P = np.array([
    [0.0, 1.0, 0.0, 0.0], # 571
    [0.0, 0.5, 0.5, 0.0], # 664
    [0.0, 0.5, 0.5, 0.0], # 802
    [0.0, 0.0, 0.5, 0.5] # 962 
])
mc = MarkovChain(P, ['571', '664*', '802', '962'])
mc.draw("t1.png")


P = np.array([
    [0.0, 1.0, 0.0, 0.0], # 571
    [0.0, 0.0, 1.0, 0.0], # 664
    [0.0, 0.0, 1.0, 0.0], # 802
    [0.0, 0.0, 0.5, 0.5] # 962 
])
mc = MarkovChain(P, ['571', '664', '802*', '962'])
mc.draw("t2.png")