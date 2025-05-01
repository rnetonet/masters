import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from matplotlib.lines import Line2D

from rbf import RBF
from prettyprinter import pprint

def remove_generated_pngs():
    # Remove all pngs
    import glob
    import os

    for file in glob.glob("*.png"):
        os.remove(file)

remove_generated_pngs()

# Setup plots
df = pd.read_csv("owid-covid-data.csv")

df = df.loc[df["location"] == "Brazil"]

df["weekly_new_deaths_mean"] = df["new_deaths"].rolling(window=7).mean()
df["weekly_new_cases_mean"] = df["new_cases"].rolling(window=7).mean()

df["weekly_new_deaths_mean"] = df["weekly_new_deaths_mean"].fillna(method="ffill")
df["weekly_new_cases_mean"] = df["weekly_new_cases_mean"].fillna(method="ffill")

df.fillna(method="ffill", inplace=True)
df = df[::7]

fig, ax_left = plt.subplots()
ax_right = ax_left.twinx()
ax_third = ax_left.twinx()

ax_left.plot(
    df["date"],
    df["people_vaccinated"],
    color="navy",
    linestyle="-",
    linewidth=1.00,
)

ax_left.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))

ax_right.plot(
    df["date"],
    df["weekly_new_deaths_mean"],
    color="red",
    linestyle="-",
    linewidth=1.00,
)

ax_third.plot(
    df["date"],
    df["weekly_new_cases_mean"],
    color="lightgreen",
    linestyle="-",
    linewidth=1.00,
)

xticks = []
# rbf = RBF(**{"sigma": 0.01, "lambda_": 0.5, "alpha": 0.5, "delta": 1.0})
rbf = RBF(
    **{'sigma': 0.01, 'lambda_': 0.55, 'alpha': 0.35, 'delta': 0.75}
)

for index, row in df.iterrows():
    date = df["date"][index]
    value = row["weekly_new_deaths_mean"]

    rbf.add_element(value)

    rbf.markov.to_png(date + "_markov.png")
    
    print("="*80)
    pprint(f"{date=}, {rbf.concept_center=}")
    # pprint(rbf.markov.system)
    print("="*80)

    if rbf.in_concept_change:
        ax_left.axvline(date, color="orange", ls="--", linewidth=1.00)
        xticks.append(date)


ax_left.tick_params(axis="x", labelrotation=90)
ax_right.tick_params(axis="x", labelrotation=90)

ax_left.tick_params(axis="y", colors="navy")
ax_right.tick_params(axis="y", colors="red")

ax_third.tick_params(axis="y", colors="lightgreen")
ax_third.get_yaxis().set_visible(False)

ax_right.set_xticks(xticks)

for tick in ax_right.xaxis.get_minor_ticks():
    tick.label1.set_horizontalalignment("right")

plt.gcf().subplots_adjust(bottom=0.15)

custom_legends = [
    Line2D([0], [0], color="navy", linestyle="-", linewidth=2),
    Line2D([0], [0], color="lightgreen", ls="-", linewidth=2),
    Line2D([0], [0], color="red", ls="-", linewidth=2),
    Line2D([0], [0], color="orange", ls="--", linewidth=2),
]
legend = plt.legend(
    custom_legends,
    [
        "People Vaccinated",
        "Cases",
        "Deaths",
        f"Concept Drift (Deaths)",
    ],
    ncol=2,
    borderaxespad=0,
    loc="upper left",
)
legend.get_frame().set_alpha(None)

plt.suptitle("Vaccinated / Cases / Deaths")
# plt.title(f"{len(df)=}, {len(rbf.centers)=}")

plt.show()

remove_generated_pngs()