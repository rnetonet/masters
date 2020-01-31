import argparse
import os.path

import optuna
from optuna.samplers import RandomSampler
from sklearn import metrics

from data_reader import DataReader
from rbfchain import RBFChain
from result_reader import ResultReader

#
# Setup
#
parser = argparse.ArgumentParser()
parser.add_argument("dataset_sample_path")
args = parser.parse_args()

dataset_sample_path = os.path.abspath(args.dataset_sample_path)
dataset = DataReader(dataset_sample_path)

bufalo_results_path = dataset_sample_path.replace(
    "-Export-ReplaceEyeOut.txt", "-ResultBufalo.txt"
)
result_bufalo = ResultReader(bufalo_results_path)

#
# Optuna objective function
#
def objective(trial):
    # Get parameters suggestions
    sigma = trial.suggest_discrete_uniform("sigma", 0.001, 0.1, 0.001)
    lambda_ = trial.suggest_discrete_uniform("lambda_", 0.25, 1.0, 0.01)
    alpha = trial.suggest_discrete_uniform("alpha", 0.01, 1.0, 0.01)
    delta = trial.suggest_discrete_uniform("delta", 0.25, 1.0, 0.01)

    #
    # Process dataset using RBFChain
    #
    rbfchain = RBFChain(sigma=sigma, lambda_=lambda_, alpha=alpha, delta=delta)
    rbfchain_predictions = [
        1 if rbfchain.add_element(input_data) >= rbfchain.delta else 0
        for input_data in dataset.distances
    ]

    # for input_data in dataset.distances:
    #     probability = rbfchain.add_element(input_data)

    #     if probability >= rbfchain.delta:
    #         rbfchain_predictions.append(1)
    #     else:
    #         rbfchain_predictions.append(0)

    # The study tries to minimize a value
    accuracy = metrics.accuracy_score(result_bufalo.predictions, rbfchain_predictions)

    print(
        f"\n{trial.number=}, {sigma=:.2f}, {lambda_=:.2f}, {alpha=:.2f}, {delta=:.2f} -> {accuracy=:.3f}\n"
    )

    return accuracy


study = optuna.create_study(sampler=RandomSampler(), direction="maximize")
study.optimize(objective, n_jobs=-1)
