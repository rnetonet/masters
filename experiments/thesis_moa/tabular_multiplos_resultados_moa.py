# tabular_multiplos_resultados_moa.py
import os
import os.path
import re
import sys

import pandas as pd

# Mappings
map_filename_algorithm = {
    "rbfchain": "RBFChain",
    "adwin": "ADWIN",
    "cusum": "CUSUM",
    "ddm": "DDM",
    "eddm": "EDDM",
    "ewma": "EWMA",
    "hddma": "HDDMA",
    "ph": "PageHinkley",
    "seqdrift1": "SeqDrift1",
}

map_path_dataset = {
    "nochange": "Sem Mudança",
    "abrupt": "Mudança Abrupta",
    "gradual": "Mudança Gradual",
    "incremental": "Mudança Incremental",
}

output_row_template = {
    "Algoritmo": None,
    "TP": None,
    "MR": None,
    "VP": None,
    "FP": None,
    "ATR": None,
}

output_table = {
    filename: output_row_template.copy() for filename in map_filename_algorithm.keys()
}

# Params
path = sys.argv[1]
files = os.listdir(path)

# Dataset used
dataset = None
dataset_key = None

for key in map_path_dataset:
    if key in path:
        dataset_key = key
        dataset = map_path_dataset[dataset_key]
        break

# Processing
for file in files:
    file_absolute_path = os.path.abspath(os.path.join(path, file))
    filename = file.replace(".csv", "")

    algorithm = map_filename_algorithm[filename]

    df = pd.read_csv(file_absolute_path)

    output_table_row = output_table[filename]

    output_table_row["Algoritmo"] = algorithm
    output_table_row["TP"] = float(
        df.iloc[-1]["evaluation time (cpu seconds)"]
        / df["evaluation time (cpu seconds)"].size
    )
    output_table_row["MR"] = int(df.iloc[-1]["true changes"])
    output_table_row["VP"] = int(df.iloc[-1]["detected changes"])

    if (
        output_table_row["VP"]
        - output_table_row["MR"]
        > 0
    ):
        output_table_row["FP"] = (
            output_table_row["VP"]
            - output_table_row["MR"]
        )
    else:
        output_table_row["FP"] = 0

    try:
        output_table_row["ATR"] = float(
            df.iloc[-1]["delay detection (average)"]
        )
    except ValueError:
        output_table_row["ATR"] = 0

# Printing
print("*" * 80)
print(f"*** {dataset_key:^72} ***")
print("*" * 80)
print()
print()

print("\\toprule")

headers = []
for header in output_row_template.keys():
    headers.append(f"{header:<22}")

print(" & ".join(headers), end=" \\\\ ")
print()

print("\\midrule")
for filename in output_table:
    output_table_row = output_table[filename]
    print(f"{output_table_row['Algoritmo']:<22}", end=" & ")
    print(f"{output_table_row['TP']:<22.3f}", end=" & ")
    print(f"{output_table_row['MR']:<22}", end=" & ")
    print(f"{output_table_row['VP']:<22}", end=" & ")
    print(f"{output_table_row['FP']:<22}", end=" & ")
    print(f"{output_table_row['ATR']:<22.2f}", end=" \\\\ ")
    print()
print("\\bottomrule")
