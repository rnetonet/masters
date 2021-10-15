import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from matplotlib.lines import Line2D

from rbf import RBF


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

df.fillna(method="ffill", inplace=True)

fig, ax_left = plt.subplots()
ax_right = ax_left.twinx()
ax_third = ax_left.twinx()

ax_left.plot(
    df["date"],
    df["people_vaccinated"],
    color="navy",
    linestyle="-",
    linewidth=0.75,
)

ax_left.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))

ax_right.plot(
    df["date"],
    df["new_deaths"],
    color="red",
    linestyle="-",
    linewidth=0.75,
)

ax_third.plot(
    df["date"],
    df["new_cases"],
    color="lightgreen",
    linestyle="-",
    linewidth=0.75,
)

xticks = []
rbf = RBF(**{"sigma": 0.01, "lambda_": 0.5, "alpha": 0.5, "delta": 1.0})

for index, row in df.iterrows():
    date = df["date"][index]
    value = row["new_deaths"]

    rbf.add_element(value)

    print(f"{rbf.concept_center=}, {date=}")
    rbf.markov.to_png(date + "_markov.png")

    if rbf.in_concept_change:
        ax_left.axvline(date, color="orange", ls="--", linewidth=0.75)
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

plt.suptitle("Vaccinated X Deaths")
plt.title(f"{len(df)=}, {len(rbf.centers)=}")

plt.show()

remove_generated_pngs()