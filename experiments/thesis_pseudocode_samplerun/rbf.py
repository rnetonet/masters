from decimal import Decimal
import math

from graphviz import Digraph
from skmultiflow.drift_detection.base_drift_detector import BaseDriftDetector


class MarkovChain:
    def __init__(self):
        self.system = {}

    def get_probability(self, origin, destination):
        if not isinstance(origin, str):
            origin = f"{origin:.2f}"
        if not isinstance(destination, str):
            destination = f"{destination:.2f}"
        return self.system[origin].get(destination, 0)

    def update(self, origin, destination, alpha):
        origin = f"{origin:.2f}"
        destination = f"{destination:.2f}"

        if not self.system.get(origin):
            self.system[origin] = {}

        if not self.system[origin].get(destination):
            self.system[origin][destination] = 0.0

        # Increment
        self.system[origin][destination] += alpha

        # Decrement
        if len(self.system[origin]) > 1:
            reduction_factor = alpha / (len(self.system[origin]) - 1)
            for possible_destination in self.system[origin]:
                if possible_destination != destination:
                    self.system[origin][possible_destination] -= reduction_factor

        # Adjust
        for possible_destination in self.system[origin]:
            if self.system[origin][possible_destination] > 1:
                self.system[origin][possible_destination] = 1
            elif self.system[origin][possible_destination] < 0:
                self.system[origin][possible_destination] = 0

        return self.system[origin][destination]

    def to_graphviz(self):
        dot = Digraph(comment="RBF")

        dot.attr(dpi="100")

        dot.attr("node", fontsize="8")
        dot.attr("edge", fontsize="8")
        dot.attr("edge", labelfloat="false")

        # nodes
        for origin in self.system.keys():
            dot.node(origin)

        # edges
        for origin in self.system.keys():
            for destination in self.system[origin].keys():
                dot.edge(
                    origin,
                    destination,
                    constraint="false",
                    label=format(self.system[origin][destination], ".2f"),
                )

        return dot

    def to_png(self, filename="markov"):
        dot = self.to_graphviz()
        dot.format = "png"
        return dot.render(filename)


class RBF(BaseDriftDetector):
    """ Radial Basis Functions - Drift Detection Method.

    Parameters
    ----------
    sigma: float (default=2)
        Delimits the Gaussian radius.

    lambda_: float (default=0.5)
        Minimum threshold to activate a center.

    alpha: float (default=0.25)
        Probability increase factor in Markov Chain.

    delta: float (default=1.0)
        Minimum threshold to consider probability in the Markov Chain as a
        Concept Drift indication.
    """

    def __init__(self, sigma=2, lambda_=0.5, alpha=0.25, delta=1.0):
        super().__init__()
        self.sigma = sigma
        self.lambda_ = lambda_
        self.alpha = alpha
        self.delta = delta

        self.centers = []
        self.sample_count = 0
        self.activated_center = None
        self.concept_center = None

        self.markov = MarkovChain()

        self.reset()

    def reset(self):
        """ reset

        Resets the change detector parameters.

        """
        super().reset()

        self.sample_count = 1
        self.activated_center = None
        self.concept_center = None

    def add_element(self, input_data):
        """ Add a new element to the statistics

        Parameters
        ----------
        prediction: float
        """
        if self.in_concept_change:
            self.reset()

        self.sample_count += 1

        activation = 0.0
        activation_lambda = self.lambda_
        distance = 0.0

        self.activated_center = None
        for center in self.centers:
            distance = math.sqrt(math.pow(input_data - center, 2.0))
            activation = math.exp(-math.pow(self.sigma * distance, 2))

            if activation >= activation_lambda:
                self.activated_center = center
                activation_lambda = activation

        if self.activated_center is None:
            self.centers.append(input_data)
            self.activated_center = input_data

        # First concept ?
        if not self.concept_center:
            self.concept_center = self.activated_center

        # Update markov
        probability = self.markov.update(
            self.concept_center, self.activated_center, self.alpha
        )

        if self.activated_center != self.concept_center:
            if probability < self.delta:
                self.in_warning_zone = True
            else:
                self.in_concept_change = True
                self.in_warning_zone = False
                self.concept_center = self.activated_center

        return probability
