""" Individual Module. Contains Individual class definition. """

import string
import random


class Individual:
    """ Individual Class

    Stores important information such as game score, fitness, world contents,
    and tree.
    """

    def __init__(self, score, raw_score, contents, head_node, name=None):
        self.fitness = score
        self.score = raw_score
        self.contents = contents
        self.head_node = head_node

        if name is None:
            self.name = self.get_random_string()
        else:
            self.name = name

    @staticmethod
    def get_random_string(length=8):
        """ Generate random string for name of individual.

        length - length of string
        """

        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def __lt__(self, other):
        return self.fitness < other.fitness

    def __eq__(self, other):
        return self.fitness == other.fitness

    def __add__(self, other):
        return self.fitness + other.fitness

    def __radd__(self, other):
        return other + self.fitness
