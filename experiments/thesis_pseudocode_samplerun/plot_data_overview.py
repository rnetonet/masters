import matplotlib.pyplot as plt


def plot_overview(x_filt, y_filt, vel_filt, acc_filt):
    """
    Plot an overview of the data.
    """

    # Creating the grid spec
    fig = plt.figure()
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

    x_plot.plot(x_filt)
    y_plot.plot(y_filt)
    points_plot.plot(x_filt, y_filt, "bo")
    velocity_plot.plot(vel_filt)
    acc_plot.plot(acc_filt)

    plt.show(block=True)
