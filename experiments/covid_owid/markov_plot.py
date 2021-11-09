import numpy as np
import matplotlib.pyplot as plt

# modules from this repository
from markovchain import MarkovChain

P = np.array([
    [0.0, 0.5, 0.5, 0.0], # 1262,
    [0.0, 0.5, 0.5, 0.0], # 1595,
    [0.0, 0.5, 0.5, 0.0], # 2165,
    [0.0, 0.0, 1.0, 0.0], # 3780,
])
mc = MarkovChain(P, ['1262*', '1595', '2165', '3780'])
mc.draw("t5.png")


P = np.array([
    [0.0, 1.0, 0.0, 0.0], # 1262,
    [0.0, 1.0, 0.0, 0.0], # 1595,
    [0.0, 0.5, 0.5, 0.0], # 2165,
    [0.0, 0.0, 1.0, 0.0], # 3780,
])
mc = MarkovChain(P, ['1262', '1595*', '2165', '3780'])
mc.draw("t6.png")

