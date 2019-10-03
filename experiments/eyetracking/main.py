import argparse
import os

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

import rbf

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
# Calculating distances
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

# Lines/Points
ln, = plt.plot(xdata, ydata, "k-", linewidth=0.25)
fixations, = plt.plot(fixations_x, fixations_y, "ro", markersize=0.5)


def init():
    fig.gca().set_xlim(-20_000, 40_000)
    fig.gca().set_ylim(-40_000, 10_000)
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

    xdata.append(x[frame_index])
    ydata.append(y[frame_index])
    ln.set_data(xdata, ydata)

    # Is it a fixation ?
    if probability >= rbf.delta:
        fixations_x.append(x[frame_index])
        fixations_y.append(y[frame_index])
        fixations.set_data(fixations_x, fixations_y)

    return (ln, fixations)


ani = FuncAnimation(
    fig, handle, frames=len(x), init_func=init, interval=0.5, blit=True, repeat=False
)
plt.show()
