import argparse

import settings
from data_reader import DataReader
from rbfchain import RBFChain
from plotter import FixationsPlot

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_file_path")
    args = parser.parse_args()

    dataset = DataReader(args.dataset_file_path)

    rbfchain = RBFChain(**settings.RBFCHAIN_KWARGS)

    fixations_indexes = []
    for index, input_data in enumerate(dataset.distances):
        probability = rbfchain.add_element(input_data)

        if probability >= rbfchain.delta:
            fixations_indexes.append(index)

    fixations_plot = FixationsPlot(dataset.x, dataset.y, fixations_indexes)
    fixations_plot.plot()

if __name__ == "__main__":
    main()
