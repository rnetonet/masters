import os
import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

path = sys.argv[1]
files = os.listdir(path)

map_filename_graph_title = {
    "adwin": "ADWIN",
    "pht": "PageHinkley",
    "cusum": "CUSUM",
    "rbf": "RBFDriftDetector",
}
map_path_dataset = {
    "nochange": "Sem Mudanças",
    "abrupt": "Mudanças Abruptas",
    "gradual": "Mudanças Graduais",
}
map_filename_subplot = {"rbf": 221, "cusum": 222, "pht": 223, "adwin": 224}


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
fig.subplots_adjust(hspace=0.3, wspace=0.2)

# For each experiment result, add subplot
for file in files:
    file_absolute_path = os.path.abspath(os.path.join(path, file))
    filename = file.replace(".csv", "")

    df = pd.read_csv(file_absolute_path)

    ax = fig.add_subplot(map_filename_subplot[filename])
    ax.title.set_text(map_filename_graph_title[filename])
    ax.grid(False)
    ax.autoscale(True)
    ax.set_xlim(0, 2500)
    ax.set_ylim(0, 1)

    data = []
    true_changes = 0
    detected_changes = 0

    for index, row in df.iterrows():
        data.append(row["input values"])

        if row["true changes"] > true_changes:
            ax.axvline(index - 25, color="g", ls="-", linewidth=1)
            true_changes += 1

        if row["detected changes"] > detected_changes:
            if (
                filename == "rbf" and row["detected changes"] == 1 and "gradual" in path
            ) or filename == "adwin":
                ax.axvline(index, color="r", ls="--", linewidth=1)
            else:
                ax.axvline(index + 25, color="b", ls="--", linewidth=1)
            detected_changes += 1

    ax.plot(range(0, len(data)), data, color="#D3D3D3", linestyle="-", linewidth=0.25)

plt.show()
fig.savefig(dataset_key + ".pdf")
