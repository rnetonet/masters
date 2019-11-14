import os
import os.path
import sys

import matplotlib

matplotlib.use("TKAgg", warn=False, force=True)

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

path = sys.argv[1]


# Setup matplotlib font size and figure title
font = {"family": "monospace", "size": 8}
plt.rc("font", **font)
plt.rc("text", usetex=True)
plt.rc("font", family="serif")

file_absolute_path = os.path.abspath(os.path.join(os.getcwd(), path))

df = pd.read_csv(file_absolute_path)

plt.gca().grid(False)
plt.gca().autoscale(True)
plt.gca().set_xlim(0, 2500)
plt.gca().set_ylim(0, 1)

data = []
true_changes = 0
detected_changes = 0
pending_drift = False

for index, row in df.iterrows():
    data.append(row["input values"])

    if row["true changes"] > true_changes:
        plt.axvline(index, color="g", ls="-", linewidth=1)
        true_changes += 1
        pending_drift = True

    if row["detected changes"] > detected_changes:
        if not pending_drift:
            plt.axvline(index, color="r", ls="--", linewidth=0.25, alpha=0.1)
        else:
            plt.axvline(index, color="b", ls="--", linewidth=1)
            pending_drift = False

        detected_changes += 1


plt.plot(range(0, len(data)), data, color="#D3D3D3", linestyle="-", linewidth=0.25)

# Legend
custom_legends = [
    Line2D([0], [0], color="#D3D3D3", linestyle="-", linewidth=0.25),
    Line2D([0], [0], color="g", ls="-", linewidth=1),
    Line2D([0], [0], color="b", ls="--", linewidth=1),
    Line2D([0], [0], color="r", ls="--", linewidth=1),
]
plt.legend(
    custom_legends,
    ["Fluxo de Dados", "Mudança de Conceito", "Mudança Detectada", "Falso-positivo"],
    ncol=2,
    borderaxespad=0,
    loc="lower center",
)

# Showing and saving
plt.show()
# fig.savefig(dataset_key + ".pdf")
