import glob
import os
import os.path
import statistics
import csv

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from sklearn import metrics
from tabulate import tabulate

from data_reader import DataReader
from rbfchain import RBFChain

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

CONTEXT_PARAMS = {
    "img": {"sigma": 0.01, "lambda_": 0.95, "alpha": 0.095, "delta": 1.0},
    "video": {"sigma": 0.01, "lambda_": 0.95, "alpha": 0.025, "delta": 1.0},
    "dots": {"sigma": 0.01, "lambda_": 0.95, "alpha": 0.025, "delta": 1.0}
}

def handle(dataset_path, raw=False, context=None):
    dataset_abs_path = os.path.abspath(dataset_path)
    dataset_filename = os.path.basename(dataset_abs_path)
    dataset = DataReader(dataset_abs_path)

    context = context or {}

    #
    # Plot setup
    #
    fig = plt.figure()

    # Plot data
    xdata, ydata = [], []
    fixations_x, fixations_y = [], []
    fixations_times = []

    # Lines/Points
    (ln,) = plt.plot(xdata, ydata, "-", color=(0, 1, 0), linewidth=0.25)
    (fixations,) = plt.plot(
        fixations_x,
        fixations_y,
        linestyle="",
        marker="o",
        markersize=1,
        alpha=0.25,
        color="red",
    )

    # Legends
    custom_legends = [
        Line2D([0], [0], color=(0, 1, 0), ls="-", linewidth=1),
        Line2D([0], [0], color="r", ls="-", linewidth=1),
    ]
    fig.legend(
        custom_legends,
        ["Saccades", "Fixations"],
        ncol=1,
        borderaxespad=0,
        loc="lower center",
    )

    #
    # Processing dataset
    #
    result_rbfchain_predictions = []
    result_rbfchain_fixations_positions = []

    if not raw:
        rbfchain = RBFChain(
            **CONTEXT_PARAMS[context["dataset"]]
        )
        for index, input_data in enumerate(dataset.distances):
            probability = rbfchain.add_element(input_data)

            is_fixation = probability >= rbfchain.delta

            if is_fixation:
                result_rbfchain_predictions.append(1)
                result_rbfchain_fixations_positions.append(index)
            else:
                result_rbfchain_predictions.append(0)
    else:
        for index, is_fixation in enumerate(dataset.labels):
            if is_fixation:
                result_rbfchain_predictions.append(1)
                result_rbfchain_fixations_positions.append(index)
            else:
                result_rbfchain_predictions.append(0)

    #
    # Plotting
    #
    fig.gca().set_xlim((min(dataset.x) - 10, max(dataset.x) + 10))
    fig.gca().set_ylim((min(dataset.y) - 10, max(dataset.y) + 10))

    ln.set_data(dataset.x, dataset.y)

    for fixation_position in result_rbfchain_fixations_positions:
        fixations_x.append(dataset.x[fixation_position])
        fixations_y.append(dataset.y[fixation_position])
        fixations.set_data(fixations_x, fixations_y)

    accuracy_score = metrics.accuracy_score(dataset.labels, result_rbfchain_predictions)

    precision_score = metrics.precision_score(
        dataset.labels, result_rbfchain_predictions
    )

    cohen_kappa_score = max(
        0, metrics.cohen_kappa_score(dataset.labels, result_rbfchain_predictions)
    )
    jaccard_score = metrics.jaccard_score(dataset.labels, result_rbfchain_predictions)
    recall_score = metrics.recall_score(dataset.labels, result_rbfchain_predictions)

    balanced_accuracy_score = metrics.balanced_accuracy_score(dataset.labels, result_rbfchain_predictions)
    sensivity_score = metrics.recall_score(dataset.labels, result_rbfchain_predictions, pos_label=0)
    specificity_score = metrics.recall_score(dataset.labels, result_rbfchain_predictions)

    fig.gca().set_title(f"{dataset_filename=}, {raw=}, {cohen_kappa_score=:.2f}")
    plt.savefig(f"results/{context['dataset']}-{dataset_filename}_{raw=}_{cohen_kappa_score=}.png")

    return {
        "dataset": dataset_path,
        "cohen_kappa_score": cohen_kappa_score,
        "jaccard_score": jaccard_score,
        "recall_score": recall_score,
        "accuracy_score": accuracy_score,
        "precision_score": precision_score,
        "balanced_accuracy_score": balanced_accuracy_score,
        "sensivity_score": sensivity_score,
        "specifity_score": specificity_score,
        "context": context
        # "accuracy": accuracy,
        # "balanced_accuracy_score": balanced_accuracy_score,
        # "precision_score": precision_score,
    }


