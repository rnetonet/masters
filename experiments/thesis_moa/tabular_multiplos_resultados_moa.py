# tabular_multiplos_resultados_moa.py
import os
import os.path
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
    "Tempo de processamento": None,
    "Mudanças Existentes": None,
    "Mudanças Detectadas": None,
    "Falso-positivos": None,
    "Atraso de Detecção": None,
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
    output_table_row["Tempo de processamento"] = df.iloc[-1]["evaluation time (cpu seconds)"] / df["evaluation time (cpu seconds)"].size
    output_table_row["Mudanças Existentes"] = df.iloc[-1]["true changes"]
    output_table_row["Mudanças Detectadas"] = df.iloc[-1]["detected changes"]
    output_table_row["Falso-positivos"] = output_table_row["Mudanças Detectadas"] - output_table_row["Mudanças Existentes"] if output_table_row["Mudanças Detectadas"] - output_table_row["Mudanças Existentes"] > 0 else 0
    output_table_row["Atraso de Detecção"] = df.iloc[-1]["delay detection (average)"]

# Printing
print(f"{dataset_key:^80}")
for table in output_table:
    print(table)
