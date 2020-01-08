import math


class MarkovChain:
    def __init__(self):
        self.system = {}
        self.current_origin = None
        self.current_destination = None

    def update(self, origin, destination, alpha):
        origin = f"{origin:.2f}"
        destination = f"{destination:.2f}"

        if origin != destination or (
            not self.current_origin and not self.current_destination
        ):
            self.current_origin = origin
            self.current_destination = destination

        if self.current_origin not in self.system:
            self.system[self.current_origin] = {}

        # if self.current_destination not in self.system[self.current_origin] and not self.system[self.current_origin]:
        #     self.system[self.current_origin][self.current_destination] = 1.0

        if self.current_destination not in self.system[self.current_origin]:
            self.system[self.current_origin][self.current_destination] = 0.0

        for possible_destination in self.system[self.current_origin]:
            if possible_destination == self.current_destination:
                self.system[self.current_origin][possible_destination] += alpha
                if self.system[self.current_origin][possible_destination] > 1:
                    self.system[self.current_origin][possible_destination] = 1
            else:
                reduction_factor = alpha / (len(self.system[self.current_origin]) - 1)
                self.system[self.current_origin][
                    possible_destination
                ] -= reduction_factor
                if self.system[self.current_origin][possible_destination] < 0:
                    self.system[self.current_origin][possible_destination] = 0

        return self.system[self.current_origin][self.current_destination]


class RBFChain:
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
        self.sample_count = 1
        # Reset or not the markov
        # self.markov = MarkovChain()

    def add_element(self, input_data):
        """ Add a new element to the statistics

        Parameters
        ----------
        prediction: float
        """
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

        if self.actual_center is None:
            self.actual_center = activated_center

        # Update markov
        probability = self.markov.update(
            self.actual_center, activated_center, self.alpha
        )

        return probability

        # # If center changed
        # if self.actual_center != activated_center:
        #     if probability >= self.delta:
        #         self.in_concept_change = True
        #     else:
        #         self.in_warning_zone = True

        #     # Update actual center
        #     self.actual_center = activated_center

        # if probability >= self.delta and self.in_warning_zone:
        #     self.in_concept_change = True
