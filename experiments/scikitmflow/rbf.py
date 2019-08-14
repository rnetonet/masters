import math

from graphviz import Digraph
from skmultiflow.drift_detection.base_drift_detector import BaseDriftDetector


class MarkovChain:
    def __init__(self):
        self.system = {}

    def add(self, origin, destination, alpha):
        if origin not in self.system:
            self.system[origin] = {}

        if destination not in self.system[origin]:
            self.system[origin][destination] = 0.0

        for _destination in self.system[origin].keys():
            if math.isclose(_destination, destination):
                new_probability = self.system[origin][_destination] + alpha
                self.system[origin][_destination] = (
                    new_probability if new_probability <= 1 else 1
                )
            else:
                factor_to_decrease = alpha / (len(self.system[origin]) - 1)
                if self.system[origin][_destination] >= factor_to_decrease:
                    self.system[origin][_destination] -= factor_to_decrease


    def to_graphviz(self, output_filename):
        dot = Digraph(comment="RBF")

        dot.attr("node", fontsize="8")
        dot.attr("edge", fontsize="8")
        dot.attr("edge", labelfloat="false")

        # nodes
        for origin in self.system.keys():
            dot.node(str(origin))

        # edges
        for origin in self.system.keys():
            for destination in self.system[origin].keys():
                dot.edge(
                    str(origin),
                    str(destination),
                    constraint="false",
                    label=str(self.system[origin][destination]),
                )

        print(dot.source)
        dot.render("markov.gv", view=True)


class RBF(BaseDriftDetector):
    """ Radial Basis Functions - Drift Detection Method.

    Parameters
    ----------
    sigma: float (default=2)
        Delimits the Gaussian radius.

    lambda_: float (default=0.5)
        Minimum threshold.

    alpha: float (default=0.25)
        Value to increase the probability in the Markov Chain.

    delta: float (default=1.0)
        Minimum threshold to consider the probability as a Concept Drift indication.
    """

    def __init__(self, sigma=2, lambda_=0.5, alpha=0.25, delta=1.0):
        super().__init__()
        self.sigma = sigma
        self.lambda_ = lambda_
        self.alpha = alpha
        self.delta = delta

        self.actual_center = None
        self.centers = []
        self.sample_count = 0

        self.markov = MarkovChain()

        self.reset()

    def reset(self):
        """ reset

        Resets the change detector parameters.

        """
        super().reset()
        self.sample_count = 1
        # Reset or not the markov
        # self.markov = MarkovChain()

    def add_element(self, input_data):
        """ Add a new element to the statistics

        Parameters
        ----------
        prediction: float
        """
        self.in_warning_zone = False

        if self.in_concept_change:
            self.reset()

        self.sample_count += 1

        activation = 0.0
        activation_lambda = self.lambda_
        distance = 0.0
        activated_center = None

        for center in self.centers:
            distance = math.sqrt(math.pow(input_data - center, 2.0))
            activation = math.exp(-math.pow(self.sigma * distance, 2))

            if activation >= activation_lambda:
                activated_center = center
                activation_lambda = activation

        if not activated_center:
            self.centers.append(input_data)
            activated_center = input_data

        if activated_center != self.actual_center:
            if self.actual_center is None:
                self.actual_center = activated_center

                self.markov.add(self.actual_center, activated_center, self.alpha)
            else:
                self.markov.add(self.actual_center, activated_center, self.alpha)
                probability = self.markov.system[self.actual_center][activated_center]

                self.actual_center = activated_center

                if probability >= self.delta:
                    self.in_concept_change = True
                else:
                    self.in_warning_zone = True
