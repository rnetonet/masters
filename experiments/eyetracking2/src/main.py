import argparse
import os.path

import settings
from data_reader import DataReader
from plotter import FixationsPlot, TrajectoryPlot
from rbfchain import RBFChain
from result_reader import ResultReader

import matplotlib.pyplot as plt

dataset_filename_pattern = "{dataset_folder_name}-Trial{trial}-Export-ReplaceEyeOut.txt"
result_bufalo_pattern = "{dataset_folder_name}-Trial{trial}-ResultBufalo.txt"
result_vel100_pattern = "{dataset_folder_name}-Trial{trial}-ResultVel100.txt"
result_vel_rms_pattern = "{dataset_folder_name}-Trial{trial}-ResultVelRMS.txt"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_folder")
    parser.add_argument("trial")

    args = parser.parse_args()

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

    # Process RBFChain results
    dataset = DataReader(dataset_full_path)
    rbfchain = RBFChain(**settings.RBFCHAIN_KWARGS)
    result_rbfchain = []

    for input_data in dataset.distances:
        probability = rbfchain.add_element(input_data)

        if probability >= rbfchain.delta:
            result_rbfchain.append(0)
        else:
            result_rbfchain.append(1)

    # 0 -> fixation, 1 -> saccade
    result_bufalo = ResultReader(result_bufalo_full_path).read()
    result_vel100 = ResultReader(result_vel100_full_path).read()
    result_vel_rms = ResultReader(result_vel_rms_full_path).read()

    FixationsPlot(
        dataset.x,
        dataset.y,
        [index for index, result in enumerate(result_rbfchain) if result == 0],
        title="result_rbfchain" + f" - {dataset_folder_name}",
        block=False
    ).plot()
    FixationsPlot(
        dataset.x,
        dataset.y,
        [index for index, result in enumerate(result_bufalo) if result == 0],
        title="result_bufalo" + f" - {dataset_folder_name}",
        block=False
    ).plot()
    FixationsPlot(
        dataset.x,
        dataset.y,
        [index for index, result in enumerate(result_vel100) if result == 0],
        title="result_vel100" + f" - {dataset_folder_name}",
        block=False
    ).plot()
    FixationsPlot(
        dataset.x,
        dataset.y,
        [index for index, result in enumerate(result_vel_rms) if result == 0],
        title="result_vel_rms" + f" - {dataset_folder_name}",
        block=True
    ).plot()


    input()

    # trajectory_plot = TrajectoryPlot(dataset.x, dataset.y)
    # trajectory_plot.plot()

    #


if __name__ == "__main__":
    main()
