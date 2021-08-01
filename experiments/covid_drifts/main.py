import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from matplotlib.lines import Line2D

from rbf import RBF

DATASET_CASOS = 'dados_covid_sp.csv.gz'
DATASET_LEITOS = 'dados_covid_sp_leitos.csv.gz'

df_casos = pd.read_csv(DATASET_CASOS, delimiter=';', compression='gzip')
df_leitos = pd.read_csv(DATASET_LEITOS, delimiter=';', compression='gzip')

df_casos = df_casos.loc[
    df_casos['nome_munic'] == 'São Paulo',
    ['nome_munic', 'datahora', 'casos_novos', 'obitos_novos', 'semana_epidem'],
]
df_casos['media_semanal_casos_novos'] = (
    df_casos['casos_novos'].rolling(window=7).mean()
)

df_leitos = df_leitos.loc[
    df_leitos['nome_drs'] == 'DRS 01 Grande São Paulo',
    ['nome_drs', 'datahora', 'ocupacao_leitos'],
]
df_leitos['ocupacao_leitos'] = df_leitos['ocupacao_leitos'].apply(
    lambda v: float(v.replace(',', '.'))
)
df_leitos['media_semanal_ocupacao_leitos'] = (
    df_leitos['ocupacao_leitos'].rolling(window=7).mean()
)

fig, ax_left = plt.subplots()
ax_right = ax_left.twinx()

ax_left.plot(
    df_casos['datahora'],
    df_casos['media_semanal_casos_novos'],
    color='navy',
    linestyle='-',
    linewidth=0.75,
)

ax_right.plot(
    df_leitos['datahora'],
    df_leitos['media_semanal_ocupacao_leitos'],
    color='red',
    linestyle='-',
    linewidth=0.75,
)
ax_right.yaxis.set_major_formatter(mtick.PercentFormatter())

xticks = []

rbf = RBF(**{'sigma': 0.001, 'lambda_': 0.85, 'alpha': 0.13, 'delta': 1})

for index, row in df_casos.iterrows():
    input_data = df_casos['datahora'][index]

    rbf.add_element(row['media_semanal_casos_novos'])

    if rbf.in_concept_change:
        ax_left.axvline(
            input_data, color='green', ls='--', linewidth=0.75
        )
        xticks.append(df_casos['datahora'][index])

        rbf.markov.to_png()

ax_left.tick_params(axis='x', labelrotation=90)
ax_right.tick_params(axis='x', labelrotation=90)

ax_left.tick_params(axis='y', colors='navy')
ax_right.tick_params(axis='y', colors='red')

ax_right.set_xticks(xticks)

for tick in ax_right.xaxis.get_minor_ticks():
    tick.label1.set_horizontalalignment('right')

plt.gcf().subplots_adjust(bottom=0.15)

custom_legends = [
    Line2D([0], [0], color='navy', linestyle='-', linewidth=1),
    Line2D([0], [0], color='red', ls='-', linewidth=1),
    Line2D([0], [0], color='green', ls='--', linewidth=1),
]
legend = plt.legend(
    custom_legends,
    ['Daily Cases (7d window mean)', 'ICUs occupation (%)', 'Concept Drift'],
    ncol=2,
    borderaxespad=0,
    loc='upper left',
)
legend.get_frame().set_alpha(None)

plt.show()
