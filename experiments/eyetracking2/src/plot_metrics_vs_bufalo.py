import pickle
import matplotlib.pyplot as plt
import os

# Configure matplotlib
plt.style.use("seaborn-paper")
plt.rc("font", family="serif")
PLT_FONT_SIZE = 4.75
plt.rc("font", size=PLT_FONT_SIZE)  # controls default text sizes
plt.rc("axes", titlesize=PLT_FONT_SIZE)  # fontsize of the axes title
plt.rc("axes", labelsize=PLT_FONT_SIZE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=PLT_FONT_SIZE)  # fontsize of the tick labels
plt.rc("ytick", labelsize=PLT_FONT_SIZE)  # fontsize of the tick labels
plt.rc("legend", fontsize=PLT_FONT_SIZE)  # legend fontsize
plt.rc("figure", titlesize=PLT_FONT_SIZE)  # fontsize of the figure title
plt.rc("figure", titleweight="bold")
plt.rc("figure", dpi=200)
plt.rc("figure", figsize=[7, 3.5])

# Pickle object path
pickle_obj_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "results/pickle/", "high.pickle"
)

data = pickle.load(open(pickle_obj_path, "rb"))

# Plot settings
name_map = {
    "ACC": "accuracies",
    "PRC": "precisions",
    "RCL": "recalls",
}

algorithm_name = "buffalo"

# Plot
fig, ax = plt.subplots()
ax.plot(
    data["accuracies"]["bufalo"],
    marker=".",
    markersize=0.2,
    linestyle="-",
    linewidth=0.2,
    alpha=0.5,
    label="ACC",
)
ax.plot(
    data["precisions"]["bufalo"],
    marker=".",
    markersize=0.2,
    linestyle="-",
    linewidth=0.2,
    alpha=0.5,
    label="PRC",
)
ax.plot(
    data["recalls"]["bufalo"],
    marker=".",
    markersize=0.2,
    linestyle="-",
    linewidth=0.2,
    alpha=0.5,
    label="RCL",
)

plt.gca().set_ylabel('Value')
plt.gca().set_xlabel('Trial')

plt.legend()
plt.show()