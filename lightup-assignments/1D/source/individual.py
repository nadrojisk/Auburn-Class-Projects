""" Module for the Individual Class which is used to aid the lightup solver module. """
import string
import random


class Individual:
    """ Individual Class used throughout the EA framework

    fitness - value denoting fitness of the Individual
    name - randomly generated / unique name to identify the individual
    """

    def __init__(self, lit=0, name=None, solution=None, fitness=0,
                 black_cell_violations=0, bulb_violations=0, bulbs=0):

        self.lit = lit
        self.fitness = fitness
        self.solution = solution
        self.bulbs = bulbs
        self.black_cell_violations = black_cell_violations
        self.bulb_violations = bulb_violations
        self.name = name

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

        return [cls(fitness=x[0], name=x[1]) for x in zip(fitnesses, names)]

    def __lt__(self, other):
        less_or_equal = (self.lit <= other.lit) and \
            (self.bulb_violations >= other.bulb_violations) and \
            (self.black_cell_violations >= other.black_cell_violations) and \
            (self.bulbs <= other.bulbs)
        less = (self.lit < other.lit) or \
            (self.bulb_violations > other.bulb_violations) or \
            (self.black_cell_violations > other.black_cell_violations) or \
            (self.bulbs < other.bulbs)
        return less_or_equal and less

    def __eq__(self, other):
        return self.lit == other.lit and \
            self.black_cell_violations == other.black_cell_violations and\
            self.bulb_violations == other.bulb_violations and\
            self.bulbs == other.bulbs

    def __add__(self, other):
        return self.fitness + other.fitness

    def __radd__(self, other):
        return other + self.fitness

    def __str__(self):
        out = f"{self.name} "
        out += f"f:{self.fitness} "
        out += f"l:{self.lit} "
        out += f"cell:{self.black_cell_violations} "
        out += f"bulb: {self.bulb_violations}"
        return out

    def __repr__(self):
        return str(self)
