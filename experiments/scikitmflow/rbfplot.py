import os
import os.path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D


class RBFPlot:
    def __init__(self, suptitle="RBF"):
        self.suptitle = suptitle

        self.data = []
        self.data_change_history = []
        self.warning_zone_history = []
        self.concept_drift_history = []
        self.markov_history = []

    def update(self, input_data, change, rbf):
        self.data.append(input_data)
        self.data_change_history.append(change)

        self.warning_zone_history.append(rbf.detected_warning_zone())
        self.concept_drift_history.append(rbf.detected_change())
        self.markov_history.append(rbf.markov.system.copy())

    def plot(self):
        # Setup
        font = {"family": "monospace", "size": 8}
        plt.rc("font", **font)
        plt.rc("text", usetex=True)
        plt.rc("font", family="serif")

        fig = plt.figure()
        fig.suptitle(self.suptitle, fontsize=12)
        fig.subplots_adjust(hspace=0.2, wspace=0.2)

        ax = fig.gca()
        ax.grid(False)
        ax.autoscale(True)
        ax.set_xlim(0, 2500)
        ax.set_ylim(0, 1)

        for index, _ in enumerate(self.data):
            if self.data_change_history[index]:
                ax.axvline(index - 25, color="g", ls="-", linewidth=1)

            if self.warning_zone_history[index]:
                ax.axvline(index + 25, color="y", ls="--", linewidth=0.1)

            if self.concept_drift_history[index]:
                ax.axvline(index + 25, color="b", ls="--", linewidth=1)
                print(self.markov_history[index])

        ax.plot(
            range(0, len(self.data)),
            self.data,
            color="k",
            #color="#D3D3D3",
            linestyle="-",
            linewidth=0.25,
        )

        # Legend
        custom_legends = [
            Line2D([0], [0], color="#D3D3D3", linestyle="-", linewidth=0.25),
            Line2D([0], [0], color="g", ls="-", linewidth=1),
            Line2D([0], [0], color="b", ls="--", linewidth=1),
            Line2D([0], [0], color="y", ls="--", linewidth=1),
        ]

        fig.legend(
            custom_legends,
            [
                "Fluxo de Dados",
                "Mudança de Conceito",
                "Mudança Detectada",
                "Zona de alerta",
            ],
            ncol=2,
            borderaxespad=0,
            loc="lower center",
        )

        # Showing and saving
        plt.show()
