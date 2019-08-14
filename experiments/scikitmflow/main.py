import os.path

from scipy.io.arff import loadarff

from rbf import RBF
from rbfplot import RBFPlot

datasets = [
    {
        "name": "gradual",
        "path": os.path.join(os.path.curdir, "data", "gradual.arff")
    },
    # {
    #     "name": "abrupt",
    #     "path": os.path.join(os.path.curdir, "data", "abrupt.arff")
    # },
    # {
    #     "name": "nochange",
    #     "path": os.path.join(os.path.curdir, "data", "nochange.arff")
    # },
]

for dataset in datasets:
    arff, meta = loadarff(dataset["path"])

    plot = RBFPlot(suptitle=dataset["name"])
    rbf = RBF(sigma=2.5, lambda_=0.5, alpha=0.05, delta=1.0)

    for index, input_data in enumerate(arff["input"]):
        rbf.add_element(input_data)

        change = int(arff["change"][index])
        plot.update(input_data, change, rbf)

    plot.plot()
    # rbf.markov.to_graphviz(None)