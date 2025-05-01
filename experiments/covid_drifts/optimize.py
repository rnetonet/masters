import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import optuna
import pandas as pd

from rbf import RBF

DATASET = "covid_saude_gov_br.csv"

df = pd.read_csv(DATASET, delimiter=";")
data = df.loc[df["municipio"] == "Salvador", ["municipio", "data", "casosNovos"]]
smoothed_ts = data["casosNovos"].rolling(window=15).mean()

def objective(trial):
    sigma = trial.suggest_float('sigma', 0.005, 0.1, step=0.001)
    lambda_ = trial.suggest_float('lambda_', 0.5, 1, step=0.05)
    alpha = trial.suggest_float('alpha', 0.025, 0.25, step=0.05)
    delta = trial.suggest_float('delta', 0.5, 1, step=0.05)

    rbf = RBF(sigma, lambda_, alpha, delta)
    for input_data in smoothed_ts:
        rbf.add_element(input_data)

    return len(rbf.centers)

study_name = "covid_saude_gov_br"
storage_name = "sqlite:///{}.db".format(study_name)
study = optuna.create_study(study_name=study_name, storage=storage_name)
study.optimize(objective, n_trials=1_000_000)

print(study.best_params)