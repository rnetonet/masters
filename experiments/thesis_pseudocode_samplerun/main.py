import matplotlib

matplotlib.use("TKAgg", warn=False, force=True)

import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import rbf
from rbfplot import RBFPlot

# --
# Setup RBF
# --
rbf = rbf.RBF(sigma=3, lambda_=0.8, alpha=0.25, delta=0.5)
rbfplot = RBFPlot(step=1)

# Datasets
dataset = [0.11, 0.12, 0.13, 0.33, 0.34, 0.45, 0.6, 0.33, 0.25, 0.14, 0.11, 0.15]

#
# Plot setup
#

# Font size
font = {"family": "normal", "size": 7}
plt.rc("font", **font)

# Subplots
fig = plt.figure()
gs = fig.add_gridspec(nrows=3, ncols=4)
plots = []
for i in range(3):
    for j in range(4):
        plot = fig.add_subplot(gs[i, j])
        plot.grid(False)
        plot.autoscale(False)
        plot.set_xlim([0, 13])
        plot.set_ylim([0, 1])

        plots.append(plot)

fig.subplots_adjust(hspace=0.3, wspace=0.3)

# Processing and plotting

points = []
concept_drifts_positions = []
warnings_zones_positions = []

colors = list(mcolors.TABLEAU_COLORS.keys())

for position, value in enumerate(dataset):
    probability = rbf.add_element(value)
    rbfplot.update(value, rbf.in_concept_change, rbf)

    print(
        f"{position}: {value=} | {rbf.centers=} | {rbf.concept_center=} | {rbf.activated_center=} | {probability=} | {rbf.in_warning_zone=} | {rbf.in_concept_change=}"
    )
    points.append(
        {
            "position": position + 1,  # Fake starting with 1
            "value": value,
            "concept_center": rbf.concept_center,
            "activated_center": rbf.activated_center,
            "probability": probability,
            "color": colors[rbf.centers.index(rbf.activated_center)],
        }
    )

    if rbf.in_warning_zone:
        warnings_zones_positions.append(position + 1)  # Fake start with 1

    if rbf.in_concept_change:
        # print(rbf.markov.to_graphviz())
        concept_drifts_positions.append(position + 1)  # Fake start with 1

    #
    # plot
    #
    for point in points:
        plots[position].plot(
            point["position"],
            point["value"],
            linewidth=0.25,
            markersize=4,
            marker="o",
            linestyle="solid",
            color=point["color"],
        )
        plots[position].set_title(
            f"T{point['position']} | E={point['value']} | CC={point['concept_center']} | CA={point['activated_center']}"
        )

    for warning_position in warnings_zones_positions:
        plots[position].axvline(
            x=warning_position, linewidth=0.12, linestyle="-", color="y"
        )

    for drift_position in concept_drifts_positions:
        plots[position].axvline(x=drift_position, linewidth=0.25, color="r")

    rbf.markov.to_png(f"img/T{position + 1}")  # Fake start with 1

# Plot
plt.show(block=True)
