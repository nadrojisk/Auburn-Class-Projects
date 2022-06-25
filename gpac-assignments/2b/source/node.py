""" Node module. Implements functionality for node object. """

import random
from utilities import MyException

operations = ['*', '+', '-', '/', 'RAND']
GHOST_DISTANCE = 'G'
PILL_DISTANCE = 'P'
FRUIT_DISTANCE = 'F'
WALL_DISTANCE = 'W'
CONSTANT = 'C'
sensors = [GHOST_DISTANCE, PILL_DISTANCE, FRUIT_DISTANCE, WALL_DISTANCE, CONSTANT]


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

    def __init__(self, depth=0, children=None, data=None, tree_type='grow', max_depth=4):
        self.tree_type = tree_type
        self.max_depth = max_depth
        self.depth = depth
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

        if self.depth >= self.max_depth - 1:
            value = self.generate_sensor()

        else:
            # If tree type is full, or first node in tree, or if coin flip
            # pick an operator, otherwise it should be a sensor for data
            if self.tree_type == 'full' or self.depth == 0 or random.randint(0, 1):
                value = random.choice(operations)
            else:
                value = self.generate_sensor()
        return value

    @staticmethod
    def generate_sensor():
        """ Generate sensor value, if it is constant generate
        a random value. """

        value = random.choice(sensors)
        if value == CONSTANT:
            value = random.randint(-10, 10)
        return value

    def grow(self):
        """ Grows tree from current node. If the max depth has been reached then nothing happens.
        If it is one before the max depth then the children are leaf nodes which
        must have a sensor value instead of an operation.

        Otherwise it is a 50 50 chance to be an operation or a sensor node.
        """

        if self.children != [None, None]:
            raise MyException("Error: Grow has been called twice on the same node")

        depth = self.depth + 1

        # loop for each child
        for element in range(2):
            if depth >= self.max_depth:
                break
            current = Node(depth, tree_type=self.tree_type, max_depth=self.max_depth)
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

    def calculate(self, ghost_distance, pill_distance, walls, fruit_distance):
        """ Calculates the output of the tree.

        Takes in sensor values which are translated in the tree.
        """

        # if data contains an operation we need to recursively call until
        # real values are stored
        if self.data in operations:
            value1 = self.children[0].calculate(
                ghost_distance, pill_distance, walls, fruit_distance)
            value2 = self.children[1].calculate(
                ghost_distance, pill_distance, walls, fruit_distance)
            output = operation_functions[self.data](value1, value2)
            return output

        return self.placeholder_to_value(ghost_distance, pill_distance, walls, fruit_distance)

    def placeholder_to_value(self, ghost_distance, pill_distance, walls, fruit_distance):
        """ Translates placeholder value into actual value.

        For instance if a node's data was 'G' and ghost_distance was 10 then 'G'
        would be converted to 10.
        """

        data = self.data
        if data == GHOST_DISTANCE:
            data = ghost_distance
        elif data == PILL_DISTANCE:
            data = pill_distance
        elif data == WALL_DISTANCE:
            data = walls
        elif data == FRUIT_DISTANCE:
            data = fruit_distance
        return data
