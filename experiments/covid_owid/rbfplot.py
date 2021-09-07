import io
import os
import webbrowser

import matplotlib.image as plt_img
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import imageio


class RBFPlot:
    def __init__(self, suptitle="RBF", step=50):
        self.suptitle = suptitle
        self.step = 50

        self.data = []
        self.data_change_history = []

        self.warning_zone_history = []
        self.concept_drift_history = []

        self.markov_history = []
        self.markov_plot_history = []

    def update(self, input_data, change, rbf):
        self.data.append(input_data)
        self.data_change_history.append(change)

        self.warning_zone_history.append(rbf.detected_warning_zone())
        self.concept_drift_history.append(rbf.detected_change())
        self.markov_history.append(rbf.markov.system.copy())

        if not self.markov_plot_history or len(self.data) % self.step == 0:
            raw_img = io.BytesIO(rbf.markov.to_graphviz().pipe(format="png"))
            img = plt_img.imread(raw_img, format="png")
            self.markov_plot_history.append(img)
        else:
            self.markov_plot_history.append(self.markov_plot_history[-1])

    def plot(self, instant_in_time):
        # Setup
        font = {"family": "monospace", "size": 8}
        plt.rc("font", **font)
        plt.rc("text", usetex=True)
        plt.rc("font", family="serif")

        data = self.data[:instant_in_time]

        fig, axes = plt.subplots(nrows=2, dpi=600)
        stream, markov = axes

        fig.suptitle(self.suptitle, fontsize=12)
        fig.subplots_adjust(hspace=0.2, wspace=0.2)

        stream.grid(False)
        stream.autoscale(True)

        markov.grid(False)
        markov.autoscale(True)

        for index, _ in enumerate(data):
            if self.data_change_history[index]:
                stream.axvline(index, color="g", ls="-", linewidth=1, alpha=0.25)

            if self.warning_zone_history[index]:
                stream.axvline(index + 5, color="y", ls="--", linewidth=2, alpha=0.25)

            if self.concept_drift_history[index]:
                stream.axvline(index + 5, color="b", ls="--", linewidth=1)

        stream.plot(range(0, len(data)), data, color="k", linestyle="-", linewidth=0.25)

        # Plot the markov
        try:
            markov_figure = self.markov_plot_history[instant_in_time]
        except IndexError:
            markov_figure = self.markov_plot_history[-1]

        markov.imshow(markov_figure, aspect="equal")

        # Legend
        custom_legends = [
            Line2D([0], [0], color="#D3D3D3", linestyle="-", linewidth=0.25),
            Line2D([0], [0], color="g", ls="-", linewidth=1),
            Line2D([0], [0], color="b", ls="--", linewidth=1),
            Line2D([0], [0], color="y", ls="--", linewidth=1),
        ]

        stream.legend(
            custom_legends,
            [
                "Fluxo de Dados",
                "Mudança de Conceito",
                "Mudança Detectada",
                "Zona de alerta",
            ],
            ncol=2,
            borderaxespad=0,
            loc="best",
        )

        # Returna image bytes of canvas
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype="uint8")
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        plt.close(fig)

        return image

    def plot_animation(self):
        length = len(self.data)

        filename = os.path.join(os.getcwd(), self.suptitle + ".mp4")
        writer = imageio.get_writer(filename, fps=1, quality=5)

        for instant_in_time in range(0, length, self.step):
            writer.append_data(self.plot(instant_in_time))

        writer.close()
        webbrowser.open(filename)
