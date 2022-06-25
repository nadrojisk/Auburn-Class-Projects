""" Module for the Individual Class which is used to aid the lightup solver module. """
import string
import random


class Individual:
    """ Individual Class used throughout the EA framework

    fitness - value denoting fitness of the Individual
    name - randomly generated / unique name to identify the individual
    """

    def __init__(self, fitness=0, name=None, solution=None, penalty=None, mutation_rate=None, penalty_coefficient=None):

        self.fitness = fitness
        self.solution = solution
        self.iterations = len(solution) if solution else 0
        self.penalty = penalty
        self.name = name
        self.mutation_rate = mutation_rate
        self.penalty_coefficient = penalty_coefficient
        if self.name is None:
            self.name = self.get_random_string()

    @staticmethod
    def get_random_string(length=8):
        """ Generate random string for name of individual.

        length - length of string
        """

        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

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
