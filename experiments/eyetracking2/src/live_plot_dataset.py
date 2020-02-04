import argparse
import glob
import os
import os.path
import pickle
import re
import shutil
import time
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
import tabulate
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from sklearn import metrics

import settings
from data_reader import DataReader
from plotter import FixationsPlot
from rbfchain import RBFChain
from result_reader import ResultReader

# Configure matplotlib
plt.style.use("seaborn-paper")
plt.rc("font", family="serif")
PLT_FONT_SIZE = 4.75
plt.rc("font", size=PLT_FONT_SIZE)  # controls default text sizes
plt.rc("axes", titlesize=PLT_FONT_SIZE)  # fontsize of the axes title
plt.rc("axes", labelsize=PLT_FONT_SIZE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=PLT_FONT_SIZE)  # fontsize of the tick labels
plt.rc("ytick", labelsize=PLT_FONT_SIZE)  # fontsize of the tick labels
plt.rc("legend", fontsize=PLT_FONT_SIZE)  # legend fontsize
plt.rc("figure", titlesize=PLT_FONT_SIZE)  # fontsize of the figure title
plt.rc("figure", titleweight="bold")
plt.rc("figure", dpi=200)
plt.rc("figure", figsize=[7, 3.5])


#
# Parse arguments
#
parser = argparse.ArgumentParser()
parser.add_argument("dataset_path")

args = parser.parse_args()

dataset_abs_path = os.path.abspath(args.dataset_path)
dataset_filename = os.path.basename(dataset_abs_path)

#
# Plot setup
#
fig = plt.figure()
fig.gca().set_title(dataset_filename)

# Plot data
xdata, ydata = [], []
fixations_x, fixations_y = [], []
fixations_times = []

# Lines/Points
(ln,) = plt.plot(xdata, ydata, "-", color=(0, 1, 0), linewidth=0.25)
(fixations,) = plt.plot(
    fixations_x,
    fixations_y,
    linestyle="",
    marker="o",
    markersize=1,
    alpha=0.25,
    color="red",
)

# Legends
custom_legends = [
    Line2D([0], [0], color=(0, 1, 0), ls="-", linewidth=1),
    Line2D([0], [0], color="r", ls="-", linewidth=1),
]
fig.legend(
    custom_legends,
    ["Saccades", "Fixations"],
    ncol=1,
    borderaxespad=0,
    loc="lower center",
)

#
# Processing dataset
#
dataset = DataReader(dataset_abs_path)
rbfchain = RBFChain(**settings.RBFCHAIN_KWARGS)

result_rbfchain_predictions = []
result_rbfchain_fixations_positions = []

for index, input_data in enumerate(dataset.distances):
    probability = rbfchain.add_element(input_data)

    is_fixation = probability >= rbfchain.delta

    if is_fixation:
        result_rbfchain_predictions.append(1)
        result_rbfchain_fixations_positions.append(index)
    else:
        result_rbfchain_predictions.append(0)

#
# Animation functions
#
def init():
    fig.gca().set_xlim((min(dataset.x) - 1000, max(dataset.x) + 1000))
    fig.gca().set_ylim((min(dataset.y) - 1000, max(dataset.y) + 1000))
    return (ln,)


def handle(frame_index):
    print(frame_index)
    xdata.append(dataset.x[frame_index])
    ydata.append(dataset.y[frame_index])
    ln.set_data(xdata, ydata)

    if result_rbfchain_predictions[frame_index]:
        fixations_x.append(dataset.x[frame_index])
        fixations_y.append(dataset.y[frame_index])
        fixations.set_data(fixations_x, fixations_y)

    return (ln, fixations)


#
# Start animation
#
animation = FuncAnimation(
    fig,
    handle,
    frames=len(dataset.x),
    init_func=init,
    interval=0,
    blit=True,
    repeat=False,
)

plt.show()
