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
files = os.listdir(path)

map_filename_graph_title = {
    "rbfchain": "RBFChain",
    "adwin": "ADWIN",
    "cusum": "CUSUM",
    "ddm": "DDM",
    "eddm": "EDDM",
    "ewma": "EWMA",
    "hddma": "HDDMA",
    "ph": "PageHinkley",
    "seqdrift1": "SeqDrift1",
}
map_path_dataset = {
    "nochange": "Sem Mudança",
    "abrupt": "Mudança Abrupta",
    "gradual": "Mudança Gradual",
    "incremental": "Mudança Incremental",
}
map_filename_subplot = {
    "rbfchain": 331,
    "adwin": 332,
    "cusum": 333,
    "ddm": 334,
    "eddm": 335,
    "ewma": 336,
    "hddma": 337,
    "ph": 338,
    "seqdrift1": 339,
}


# Dataset used
dataset = None
dataset_key = None

for key in map_path_dataset:
    if key in path:
        dataset_key = key
        dataset = map_path_dataset[dataset_key]
        break

# Setup matplotlib font size and figure title
font = {"family": "monospace", "size": 8}
plt.rc("font", **font)
plt.rc("text", usetex=True)
plt.rc("font", family="serif")

fig = plt.figure()
fig.suptitle(dataset, fontsize=12)
fig.subplots_adjust(hspace=0.5, wspace=0.2)

# For each experiment result, add subplot
for file in files:
    file_absolute_path = os.path.abspath(os.path.join(path, file))
    filename = file.replace(".csv", "")

    df = pd.read_csv(file_absolute_path)

    ax = fig.add_subplot(map_filename_subplot[filename])
    ax.title.set_text(map_filename_graph_title[filename])
    ax.grid(False)
    ax.autoscale(True)
    ax.set_xlim(0, 2501)
    ax.set_ylim(0, 1.1)

    data = []
    true_changes = 0
    detected_changes = 0
    pending_drift = False

    for index, row in df.iterrows():
        data.append(row["input values"])

        if row["true changes"] > true_changes:
            ax.axvline(index, color="g", ls="-", linewidth=1)
            true_changes += 1
            pending_drift = True

        if row["detected changes"] > detected_changes:
            if not pending_drift:
                plt.axvline(index, color="r", ls="--", linewidth=1)
            else:
                plt.axvline(index, color="b", ls="--", linewidth=1)
                pending_drift = False
            detected_changes += 1

    ax.plot(range(0, len(data)), data, color="#D3D3D3", linestyle="-", linewidth=0.25)

# Legend
custom_legends = [
    Line2D([0], [0], color="#D3D3D3", linestyle="-", linewidth=0.25),
    Line2D([0], [0], color="g", ls="-", linewidth=1),
    Line2D([0], [0], color="b", ls="--", linewidth=1),
    Line2D([0], [0], color="r", ls="--", linewidth=1),
]
fig.legend(
    custom_legends,
    ["Fluxo de Dados", "Mudança de Conceito", "Mudança Detectada", "Falso-positivo"],
    ncol=2,
    borderaxespad=0,
    loc="lower center",
)

# Showing and saving
plt.show()
fig.savefig(dataset_key + ".png")
