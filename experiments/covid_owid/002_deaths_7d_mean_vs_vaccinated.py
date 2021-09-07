import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from matplotlib.lines import Line2D

from rbf import RBF

df = pd.read_csv("owid-covid-data.csv")

df = df.loc[df["location"] == "Brazil"]
df = df.dropna(subset=("new_deaths",))
df = df.fillna(0)
df["weekly_new_deaths_mean"] = df["new_deaths"].rolling(window=7).mean()
df = df[::7]

fig, ax_left = plt.subplots()
ax_right = ax_left.twinx()

ax_left.plot(
    df["date"],
    df["people_vaccinated"],
    color="navy",
    linestyle="-",
    linewidth=0.75,
)

ax_left.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
# ax_left.ticklabel_format(useOffset=False, style="plain", axis="y")

ax_right.plot(
    df["date"],
    df["weekly_new_deaths_mean"],
    color="red",
    linestyle="-",
    linewidth=0.75,
)

xticks = []
rbf = RBF(**{"sigma": 0.01, "lambda_": 0.5, "alpha": 0.5, "delta": 1.0})

for index, row in df.iterrows():
    input_data = df["date"][index]

    rbf.add_element(row["weekly_new_deaths_mean"])

    if rbf.in_concept_change:
        ax_left.axvline(input_data, color="green", ls="--", linewidth=0.75)
        xticks.append(df["date"][index])

        rbf.markov.to_png()


ax_left.tick_params(axis="x", labelrotation=90)
ax_right.tick_params(axis="x", labelrotation=90)

ax_left.tick_params(axis="y", colors="navy")
ax_right.tick_params(axis="y", colors="red")

ax_right.set_xticks(xticks)

for tick in ax_right.xaxis.get_minor_ticks():
    tick.label1.set_horizontalalignment("right")

plt.gcf().subplots_adjust(bottom=0.15)

custom_legends = [
    Line2D([0], [0], color="navy", linestyle="-", linewidth=1),
    Line2D([0], [0], color="red", ls="-", linewidth=1),
    Line2D([0], [0], color="green", ls="--", linewidth=1),
]
legend = plt.legend(
    custom_legends,
    ["People Vaccinated", "Deaths (7d window mean)", f"Concept Drift"],
    ncol=2,
    borderaxespad=0,
    loc="upper left",
)
legend.get_frame().set_alpha(None)

plt.suptitle("Vaccinated X Deaths (7d window mean)")
plt.title(f"{len(df)=}, {len(rbf.centers)=}")

plt.show()
