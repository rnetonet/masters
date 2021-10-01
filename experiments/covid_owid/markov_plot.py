import numpy as np
import matplotlib.pyplot as plt

# modules from this repository
from markovchain import MarkovChain

P = np.array([[0.5, 0.5], [0.0, 1.0]]) # Transition matrix
mc = MarkovChain(P, ['571', '962'])
mc.draw("t1.png")

P = np.array([[0.0, 1.0], [0.0, 1.0]]) # Transition matrix
mc = MarkovChain(P, ['571', '962'])
mc.draw("t2.png")