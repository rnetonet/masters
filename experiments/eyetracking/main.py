import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Adjust sys.path, allowing to import scikitmflow RBF implemetation
parent_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
sys.path.append(parent_dir.as_posix())

from scikitmflow import rbf, rbfplot

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

# Creating the grid spec
fig = plt.figure()
gs = fig.add_gridspec(nrows=3, ncols=2)

x_plot = fig.add_subplot(gs[0, 0])
y_plot = fig.add_subplot(gs[0, 1])
points_plot = fig.add_subplot(gs[1, :])
velocity_plot = fig.add_subplot(gs[2, 0])
acc_plot = fig.add_subplot(gs[2, 1])

fig.subplots_adjust(hspace=0.2, wspace=0.2)

x_plot.grid(False)
x_plot.autoscale(True)
x_plot.set_title("x")

y_plot.grid(False)
y_plot.autoscale(True)
y_plot.set_title("y")

points_plot.grid(False)
points_plot.autoscale(True)
points_plot.set_title("(x, y)")

velocity_plot.grid(False)
velocity_plot.autoscale(True)
velocity_plot.set_title("vel")

acc_plot.grid(False)
acc_plot.autoscale(True)
acc_plot.set_title("acc")

x_plot.plot(x)
y_plot.plot(y)
points_plot.plot(x, y, "bo")
velocity_plot.plot(vel)
acc_plot.plot(acc)

plt.show(block=True)

# RBF
plot = rbfplot.RBFPlot(suptitle="Fixation", step=100)
rbf = rbf.RBF(sigma=0.005, lambda_=0.005, alpha=0.001, delta=0.250)

for index, input_data in enumerate(vel):
    if not input_data:
        continue

    rbf.add_element(input_data)

    if rbf.in_concept_change:
        print(f"\t data: {input_data}, rbf.centers={sorted(rbf.centers)}, rbf.actual_center={rbf.actual_center} \n")
        print(json.dumps(rbf.markov.system, indent=4))
    else:
        print(f"data: {input_data}, rbf.centers={sorted(rbf.centers)}, rbf.actual_center={rbf.actual_center} \n")

    # print(json.dumps(rbf.markov.system, indent=4))

    # change = 1 if index in (2800, 3000, 3100, 3400, 4900, 6150) else 0
    # plot.update(input_data, change, rbf)

# plt.show( plot.plot(len(vel)) )

# plot.plot_animation()