for image in glob.glob("results/*.png"):
    os.remove(image)

results = []

for dataset_dir, subdirs, files in os.walk("data"):
    for file in files:
        dataset_path = dataset_dir + os.sep + file
        dataset = dataset_dir.split("/")[-1]

        if dataset_path.endswith(".csv"):

            handle(dataset_path, raw=True, context={"dataset": dataset})
            results.append(
                handle(dataset_path, raw=False, context={"dataset": dataset})
            )

# Analytical results
print(tabulate(results, tablefmt="grid", headers="keys"))
with open("results/results.csv", "w") as f:
    _csv = csv.DictWriter(f, fieldnames=results[0].keys())
    _csv.writerows(results)

# Summary results
summary_kappa_results = {}
summary_jaccard_results = {}
summary_recall_results = {}
summary_accuracy_results = {}
summary_precision_results = {}
balanced_accuracy_results = {}
sensivity_results = {}
specifity_results = {}

for result in results:
    dataset = result["context"]["dataset"]

    summary_kappa_results.setdefault(dataset, [])
    summary_kappa_results.get(dataset).append(result["cohen_kappa_score"])

    summary_jaccard_results.setdefault(dataset, [])
    summary_jaccard_results.get(dataset).append(result["jaccard_score"])

    summary_recall_results.setdefault(dataset, [])
    summary_recall_results.get(dataset).append(result["recall_score"])

    summary_accuracy_results.setdefault(dataset, [])
    summary_accuracy_results.get(dataset).append(result["accuracy_score"])

    summary_precision_results.setdefault(dataset, [])
    summary_precision_results.get(dataset).append(result["precision_score"])

    balanced_accuracy_results.setdefault(dataset, [])
    balanced_accuracy_results.get(dataset).append(result["balanced_accuracy_score"])

    sensivity_results.setdefault(dataset, [])
    sensivity_results.get(dataset).append(result["sensivity_score"])

    specifity_results.setdefault(dataset, [])
    specifity_results.get(dataset).append(result["specifity_score"])

def generate_summary_table(summary_results):
    summary_table = []
    for dataset, scores in summary_results.items():
        summary_table.append([dataset, statistics.mean(scores)])
    return summary_table

print(tabulate(generate_summary_table(summary_accuracy_results), tablefmt="grid", headers=["Dataset", "Accuracy Score"]))
print(tabulate(generate_summary_table(summary_precision_results), tablefmt="grid", headers=["Dataset", "Precision Score"]))
print(tabulate(generate_summary_table(summary_recall_results), tablefmt="grid", headers=["Dataset", "Recall Score"]))
print(tabulate(generate_summary_table(summary_jaccard_results), tablefmt="grid", headers=["Dataset", "Jaccard Score"]))
print(tabulate(generate_summary_table(summary_kappa_results), tablefmt="grid", headers=["Dataset", "Cohen Kappa Score"]))

print(tabulate(generate_summary_table(balanced_accuracy_results), tablefmt="grid", headers=["Dataset", "Balanced Accuracy Score"]))
print(tabulate(generate_summary_table(sensivity_results), tablefmt="grid", headers=["Dataset", "Sensivity Score"]))
print(tabulate(generate_summary_table(specifity_results), tablefmt="grid", headers=["Dataset", "Specifity Score"]))
