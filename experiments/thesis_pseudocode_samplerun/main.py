import rbf
from rbfplot import RBFPlot

# --
# Setup RBF
# --
rbf = rbf.RBF(sigma=3, lambda_=0.8, alpha=0.25, delta=0.5)
rbfplot = RBFPlot(step=1)

# Datasets
dataset = [0.11, 0.12, 0.13, 0.34, 0.45, 0.47, 0.33, 0.25, 0.14, 0.10]

for value in dataset:
    probability = rbf.add_element(value)
    rbfplot.update(value, rbf.in_concept_change, rbf)

    print(f"value={value} | rbf.centers={rbf.centers} | probability={probability} | rbf.in_warning_zone={rbf.in_warning_zone} | rbf.in_concept_change={rbf.in_concept_change}")
    print( rbf.markov.to_graphviz() )