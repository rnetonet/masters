import argparse
import glob
import os
import os.path
import re
import shutil

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

trial_regex = re.compile(r"Trial([0-9]*)")


def main():
    #
    # Parse arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("datasets_top_folder")

    args = parser.parse_args()

    # Counter used in the output table and to prefix the images
    counter = 0
    accuracies = {
        "bufalo": [],
        "vel100": [],
        "vel_rms": []
    }
    precisions = {
        "bufalo": [],
        "vel100": [],
        "vel_rms": []
    }
    recalls = {
        "bufalo": [],
        "vel100": [],
        "vel_rms": []
    }

    # Output table
    headers = [
        "#",
        "Dataset",
        "Trial",
        "Algorithm",
        "Accuracy",
        "Precision",
        "Recall",
    ]
    table = []

    # Output results paths
    datasets_top_folder_abs_path = os.path.abspath(args.datasets_top_folder)
    image_result_base_path = os.path.join(os.getcwd(), "results", "images")
    result_tables_base_path = os.path.join(os.getcwd(), "results", "tables")

    result_table_full_path_txt = os.path.join(
        result_tables_base_path,
        os.path.basename(datasets_top_folder_abs_path) + ".txt",
    )
    result_table_full_path_latex = os.path.join(
        result_tables_base_path,
        os.path.basename(datasets_top_folder_abs_path) + ".tex",
    )

    result_table_summary_full_path_txt = os.path.join(
        result_tables_base_path,
        os.path.basename(datasets_top_folder_abs_path) + "_summary_" + ".txt",
    )
    result_table_summary_full_path_latex = os.path.join(
        result_tables_base_path,
        os.path.basename(datasets_top_folder_abs_path) + "_summary_" + ".tex",
    )

    # Clear previous outputs and recreated folders
    shutil.rmtree(image_result_base_path, ignore_errors=True)
    shutil.rmtree(result_tables_base_path, ignore_errors=True)

    os.makedirs(image_result_base_path)
    os.makedirs(result_tables_base_path)

    #
    # Iterate over each dataset folder.
    # Each folder has multiple trials.
    #
    for dataset_folder in os.listdir(datasets_top_folder_abs_path):
        #
        # Mount paths
        #
        dataset_folder = os.path.join(args.datasets_top_folder, dataset_folder)
        dataset_abs_path = os.path.abspath(dataset_folder)
        dataset_basename = os.path.basename(dataset_folder)

        #
        # Iterate over each trial for the current dataset folder
        #
        trials_full_paths = sorted(
            glob.glob(os.path.join(dataset_abs_path, "*ReplaceEyeOut*")),
            key=lambda trial_path: int(trial_regex.findall(trial_path)[0]),
        )

        for trial_full_path in trials_full_paths:
            # Update counter
            counter += 1

            #
            # Extract trial number and mount the paths used
            #
            trial_filename = os.path.basename(trial_full_path)
            trial = trial_regex.findall(trial_full_path)[0]

            result_bufalo_full_path = os.path.join(
                dataset_abs_path,
                result_bufalo_pattern.format(
                    dataset_folder_name=dataset_basename, trial=trial
                ),
            )
            result_vel100_full_path = os.path.join(
                dataset_abs_path,
                result_vel100_pattern.format(
                    dataset_folder_name=dataset_basename, trial=trial
                ),
            )
            result_vel_rms_full_path = os.path.join(
                dataset_abs_path,
                result_vel_rms_pattern.format(
                    dataset_folder_name=dataset_basename, trial=trial
                ),
            )

            result_image_full_path = os.path.join(
                image_result_base_path,
                str(counter) + "_" + trial_filename.replace(".txt", ".png"),
            )

            #
            # Process dataset using RBFChain
            #
            dataset = DataReader(trial_full_path)
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
            fig, axs = plt.subplots(2, 2, figsize=(12, 6))

            fig.suptitle(os.path.basename(trial_full_path))

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
            table.append(
                [
                    str(counter) + "\n" + " ",
                    dataset_basename,
                    trial,
                    "Bufalo\nVel100\nVelRMS",
                    f"{metrics.accuracy_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n{metrics.accuracy_score(result_vel100.predictions, result_rbfchain_predictions):.2f}\n{metrics.accuracy_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
                    f"{metrics.precision_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n{metrics.precision_score(result_vel100.predictions, result_rbfchain_predictions):.2f}\n{metrics.precision_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
                    f"{metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n{metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions):.2f}\n{metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
                ]
            )

            #
            # Keeps an history, enabling the creation of a summary.
            #
            accuracies["bufalo"].append(metrics.accuracy_score(result_bufalo.predictions, result_rbfchain_predictions))
            accuracies["vel100"].append(metrics.accuracy_score(result_vel100.predictions, result_rbfchain_predictions))
            accuracies["vel_rms"].append(metrics.accuracy_score(result_vel_rms.predictions, result_rbfchain_predictions))

            precisions["bufalo"].append(metrics.precision_score(result_bufalo.predictions, result_rbfchain_predictions))
            precisions["vel100"].append(metrics.precision_score(result_vel100.predictions, result_rbfchain_predictions))
            precisions["vel_rms"].append(metrics.precision_score(result_vel_rms.predictions, result_rbfchain_predictions))

            recalls["bufalo"].append(metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions))
            recalls["vel100"].append(metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions))
            recalls["vel_rms"].append(metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions))

            # Save figure
            if os.path.exists(result_image_full_path):
                os.remove(result_image_full_path)

            plt.savefig(result_image_full_path)
            plt.close()

            # output partial table
            print(f"{trial_full_path} \u2611")
            os.system("clear")
            print(
                tabulate.tabulate(
                    table, headers=headers, tablefmt="grid", floatfmt=".2f"
                )
            )

    #
    # Persist output tables
    #
    with open(result_table_full_path_txt, "w") as fp:
        output_table = tabulate.tabulate(
            table, headers=headers, tablefmt="grid", floatfmt=".2f"
        )
        fp.write(output_table)

    with open(result_table_full_path_latex, "w") as fp:
        output_table = tabulate.tabulate(
            table, headers=headers, tablefmt="latex", floatfmt=".2f"
        )
        fp.write(output_table)

    #
    # Create and persist summary tables
    #
    ...

if __name__ == "__main__":
    main()
