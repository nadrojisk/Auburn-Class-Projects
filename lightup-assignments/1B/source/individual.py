""" Module for the Individual Class which is used to aid the lightup solver module. """
import string
import random


class Individual:
    """ Individual Class used throughout the EA framework

    fitness - value denoting fitness of the Individual
    name - randomly generated / unique name to identify the individual
    """

    def __init__(self, fitness, name=None, solution=None, iterations=None, runtime=None):
        self.fitness = fitness
        self.solution = solution
        self.iterations = iterations
        self.fitness_og = fitness
        self.runtime = runtime
        self.name = name
        if self.name is None:
            self.name = self.get_random_string()
        self.prob = 0

    @staticmethod
    def get_random_string(length=8):
        """ Generate random string for name of individual.

        length -- length of string
        """

        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def windowed(self, min_fit):
        """ Modifies fitness to windowed value

        min_fit - minimum fitness of current set
        """

        self.fitness = self.fitness - min_fit + 1

    def cleanup(self):
        """ Reverts temp values back to original values."""

        self.prob = 0
        self.fitness = self.fitness_og

    @classmethod
    def from_list(cls, fitnesses, names):
        """Helper method to ingest from list of fitnesses and names. """

        return [cls(x[0], x[1]) for x in zip(fitnesses, names)]

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __eq__(self, other):
        return self.fitness == other.fitness and self.name == other.name

    def __add__(self, other):
        return self.fitness + other.fitness

    def __radd__(self, other):
        return other + self.fitness
