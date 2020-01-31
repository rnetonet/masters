import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from data_reader import DataReader

class DataOverviewPlot:
    def __init__(self, dataset: DataReader):
        self.dataset = dataset

    def plot(self):
        fig = plt.figure()
        fig.gca().set_title(self.__class__.__name__)

        gs = fig.add_gridspec(nrows=3, ncols=2)

        x_plot = fig.add_subplot(gs[0, 0])
        y_plot = fig.add_subplot(gs[0, 1])
        points_plot = fig.add_subplot(gs[1, :])
        velocity_plot = fig.add_subplot(gs[2, 0])
        acc_plot = fig.add_subplot(gs[2, 1])

        fig.subplots_adjust(hspace=0.2, wspace=0.2)

        x_plot.grid(False)
        x_plot.autoscale(True)
        x_plot.set_title("x")

        y_plot.grid(False)
        y_plot.autoscale(True)
        y_plot.set_title("y")

        points_plot.grid(False)
        points_plot.autoscale(True)
        points_plot.set_title("(x, y)")

        velocity_plot.grid(False)
        velocity_plot.autoscale(True)
        velocity_plot.set_title("vel")

        acc_plot.grid(False)
        acc_plot.autoscale(True)
        acc_plot.set_title("acc")

        x_plot.plot(self.dataset.x)
        y_plot.plot(self.dataset.y)
        points_plot.plot(self.dataset.x, self.dataset.y, "bo")
        velocity_plot.plot(self.dataset.vel)
        acc_plot.plot(self.dataset.acc)

        plt.show(block=True)


class TrajectoryPlot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def plot(self):
        fig = plt.figure()
        fig.gca().set_title(self.__class__.__name__)

        custom_legends = [
            Line2D([0], [0], color=(0, 1, 0), ls="-", linewidth=1),
            Line2D([0], [0], color="r", ls="-", linewidth=1, alpha=0.5),
        ]
        fig.legend(
            custom_legends,
            ["Saccades", "Fixations"],
            ncol=1,
            borderaxespad=0,
            loc="lower center",
        )

        # Trajectory
        plt.plot(self.x, self.y, "-", color=(0, 1, 0), linewidth=0.25)
        plt.show(block=False)


class FixationsPlot:
    def __init__(self, x, y, fixations_indexes, title=None, block=True):
        self.x = x
        self.y = y
        self.fixations_indexes = fixations_indexes
        self.title = title
        self.block = block

    def plot_in_ax(self, ax):
        if not self.title:
            ax.set_title(self.__class__.__name__)
        else:
            ax.set_title(self.title)

        custom_legends = [
            Line2D([0], [0], color=(0, 1, 0), ls="-", linewidth=1),
            Line2D([0], [0], color="r", ls="-", linewidth=1, alpha=0.5),
        ]
        ax.legend(
            custom_legends,
            ["Saccades", "Fixations"],
            ncol=1,
            borderaxespad=0,
            loc="best",
        )

        # Trajectory
        ax.plot(self.x, self.y, "-", color=(0, 1, 0), linewidth=0.25)

        # Fixations
        fixations_x, fixations_y = [], []
        for index in self.fixations_indexes:
            fixations_x.append(self.x[index])
            fixations_y.append(self.y[index])

        ax.plot(
            fixations_x,
            fixations_y,
            linestyle="",
            marker="o",
            markersize=1,
            alpha=0.25,
            color="red",
        )

    def plot_to_file(self, filename, **kwargs):
        fig = plt.figure()
        self.plot_in_ax(fig.gca())
        fig.savefig(filename, **kwargs)
        plt.close(fig)
