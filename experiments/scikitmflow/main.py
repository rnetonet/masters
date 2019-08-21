import os.path
import json

from scipy.io.arff import loadarff

from rbf import RBF
from rbfplot import RBFPlot

datasets = [
    # {
    #     "name": "nochange",
    #     "path": os.path.join(os.path.curdir, "data", "nochange.arff"),
    #     "rbf": {"sigma": 2.5, "lambda_": 0.5, "alpha": 0.15, "delta": 0.75}
    # },
    {
        "name": "abrupt",
        "path": os.path.join(os.path.curdir, "data", "abrupt.arff"),
        "rbf": {"sigma": 2.5, "lambda_": 0.5, "alpha": 0.05, "delta": 0.75}
    },
    # {
    #     "name": "gamaabrupt",
    #     "path": os.path.join(os.path.curdir, "data", "gamaabrupt.arff"),
    #     "rbf": {"sigma": 2.5, "lambda_": 0.5, "alpha": 0.001, "delta": 1.0}
    # },
    # {
    #     "name": "gradual",
    #     "path": os.path.join(os.path.curdir, "data", "gradual.arff"),
    #     "rbf": {"sigma": 2.5, "lambda_": 0.5, "alpha": 0.25, "delta": 0.75}
    # },
]

for dataset in datasets:
    arff, meta = loadarff(dataset["path"])

    plot = RBFPlot(suptitle=dataset["name"], step=100)
    rbf = RBF(**dataset["rbf"])

    for index, input_data in enumerate(arff["input"]):
        rbf.add_element(input_data)

        change = int(arff["change"][index])
        plot.update(input_data, change, rbf)

        print(json.dumps(rbf.markov.system, indent=4))

    # rbf.markov.to_graphviz(dataset["name"] + ".gv")
    plot.plot_animation()