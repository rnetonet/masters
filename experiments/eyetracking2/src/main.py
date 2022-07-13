import argparse
import glob
import os
import os.path
import pickle
import re
import shutil

import matplotlib.pyplot as plt
import numpy as np
import tabulate
from sklearn import metrics

import settings
from data_reader import DataReader
from plotter import FixationsPlot
from rbfchain import RBFChain
from result_reader import ResultReader

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
    accuracies = {"clusterfix": [], "vel_100": [], "vel_rms": []}
    precisions = {"clusterfix": [], "vel_100": [], "vel_rms": []}
    recalls = {"clusterfix": [], "vel_100": [], "vel_rms": []}

    balanced_accuracy = {"clusterfix": [], "vel_100": [], "vel_rms": []}
    sensivity = {"clusterfix": [], "vel_100": [], "vel_rms": []}
    specificity = {"clusterfix": [], "vel_100": [], "vel_rms": []}

    # Output table
    headers = [
        "Trial",
        "Dataset",
        "Algorithm",
        "Accuracy",
        "Precision",
        "Recall",
        "Balanced Accuracy",
        "Specifity",
        "Sensivity",
    ]
    table = []

    # Output results paths
    datasets_top_folder_abs_path = os.path.abspath(args.datasets_top_folder)
    summary_image_result_base_path = os.path.join(
        os.getcwd(), "results", "images", "summary"
    )
    analytical_image_result_base_path = os.path.join(
        os.getcwd(), "results", "images", "analytical"
    )
    result_tables_base_path = os.path.join(os.getcwd(), "results", "tables")
    result_pickle_base_path = os.path.join(os.getcwd(), "results", "pickle")

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
        os.path.basename(datasets_top_folder_abs_path) + "_summary" + ".txt",
    )
    result_table_summary_full_path_latex = os.path.join(
        result_tables_base_path,
        os.path.basename(datasets_top_folder_abs_path) + "_summary" + ".tex",
    )

    result_pickle_full_path = os.path.join(
        result_pickle_base_path,
        os.path.basename(datasets_top_folder_abs_path) + ".pickle",
    )

    # Clear previous outputs and recreated folders
    shutil.rmtree(summary_image_result_base_path, ignore_errors=True)
    shutil.rmtree(analytical_image_result_base_path, ignore_errors=True)
    shutil.rmtree(result_tables_base_path, ignore_errors=True)
    shutil.rmtree(result_pickle_base_path, ignore_errors=True)

    os.makedirs(summary_image_result_base_path)
    os.makedirs(analytical_image_result_base_path)
    os.makedirs(result_tables_base_path)
    os.makedirs(result_pickle_base_path)

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

        # Sort the trials
        trials_full_paths = sorted(
            glob.glob(os.path.join(dataset_abs_path, "*ReplaceEyeOut*")),
            key=lambda trial_path: int(trial_regex.findall(trial_path)[0]),
        )

        # For each trial
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
                summary_image_result_base_path,
                str(counter) + "_" + trial_filename.replace(".txt", ".png"),
            )
            result_image_rbfchain_full_path = os.path.join(
                analytical_image_result_base_path,
                str(counter) + "_" + trial_filename.replace(".txt", "_rbfchain.png"),
            )
            result_image_bufalo_full_path = os.path.join(
                analytical_image_result_base_path,
                str(counter) + "_" + trial_filename.replace(".txt", "_bufalo.png"),
            )
            result_image_vel100_full_path = os.path.join(
                analytical_image_result_base_path,
                str(counter) + "_" + trial_filename.replace(".txt", "_vel100.png"),
            )
            result_image_velrms_full_path = os.path.join(
                analytical_image_result_base_path,
                str(counter) + "_" + trial_filename.replace(".txt", "_velrms.png"),
            )

            #
            # Process dataset using RBFChain
            #
            dataset = DataReader(trial_full_path)
            rbfchain = RBFChain(**settings.RBFCHAIN_KWARGS)

            result_rbfchain_predictions = []
            result_rbfchain_fixations_positions = []

            for index, input_data in enumerate(dataset.distances):
                probability = rbfchain.add_element(input_data)

                is_fixation = probability >= rbfchain.delta

                if is_fixation:
                    result_rbfchain_predictions.append(1)
                    result_rbfchain_fixations_positions.append(index)
                else:
                    result_rbfchain_predictions.append(0)

            #
            # Reading results files
            #
            result_bufalo = ResultReader(result_bufalo_full_path)
            result_vel100 = ResultReader(result_vel100_full_path)
            result_vel_rms = ResultReader(result_vel_rms_full_path)

            #
            # Creating the main plot and subplots
            #
            fig, axs = plt.subplots(2, 2)

            fig.suptitle(os.path.basename(trial_full_path))

            # RBFChain
            rbfchain_fixations_plot = FixationsPlot(
                dataset.x,
                dataset.y,
                result_rbfchain_fixations_positions,
                title="RBF & Markov Chain",
                block=False,
            )
            rbfchain_fixations_plot.plot_in_ax(axs[0, 0])
            rbfchain_fixations_plot.plot_to_file(result_image_rbfchain_full_path)

            # Bufalo
            bufalo_fixations_plot = FixationsPlot(
                dataset.x,
                dataset.y,
                result_bufalo.fixations_positions,
                title="ClusterFix",
                block=False,
            )
            bufalo_fixations_plot.plot_in_ax(axs[0, 1])
            bufalo_fixations_plot.plot_to_file(result_image_bufalo_full_path)

            # Vel 100
            vel100_fixations_plot = FixationsPlot(
                dataset.x,
                dataset.y,
                result_vel100.fixations_positions,
                title="Vel 100",
                block=False,
            )
            vel100_fixations_plot.plot_in_ax(axs[1, 0])
            vel100_fixations_plot.plot_to_file(result_image_vel100_full_path)

            # Vel RMS
            velrms_fixations_plot = FixationsPlot(
                dataset.x,
                dataset.y,
                result_vel_rms.fixations_positions,
                title="Vel RMS",
                block=True,
            )
            velrms_fixations_plot.plot_in_ax(axs[1, 1])
            velrms_fixations_plot.plot_to_file(result_image_velrms_full_path)

            #
            # Calculate accuracy and tabulate
            #
            table.append(
                [
                    str(counter) + "\n" + " " + "\n" + " ",
                    dataset_basename + "-" + trial + "\n" + " " + "\n" + " ",
                    "ClusterFix",
                    f"{metrics.accuracy_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n\n",
                    f"{metrics.precision_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n\n",
                    f"{metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n\n",

                    f"{metrics.balanced_accuracy_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n\n",
                    f"{metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions, pos_label=0):.2f}\n\n",
                    f"{metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions):.2f}\n\n",

                ],
            )
            table.append(
                [
                    "",
                    "",
                    "Vel 100",
                    f"{metrics.accuracy_score(result_vel100.predictions, result_rbfchain_predictions):.2f}",
                    f"{metrics.precision_score(result_vel100.predictions, result_rbfchain_predictions):.2f}",
                    f"{metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions):.2f}",

                    f"{metrics.balanced_accuracy_score(result_vel100.predictions, result_rbfchain_predictions):.2f}\n\n",
                    f"{metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions, pos_label=0):.2f}\n\n",
                    f"{metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions):.2f}\n\n",
                ],
            )
            table.append(
                [
                    "",
                    "",
                    "Vel RMS",
                    f"{metrics.accuracy_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
                    f"{metrics.precision_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",
                    f"{metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}",

                    f"{metrics.balanced_accuracy_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}\n\n",
                    f"{metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions, pos_label=0):.2f}\n\n",
                    f"{metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions):.2f}\n\n",
                ],
            )

            #
            # Keeps an history, enabling the creation of a summary.
            #
            accuracies["clusterfix"].append(
                metrics.accuracy_score(
                    result_bufalo.predictions, result_rbfchain_predictions
                )
            )
            accuracies["vel_100"].append(
                metrics.accuracy_score(
                    result_vel100.predictions, result_rbfchain_predictions
                )
            )
            accuracies["vel_rms"].append(
                metrics.accuracy_score(
                    result_vel_rms.predictions, result_rbfchain_predictions
                )
            )

            precisions["clusterfix"].append(
                metrics.precision_score(
                    result_bufalo.predictions, result_rbfchain_predictions
                )
            )
            precisions["vel_100"].append(
                metrics.precision_score(
                    result_vel100.predictions, result_rbfchain_predictions
                )
            )
            precisions["vel_rms"].append(
                metrics.precision_score(
                    result_vel_rms.predictions, result_rbfchain_predictions
                )
            )

            recalls["clusterfix"].append(
                metrics.recall_score(
                    result_bufalo.predictions, result_rbfchain_predictions
                )
            )
            recalls["vel_100"].append(
                metrics.recall_score(
                    result_vel100.predictions, result_rbfchain_predictions
                )
            )
            recalls["vel_rms"].append(
                metrics.recall_score(
                    result_vel_rms.predictions, result_rbfchain_predictions
                )
            )


            balanced_accuracy["clusterfix"].append(
                metrics.balanced_accuracy_score(result_bufalo.predictions, result_rbfchain_predictions)
            )
            balanced_accuracy["vel_100"].append(
                metrics.balanced_accuracy_score(result_vel100.predictions, result_rbfchain_predictions)
            )
            balanced_accuracy["vel_rms"].append(
               metrics.balanced_accuracy_score(result_vel_rms.predictions, result_rbfchain_predictions)
            )

            sensivity["clusterfix"].append(
                metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions)
            )
            sensivity["vel_100"].append(
                metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions)
            )
            sensivity["vel_rms"].append(
                metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions)
            )

            specificity["clusterfix"].append(
                metrics.recall_score(result_bufalo.predictions, result_rbfchain_predictions, pos_label=0)
            )
            specificity["vel_100"].append(
                metrics.recall_score(result_vel100.predictions, result_rbfchain_predictions, pos_label=0)
            )
            specificity["vel_rms"].append(
                metrics.recall_score(result_vel_rms.predictions, result_rbfchain_predictions, pos_label=0)
            )

            # Save summary figure
            if os.path.exists(result_image_full_path):
                os.remove(result_image_full_path)

            plt.tight_layout(h_pad=1, w_pad=1)
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
            table, headers=headers, tablefmt="latex_booktabs", floatfmt=".2f"
        )
        fp.write(output_table)

    #
    # Create, persist and output summary tables
    #
    summary_headers = [
        "Algorithm",

        "Min. Accuracy",
        "Max. Accuracy",
        "Avg. Accuracy",
        "Std. Accuracy",

        "Min. Precision",
        "Max. Precision",
        "Avg. Precision",
        "Std. Precision",

        "Min. Recall",
        "Max. Recall",
        "Avg. Recall",
        "Std. Recall",


        "Min. Balanced Accuracy",
        "Max. Balanced Accuracy",
        "Avg. Balanced Accuracy",
        "Std. Balanced Accuracy",

        "Min. Specifity",
        "Max. Specifity",
        "Avg. Specifity",
        "Std. Specifity",

        "Min. Sensivity",
        "Max. Sensivity",
        "Avg. Sensivity",
        "Std. Sensivity",
    ]
    summary_table = [
        [
            "ClusterFix",
            np.min(accuracies["clusterfix"]),
            np.max(accuracies["clusterfix"]),
            np.mean(accuracies["clusterfix"]),
            np.std(accuracies["clusterfix"]),

            np.min(precisions["clusterfix"]),
            np.max(precisions["clusterfix"]),
            np.mean(precisions["clusterfix"]),
            np.std(precisions["clusterfix"]),

            np.min(recalls["clusterfix"]),
            np.max(recalls["clusterfix"]),
            np.mean(recalls["clusterfix"]),
            np.std(recalls["clusterfix"]),


            np.min(balanced_accuracy["clusterfix"]),
            np.max(balanced_accuracy["clusterfix"]),
            np.mean(balanced_accuracy["clusterfix"]),
            np.std(balanced_accuracy["clusterfix"]),

            np.min(specificity["clusterfix"]),
            np.max(specificity["clusterfix"]),
            np.mean(specificity["clusterfix"]),
            np.std(specificity["clusterfix"]),

            np.min(sensivity["clusterfix"]),
            np.max(sensivity["clusterfix"]),
            np.mean(sensivity["clusterfix"]),
            np.std(sensivity["clusterfix"]),
        ],
        [
            "Vel 100",
            np.min(accuracies["vel_100"]),
            np.max(accuracies["vel_100"]),
            np.mean(accuracies["vel_100"]),
            np.std(accuracies["vel_100"]),

            np.min(precisions["vel_100"]),
            np.max(precisions["vel_100"]),
            np.mean(precisions["vel_100"]),
            np.std(precisions["vel_100"]),

            np.min(recalls["vel_100"]),
            np.max(recalls["vel_100"]),
            np.mean(recalls["vel_100"]),
            np.std(recalls["vel_100"]),


            np.min(balanced_accuracy["vel_100"]),
            np.max(balanced_accuracy["vel_100"]),
            np.mean(balanced_accuracy["vel_100"]),
            np.std(balanced_accuracy["vel_100"]),

            np.min(specificity["vel_100"]),
            np.max(specificity["vel_100"]),
            np.mean(specificity["vel_100"]),
            np.std(specificity["vel_100"]),

            np.min(sensivity["vel_100"]),
            np.max(sensivity["vel_100"]),
            np.mean(sensivity["vel_100"]),
            np.std(sensivity["vel_100"]),
        ],
        [
            "Vel RMS",
            np.min(accuracies["vel_rms"]),
            np.max(accuracies["vel_rms"]),
            np.mean(accuracies["vel_rms"]),
            np.std(accuracies["vel_rms"]),

            np.min(precisions["vel_rms"]),
            np.max(precisions["vel_rms"]),
            np.mean(precisions["vel_rms"]),
            np.std(precisions["vel_rms"]),

            np.min(recalls["vel_rms"]),
            np.max(recalls["vel_rms"]),
            np.mean(recalls["vel_rms"]),
            np.std(recalls["vel_rms"]),


            np.min(balanced_accuracy["vel_rms"]),
            np.max(balanced_accuracy["vel_rms"]),
            np.mean(balanced_accuracy["vel_rms"]),
            np.std(balanced_accuracy["vel_rms"]),

            np.min(specificity["vel_rms"]),
            np.max(specificity["vel_rms"]),
            np.mean(specificity["vel_rms"]),
            np.std(specificity["vel_rms"]),

            np.min(sensivity["vel_rms"]),
            np.max(sensivity["vel_rms"]),
            np.mean(sensivity["vel_rms"]),
            np.std(sensivity["vel_rms"]),
        ],
        [
            "Avg",
            np.mean(
                [
                    np.min(accuracies["clusterfix"]),
                    np.min(accuracies["vel_100"]),
                    np.min(accuracies["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.max(accuracies["clusterfix"]),
                    np.max(accuracies["vel_100"]),
                    np.max(accuracies["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.mean(accuracies["clusterfix"]),
                    np.mean(accuracies["vel_100"]),
                    np.mean(accuracies["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.std(accuracies["clusterfix"]),
                    np.std(accuracies["vel_100"]),
                    np.std(accuracies["vel_rms"]),
                ]
            ),

            np.mean(
                [
                    np.min(precisions["clusterfix"]),
                    np.min(precisions["vel_100"]),
                    np.min(precisions["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.max(precisions["clusterfix"]),
                    np.max(precisions["vel_100"]),
                    np.max(precisions["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.mean(precisions["clusterfix"]),
                    np.mean(precisions["vel_100"]),
                    np.mean(precisions["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.std(precisions["clusterfix"]),
                    np.std(precisions["vel_100"]),
                    np.std(precisions["vel_rms"]),
                ]
            ),

            np.mean(
                [
                    np.min(recalls["clusterfix"]),
                    np.min(recalls["vel_100"]),
                    np.min(recalls["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.max(recalls["clusterfix"]),
                    np.max(recalls["vel_100"]),
                    np.max(recalls["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.mean(recalls["clusterfix"]),
                    np.mean(recalls["vel_100"]),
                    np.mean(recalls["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.std(recalls["clusterfix"]),
                    np.std(recalls["vel_100"]),
                    np.std(recalls["vel_rms"]),
                ]
            ),

            np.mean(
                [
                    np.min(balanced_accuracy["clusterfix"]),
                    np.min(balanced_accuracy["vel_100"]),
                    np.min(balanced_accuracy["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.max(balanced_accuracy["clusterfix"]),
                    np.max(balanced_accuracy["vel_100"]),
                    np.max(balanced_accuracy["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.mean(balanced_accuracy["clusterfix"]),
                    np.mean(balanced_accuracy["vel_100"]),
                    np.mean(balanced_accuracy["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.std(balanced_accuracy["clusterfix"]),
                    np.std(balanced_accuracy["vel_100"]),
                    np.std(balanced_accuracy["vel_rms"]),
                ]
            ),


            np.mean(
                [
                    np.min(specificity["clusterfix"]),
                    np.min(specificity["vel_100"]),
                    np.min(specificity["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.max(specificity["clusterfix"]),
                    np.max(specificity["vel_100"]),
                    np.max(specificity["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.mean(specificity["clusterfix"]),
                    np.mean(specificity["vel_100"]),
                    np.mean(specificity["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.std(specificity["clusterfix"]),
                    np.std(specificity["vel_100"]),
                    np.std(specificity["vel_rms"]),
                ]
            ),


            np.mean(
                [
                    np.min(sensivity["clusterfix"]),
                    np.min(sensivity["vel_100"]),
                    np.min(sensivity["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.max(sensivity["clusterfix"]),
                    np.max(sensivity["vel_100"]),
                    np.max(sensivity["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.mean(sensivity["clusterfix"]),
                    np.mean(sensivity["vel_100"]),
                    np.mean(sensivity["vel_rms"]),
                ]
            ),
            np.mean(
                [
                    np.std(sensivity["clusterfix"]),
                    np.std(sensivity["vel_100"]),
                    np.std(sensivity["vel_rms"]),
                ]
            ),
        ],
    ]

    with open(result_table_summary_full_path_txt, "w") as fp:
        output_table = tabulate.tabulate(
            summary_table, headers=summary_headers, tablefmt="grid", floatfmt=".2f"
        )
        fp.write(output_table)

    with open(result_table_summary_full_path_latex, "w") as fp:
        output_table = tabulate.tabulate(
            summary_table, headers=summary_headers, tablefmt="latex", floatfmt=".2f"
        )
        fp.write(output_table)

    with open(result_pickle_full_path, "wb") as fp:
        result = {
            "table": table,
            "accuracies": accuracies,
            "precisions": precisions,
            "recalls": recalls,
        }
        pickle.dump(result, fp)

    print(f"Everything ok \N{hot beverage}")

if __name__ == "__main__":
    main()
