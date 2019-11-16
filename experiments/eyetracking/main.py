import argparse
import os

import matplotlib

matplotlib.use("TKAgg", warn=False, force=True)

import matplotlib.pyplot as plt
plt.style.use('seaborn-white')

import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

import rbf

import dede_clusterfix
import juju_clusterfix

# --
# Argument parser
# --
args_parser = argparse.ArgumentParser(
    description="Track some primatal friends \U0001F435"
)
args_parser.add_argument(
    "-d", "--dataset", nargs=1, type=str, choices=("dede", "juju"), required=True
)
args_parser.add_argument(
    "-f",
    "--feature",
    nargs=1,
    type=str,
    choices=("dist_filt", "vel_filt"),
    required=True,
)

args = args_parser.parse_args()

dataset, = args.dataset
feature, = args.feature

# --
# Reading dataset
# --

filepaths = {
    "dede": os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sample_trials_preprocessed",
        "ded005a06",
        "ded005a06-Export-ReplaceEyeOut.txt",
    ),
    "juju": os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sample_trials_preprocessed",
        "juj003b06",
        "juj003b06-Export-ReplaceEyeOut.txt",
    ),
}

clusterfixs = {
    "dede": dede_clusterfix,
    "juju": juju_clusterfix
}

plot_limits = {
    "dede": {
        "xlim": (0, 3.5),
        "ylim": (-2.5, 0)
    },
    "juju": {
        "xlim": (-1, 2.5),
        "ylim": (-3.5, 0)
    },
}

# --
# Define clusterfix module for comparisons
# --
clusterfix = clusterfixs[dataset]

# --
# Read, split and parse the lines
# --
fp = open(filepaths[dataset], "r")
file_lines = list(fp.readlines())
fp.close()

# Lines that should be converted to int
cleaned_data = []
for index, line in enumerate(file_lines):
    # indexes <= 1 should be convert to int
    parser = int if index <= 1 else float
    cleaned_data.append(list(map(parser, line.split())))

# Unpack dataset
x, y, x_filt, y_filt, vel_x, vel_y, vel, acc, velx_filt, vely_filt, vel_filt, acc_filt = (
    cleaned_data
)

# --
# Creating "dist_filt" through the euclidian distance cauculus
# --
dist_filt = []
for _x, _y in zip(x_filt, y_filt):
    d = np.sqrt(np.power(_x, 2) + np.power(_y, 2))
    dist_filt.append(d)


# --
# Which feature will be analyzed? And which params should be aplied to the RBF ?
# --
features = {
    "dist_filt": {
        "data": dist_filt,
        "kwargs": {"sigma": 0.005, "lambda_": 0.5, "alpha": 0.05, "delta": 0.75},
    },
    "vel_filt": {
        "data": vel_filt,
        "kwargs": {"sigma": 0.25, "lambda_": 0.005, "alpha": 0.001, "delta": 0.250},
    },
}

# --
# Setup RBF
# --
rbf = rbf.RBF(**features[feature]["kwargs"])

# --
# Plot setup
# --
fig = plt.figure()

# Title
fig.gca().set_title(dataset + " - " + feature)

# Datasets
xdata, ydata = [], []
fixations_x, fixations_y = [], []
common_fixations_x, common_fixations_y = [], []
fixations_times = []

# Lines/Points
ln, = plt.plot(xdata, ydata, "-", color=(0, 1, 0), linewidth=0.5)
fixations, = plt.plot(fixations_x, fixations_y, "ro", markersize=0.25)
common_fixations, = plt.plot(fixations_x, fixations_y, "o", color="blue", markersize=0.25, alpha=0.25)

custom_legends = [
    Line2D([0], [0], color=(0, 1, 0), ls="-", linewidth=1),
    Line2D([0], [0], color="r", ls="-", linewidth=1),
    Line2D([0], [0], color="blue", ls="-", linewidth=1),
]
fig.legend(
    custom_legends,
    ["Sacadas", "Fixações", "Fixações \u2229 ClusterFix"],
    ncol=1,
    borderaxespad=0,
    loc="upper right",
)

# Setup matplotlib font size and figure title
font = {"size": 8}
plt.rc("font", **font)
plt.rc("text", usetex=True)

def init():
    fig.gca().set_xlim(*plot_limits[dataset]["xlim"])
    fig.gca().set_ylim(*plot_limits[dataset]["ylim"])
    return (ln,)


# --
# Detecting fixations and updating canvas
# --
def handle(frame_index):
    input_data = features[feature]["data"][frame_index]

    # Ignore zeros
    if not input_data:
        return (ln, fixations)

    # Add to the rbf
    probability = rbf.add_element(input_data)

    # Scale down
    scale_factor = 10 ** 4
    scaled_x = x[frame_index] / scale_factor
    scaled_y = y[frame_index] / scale_factor

    xdata.append(scaled_x)
    ydata.append(scaled_y)
    ln.set_data(xdata, ydata)

    # Is it a fixation ?
    if probability >= rbf.delta:
        fixations_x.append(scaled_x)
        fixations_y.append(scaled_y)
        fixations_times.append(frame_index + 1)
        fixations.set_data(fixations_x, fixations_y)

        # Clusterfix indexes start with 1, so we have to increment
        if frame_index + 1 in clusterfix.fixations_times:
            common_fixations_x.append(scaled_x)
            common_fixations_y.append(scaled_y)
            common_fixations.set_data(common_fixations_x, common_fixations_y)

    return (ln, fixations, common_fixations)


ani = FuncAnimation(
    fig, handle, frames=len(x), init_func=init, interval=0.000000001, blit=True, repeat=False
)

plt.show()

# --
# Validation against clusterfix data
# --
fixations_times = set(sorted(fixations_times))
fixation_times_intersection = list(fixations_times & clusterfix.fixations_times)

print(f"{len(fixations_times)=}")
print(f"{len(clusterfix.fixations_times)=}")
print(f"{len(fixation_times_intersection)=}")

# DTW plot
# from dtaidistance import dtw
# from dtaidistance import dtw_visualisation as dtwvis
# import numpy as np

# s1 = np.array(list(fixations_times))
# s2 = np.array(list(clusterfix.fixations_times))
# dtw_distance = dtw.distance(s1, s2)

# print(f"{dtw_distance=}")

# path = dtw.warping_path(s1, s2)
# dtwvis.plot_warping(s1, s2, path, filename="warp.png")

# RMSE
from sklearn.metrics import mean_squared_error, classification_report, accuracy_score
from math import sqrt

y_actual = [1 if time in clusterfix.fixations_times else 0 for time in range(1, len(features[feature]["data"]) + 1)]
y_predicted = [1 if time in fixations_times else 0 for time in range(1, len(features[feature]["data"]) + 1)]

rmse = sqrt(mean_squared_error(y_actual, y_predicted))
print(f"{rmse=:.2f}")

print(f"{accuracy_score(y_actual, y_predicted)=}")
print(f"{accuracy_score(y_actual, y_predicted, normalize=False)=}")