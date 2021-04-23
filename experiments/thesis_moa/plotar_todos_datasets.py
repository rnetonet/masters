import sys
import os
import os.path
import glob
import matplotlib

import matplotlib.pyplot as plt
plt.style.use('seaborn-white')

import pandas as pd
from scipy.io import arff


class DatasetPlotter:
    _filename_settings_map = {
        "abrupt.arff": {"name": "Abrupt", "subplot": {"row": 0, "col": 0}},
        "gradual.arff": {"name": "Gradual", "subplot": {"row": 0, "col": 1}},
        "incremental.arff": {
            "name": "Incremental",
            "subplot": {"row": 1, "col": 0},
        },
        "nochange.arff": {"name": "No Change", "subplot": {"row": 1, "col": 1}},
    }

    def __init__(self, path):
        self.base_path = os.path.abspath(path)
        self.datasets = glob.glob(os.path.join(os.getcwd(), "datasets/") + "*.arff")

    def read_arff_file(self, arff_file_name):
        full_arff_path = os.path.join(self.base_path, arff_file_name)

        arff_file = arff.loadarff(full_arff_path)
        arff_data = arff_file[0]

        df = pd.DataFrame(arff_data)

        return df

    def plot(self):
        self._setup_figure()

        for arff_file_name in self.datasets:
            self._setup_ax(arff_file_name)

        plt.show()
        self.fig.savefig("conjuntos_dados_sinteticos" + ".png", bbox_inches='tight', pad_inches=0.1)

    def _setup_figure(self):
        # font = {"family": "monospace", "size": 9}
        # plt.rc("font", **font)
        # plt.rc("text", usetex=True)
        # plt.rc("font", family="serif")

        self.fig, self.axs = plt.subplots(2, 2)
        self.fig.subplots_adjust(hspace=0.3, wspace=0.1)

        for ax in self.axs.flat:
            ax.set_xlim(0, 2500)
            ax.set_ylim(0, 1.1)

    def _setup_ax(self, arff_file_name):
        arff_file_name = os.path.basename(arff_file_name)
        settings = self._filename_settings_map[arff_file_name]
        subplot = settings["subplot"]

        ax = self.axs[subplot["row"]][subplot["col"]]
        ax.set_title(settings["name"])

        arff_file_df = self.read_arff_file(arff_file_name)

        ax.plot(arff_file_df["input"], color="k", linestyle="-", linewidth=0.1)
        ax.plot(arff_file_df["change"], color="r", linestyle="--", linewidth=0.2)


if __name__ == "__main__":
    path = "datasets/"
    if len(sys.argv) >= 2:
        path = sys.argv[1]

    dataset_plotter = DatasetPlotter(path)
    dataset_plotter.plot()
