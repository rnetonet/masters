import decimal
import sys

import matplotlib

matplotlib.use("TKAgg", force=True)

import matplotlib.colors as mcolors
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd
from scipy.io import arff

import rbf

# --
# Setup decimals
# --
decimal.getcontext().prec = 2

# --
# Setup RBF
# --
rbf = rbf.RBF(sigma=2, lambda_=0.5, alpha=0.005, delta=1.0)

# Datasets
filename = sys.argv[1]
arff = arff.loadarff(filename)
arff_data = arff[0]
df = pd.DataFrame(arff_data)
dataset = df["input"]

#
# Plot setup
#

# Font size
font = {"family": "normal", "size": 7}
plt.rc("font", **font)
plt.grid(False)
plt.autoscale(False)
plt.gca().set_xlim(0, 2501)
plt.gca().set_ylim(0, 1.1)

# Processing and plotting

x = []
y = []
points = []
concept_drifts_positions = []
warnings_zones_positions = []

colors = list(mcolors.TABLEAU_COLORS.keys())

for position, value in enumerate(dataset):
    value = decimal.Decimal(value) * 1

    probability = rbf.add_element(value)

    print(
        f"{position}: {value=} | {rbf.centers=} | {rbf.concept_center=} | {rbf.activated_center=} | {probability=} | {rbf.in_warning_zone=} | {rbf.in_concept_change=}"
    )

    x.append(position)
    y.append(value)
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
        print(rbf.markov.to_graphviz())
        concept_drifts_positions.append(position + 1)  # Fake start with 1

plt.plot(x, y, color="k", linestyle="-", linewidth=0.1)

for drift_position in concept_drifts_positions:
    plt.axvline(x=drift_position, linewidth=0.25, color="r")

# Plot
plt.show(block=True)
