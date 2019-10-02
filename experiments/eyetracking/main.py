import os

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

import rbf

# Reading dataset

# ded - less noisy
filepath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sample_trials_preprocessed",
    "ded005a06",
    "ded005a06-Export-ReplaceEyeOut.txt",
)

# juj - more noisy
# filepath = os.path.join(
#     os.path.dirname(os.path.abspath(__file__)),
#     "sample_trials_preprocessed",
#     "juj003b06",
#     "juj003b06-Export-ReplaceEyeOut.txt",
# )

#
# Read, split and parse the lines
#
fp = open(filepath, "r")
file_lines = list(fp.readlines())
fp.close()

# Lines that should be converted to int
cleaned_data = []
for index, line in enumerate(file_lines):
    # indexes <= 1 should be convert to int
    parser = int if index <= 1 else float
    cleaned_data.append(list(map(parser, line.split())))

# Unpack
x, y, x_filt, y_filt, vel_x, vel_y, vel, acc, velx_filt, vely_filt, vel_filt, acc_filt = (
    cleaned_data
)

# ---
# Plot an overview of the data
# ---

# Creating the grid spec
# fig = plt.figure()
# gs = fig.add_gridspec(nrows=3, ncols=2)

# x_plot = fig.add_subplot(gs[0, 0])
# y_plot = fig.add_subplot(gs[0, 1])
# points_plot = fig.add_subplot(gs[1, :])
# velocity_plot = fig.add_subplot(gs[2, 0])
# acc_plot = fig.add_subplot(gs[2, 1])

# fig.subplots_adjust(hspace=0.2, wspace=0.2)

# x_plot.grid(False)
# x_plot.autoscale(True)
# x_plot.set_title("x")

# y_plot.grid(False)
# y_plot.autoscale(True)
# y_plot.set_title("y")

# points_plot.grid(False)
# points_plot.autoscale(True)
# points_plot.set_title("(x, y)")

# velocity_plot.grid(False)
# velocity_plot.autoscale(True)
# velocity_plot.set_title("vel")

# acc_plot.grid(False)
# acc_plot.autoscale(True)
# acc_plot.set_title("acc")

# x_plot.plot(x)
# y_plot.plot(y)
# points_plot.plot(x, y, "bo")
# velocity_plot.plot(vel)
# acc_plot.plot(acc)

# plt.show(block=True)

# ---
# Deal with the data, identify fixations and saccadas using RBF and Markov
# ---

# Which feature will be analyzed?
feature_analyzed = vel_filt  # Velocity!

# RBF
rbf = rbf.RBF(sigma=0.25, lambda_=0.005, alpha=0.001, delta=0.250)

# --
# Plot setup
# --
fig = plt.figure()

# Title
fig.gca().set_title(filepath.split("/")[-1])

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
    input_data = feature_analyzed[frame_index]

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
    fig, handle, frames=len(x), init_func=init, interval=1, blit=True, repeat=False
)
plt.show()
