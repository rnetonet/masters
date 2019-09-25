import os

import matplotlib.pyplot as plt

import rbf

# Reading dataset
filepath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "sample_trials_preprocessed",
    "ded005a06",
    "ded005a06-Export-ReplaceEyeOut.txt",
)
fp = open(filepath, "r")
file_lines = list(fp.readlines())
fp.close()

#
# Split and parse the lines
#

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

# RBF
rbf = rbf.RBF(sigma=0.005, lambda_=0.005, alpha=0.001, delta=0.250)

# --
# Plot setup
# --
fig = plt.figure()
fig.gca().set_xlim(0, 40_000)
fig.gca().set_ylim(-40_000, 0)

# Which feature will be analyzed?
feature_analyzed = vel  # Velocity!

# ---
# Detect fixations
# ---
fixations = []

for index, input_data in enumerate(feature_analyzed):
    # Ignore zeros
    if not input_data:
        continue

    # Get correspondent x,y using index
    current_x, current_y = x[index], y[index]

    # Plot point
    plt.plot(current_x, current_y, "ko", markersize=0.5)

    # Add to the rbf
    probability = rbf.add_element(input_data)

    # Debug
    print(f"#{index}-({current_x},{current_y})->{probability}")

    # Is it a fixation ?
    if probability >= 0.5:
        fixations.append((current_x, current_y))


# --
# Plotting
# --
plt.plot(x, y, "k-", linewidth=0.25)

for fixation_point in fixations:
    _x, _y = fixation_point
    plt.plot(_x, _y, "r+", markersize=1)

plt.show()
