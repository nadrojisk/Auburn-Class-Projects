""" Node module. Implements functionality for node object. """

import random
import gpac
from utilities import MyException

operations = ['*', '+', '-', '/', 'RAND']
GHOST_DISTANCE = 'G'
PILL_DISTANCE = 'P'
FRUIT_DISTANCE = 'F'
WALL_DISTANCE = 'W'
CONSTANT = 'C'
PACMAN_DISTANCE = 'M'
PACMAN_SHORTEST_PATH = 'M_SHORT'
GHOST_SHORTEST_PATH = "G_SHORT"
pacman_sensors = [GHOST_DISTANCE, PILL_DISTANCE, FRUIT_DISTANCE,
                  WALL_DISTANCE, CONSTANT, GHOST_SHORTEST_PATH]
ghost_sensors = [GHOST_DISTANCE, PACMAN_DISTANCE, PACMAN_SHORTEST_PATH]


def mul(arg_a, arg_b):
    """ Multiplication function to be used by nodes when calculating
    final value.
    """

    return arg_a * arg_b


def add(arg_a, arg_b):
    """ Addition function to be used by nodes when calculating
    final value.
    """

    return arg_a + arg_b


def sub(arg_a, arg_b):
    """ Subtract function to be used by nodes when calculating
    final value.
    """

    return arg_a - arg_b


def div(arg_a, arg_b):
    """ Division function to be used by nodes when calculating
    final value.
    """

    if arg_b == 0:
        return 0
    return arg_a / arg_b


def rand(arg_a, arg_b):
    """ Random function to be used by nodes when calculating
    final value.
    """

    if arg_a > arg_b:
        return random.uniform(a=arg_b, b=arg_a)
    return random.uniform(arg_a, arg_b)


operation_functions = {'*': mul, '+': add, '-': sub, '/': div, 'RAND': rand}


class Node:
    """ Node class to be used with Tree based GP Solver """

    def __init__(self, depth=0, children=None, data=None, tree_type='grow', depth_limit=None,
                 max_depth=4, unit=gpac.PACMAN):
        self.tree_type = tree_type
        if depth_limit:
            self.max_depth = random.randint(1, depth_limit)
        else:
            self.max_depth = max_depth
        self.depth = depth
        self.unit = unit
        if data:
            self.data = data
        else:
            self.data = self.generate_value()
        if children:
            self.children = children
        else:
            self.children = [None, None]
        self.height = None

    def generate_value(self):
        """ Generate value for node. """

        if self.depth >= self.max_depth:
            value = self.generate_sensor()

        else:
            # If tree type is full, or first node in tree, or if coin flip
            # pick an operator, otherwise it should be a sensor for data
            if self.tree_type == 'full' or self.depth == 0 or random.randint(0, 1):
                value = random.choice(operations)
            else:
                value = self.generate_sensor()
        return value

    def generate_sensor(self):
        """ Generate sensor value, if it is constant generate
        a random value. """
        sensors = pacman_sensors if self.unit == gpac.PACMAN else ghost_sensors
        value = random.choice(sensors)
        if value == CONSTANT:
            value = random.uniform(-10, 10)
        return value

    def grow(self):
        """ Grows tree from current node. If the max depth has been reached then nothing happens.
        If it is one before the max depth then the children are leaf nodes which
        must have a sensor value instead of an operation.

        Otherwise it is a 50 50 chance to be an operation or a sensor node.
        """
        if self.children != [None, None]:
            raise MyException("Error: Grow has been called twice on the same node")
        if self.data in operations:
            depth = self.depth + 1

            # loop for each child
            for element in range(2):
                if depth > self.max_depth:
                    break
                current = Node(depth, tree_type=self.tree_type,
                               max_depth=self.max_depth, unit=self.unit)
                if current.data in operations:
                    current.grow()
                self.children[element] = current

        self.get_height()

    def to_list(self, node_list=None):
        """ Convert Tree to list of lists"""

        if not node_list:
            node_list = []
            for _ in range(self.get_height() + 1):
                node_list.append([])
        try:
            node_list[self.depth].append(self)
        except IndexError:
            print('error to_list')
        for child in self.children:
            if child:
                node_list = child.to_list(node_list)
        return node_list

    def get_total_nodes(self, count=1):
        """ Calculating the total number of nodes in a tree. """

        for child in self.children:
            if child:
                count = 1 + child.get_total_nodes(count)
        return count

    def update_depth(self, depth):
        """ Update the depth values of a node and its children. """
        self.depth = depth
        for child in self.children:
            if child:
                child.update_depth(self.depth + 1)

    def swap(self, other):
        """ Swap a node with another, ensuring its children
        and variables are updated properly.
        """

        self.data = other.data
        self.children = other.children

        self.update_depth(self.depth)
        self.get_height()

    def get_height(self):
        """ Get heigh of current node. Leaf nodes will have a height of 0.

        Recursively call get_height on children and pick the highest number
        from the two children and add by one.
        If there is no children then the node is a leaf node and therefore its height is 0.
        """

        if self.children[0]:
            child_one_height = self.children[0].get_height()
        else:
            child_one_height = -1

        if self.children[1]:
            child_two_height = self.children[1].get_height()
        else:
            child_two_height = -1

        height = max(child_one_height, child_two_height) + 1

        self.height = height
        return height

    def parse_tree(self, prior='', depth=0):
        """ Parses Tree from current node. Returns parsed tree in a string format. """
        output = depth * '|' + str(self.data) + "\n"
        if self.children[0] is not None:
            output = self.children[0].parse_tree(output, depth=depth + 1)
        if self.children[1] is not None:
            output = self.children[1].parse_tree(output, depth=depth + 1)
        output = prior + output
        return output

    def calculate(self, *args, **kwargs):
        """ Evaluates node of current individual. Checks first
        if it is a Pacman controller or a Ghost one.
        """

        func = self.calculate_pacman if self.unit == gpac.PACMAN else self.calculate_ghost
        return func(*args, **kwargs)

    def calculate_ghost(self, ghost_distance, pacman_distance, pacman_shortest):
        """ Evaluates tree of Ghost controller """

        if self.data in operations:
            value1 = self.children[0].calculate_ghost(
                ghost_distance, pacman_distance, pacman_shortest)
            value2 = self.children[1].calculate_ghost(
                ghost_distance, pacman_distance, pacman_shortest)
            output = operation_functions[self.data](value1, value2)
            return output

        data = self.data
        if data == GHOST_DISTANCE:
            data = ghost_distance
        elif data == PACMAN_DISTANCE:
            data = pacman_distance
        elif data == PACMAN_SHORTEST_PATH:
            data = pacman_shortest
        return data

    def calculate_pacman(self, ghost_distance, pill_distance, walls,
                         fruit_distance, ghost_shortest):
        """ Calculates the output of the tree.

        Takes in sensor values which are translated in the tree.
        """

        # if data contains an operation we need to recursively call until
        # real values are stored
        if self.data in operations:
            value1 = self.children[0].calculate_pacman(
                ghost_distance, pill_distance, walls, fruit_distance, ghost_shortest)
            value2 = self.children[1].calculate_pacman(
                ghost_distance, pill_distance, walls, fruit_distance, ghost_shortest)
            output = operation_functions[self.data](value1, value2)
            return output

        data = self.data
        if data == GHOST_DISTANCE:
            data = ghost_distance
        elif data == PILL_DISTANCE:
            data = pill_distance
        elif data == WALL_DISTANCE:
            data = walls
        elif data == FRUIT_DISTANCE:
            data = fruit_distance
        elif data == GHOST_SHORTEST_PATH:
            data = ghost_shortest
        return data
