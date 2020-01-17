import argparse
import os.path

import matplotlib.pyplot as plt
import tabulate
from sklearn import metrics

import settings
from data_reader import DataReader
from plotter import FixationsPlot
from rbfchain import RBFChain
from result_reader import ResultReader

#
# Patterns
#
dataset_filename_pattern = "{dataset_folder_name}-Trial{trial}-Export-ReplaceEyeOut.txt"
result_bufalo_pattern = "{dataset_folder_name}-Trial{trial}-ResultBufalo.txt"
result_vel100_pattern = "{dataset_folder_name}-Trial{trial}-ResultVel100.txt"
result_vel_rms_pattern = "{dataset_folder_name}-Trial{trial}-ResultVelRMS.txt"


def main():
    #
    # Parse arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_folder")
    parser.add_argument("trial")

    args = parser.parse_args()

    #
    # Mount paths
    #
    dataset_abs_path = os.path.abspath(args.dataset_folder)
    dataset_folder_name = os.path.basename(dataset_abs_path)

    dataset_full_path = os.path.join(
        dataset_abs_path,
        dataset_filename_pattern.format(
            dataset_folder_name=dataset_folder_name, trial=args.trial
        ),
    )
    result_bufalo_full_path = os.path.join(
        dataset_abs_path,
        result_bufalo_pattern.format(
            dataset_folder_name=dataset_folder_name, trial=args.trial
        ),
    )
    result_vel100_full_path = os.path.join(
        dataset_abs_path,
        result_vel100_pattern.format(
            dataset_folder_name=dataset_folder_name, trial=args.trial
        ),
    )
    result_vel_rms_full_path = os.path.join(
        dataset_abs_path,
        result_vel_rms_pattern.format(
            dataset_folder_name=dataset_folder_name, trial=args.trial
        ),
    )

    #
    # Process dataset using RBFChain
    #
    dataset = DataReader(dataset_full_path)
    rbfchain = RBFChain(**settings.RBFCHAIN_KWARGS)
    result_rbfchain = []
    result_rbfchain_fixations_positions = []

    for index, input_data in enumerate(dataset.distances):
        probability = rbfchain.add_element(input_data)

        if probability >= rbfchain.delta:
            result_rbfchain.append(0)
            result_rbfchain_fixations_positions.append(index)
        else:
            result_rbfchain.append(1)

    result_rbfchain_predictions = [not result for result in result_rbfchain]

    #
    # Reading results
    # 0 -> fixation, 1 -> saccade
    #
    result_bufalo = ResultReader(result_bufalo_full_path)
    result_vel100 = ResultReader(result_vel100_full_path)
    result_vel_rms = ResultReader(result_vel_rms_full_path)

    #
    # Creating the main plot and subplots
    #
    fig, axs = plt.subplots(2, 2)

    fig.suptitle(os.path.basename(dataset_full_path))

    FixationsPlot(
        dataset.x,
        dataset.y,
        result_rbfchain_fixations_positions,
        title="RBFChain",
        block=False,
    ).plot(axs[0, 0])
    FixationsPlot(
        dataset.x,
        dataset.y,
        result_bufalo.fixations_positions,
        title="Bufalo",
        block=False,
    ).plot(axs[0, 1])
    FixationsPlot(
        dataset.x,
        dataset.y,
        result_vel100.fixations_positions,
        title="vel100",
        block=False,
    ).plot(axs[1, 0])
    FixationsPlot(
        dataset.x,
        dataset.y,
        result_vel_rms.fixations_positions,
        title="vel_rms",
        block=True,
    ).plot(axs[1, 1])

    #
    # Calculate accuracy and tabulate
    #
    headers = ["Trial", "Accuracy", "Precision", "Recall"]
    table = [
        [
            "RBFChain x Bufalo",
            f"{metrics.accuracy_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}",
            f"{metrics.precision_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}",
            f"{metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}",
        ],
        [
            "RBFChain x Vel100",
            f"{metrics.accuracy_score(result_vel100.predictions, result_rbfchain_predictions):.2f}",
            f"{metrics.precision_score(result_vel100.predictions, result_rbfchain_predictions):.2f}",
            f"{metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions):.2f}",
        ],
        [
            "RBFChain x VelRMS",
            f"{metrics.accuracy_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
            f"{metrics.precision_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
            f"{metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
        ],
    ]
    print(tabulate.tabulate(table, headers))

    # Exhibit
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
