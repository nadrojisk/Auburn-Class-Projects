import pytest
import node
import random


def test_init():
    random.seed(2)
    instance = node.Node(10)

    assert instance.data == 'G'
    assert instance.depth == 10
    assert instance.children == [None, None]


def test_grow_max_depth():
    instance = node.Node(9)
    instance.grow()
    assert instance.children == [None, None]


def test_grow_almost_max():
    random.seed(2)
    instance = node.Node(2)
    instance.grow()

    assert instance.children[0].data == 'G'
    assert instance.children[1].data == 'F'

    assert instance.children[0].children == [None, None]
    assert instance.children[1].children == [None, None]


def test_grow_10():
    random.seed(2)
    instance = node.Node(0, max_depth=10)
    instance.grow()
    for y in range(2):
        current_node = instance.children[y]
        for x in range(1, instance.max_depth + 1):
            assert current_node.depth == x

            # break early if node contains a value and not an operation
            # as it will not have any children
            if current_node.data not in node.operations:
                break
            current_node = current_node.children[y]


def test_grow_5():
    random.seed(3)
    instance = node.Node(0, max_depth=5)
    instance.grow()
    for y in range(2):
        current_node = instance.children[y]
        for x in range(1, instance.max_depth + 1):
            assert current_node.depth == x

            # break early if node contains a value and not an operation
            # as it will not have any children
            if current_node.data not in node.operations:
                break
            current_node = current_node.children[y]


def test_grow_twice():
    random.seed(1)
    instance = node.Node(0)
    instance.grow()
    with pytest.raises(Exception):
        instance.grow()


def test_parse_tree():
    random.seed(1)
    instance = node.Node(data='*', depth=0)
    instance.children[0] = node.Node(data='/', depth=1)
    instance.children[1] = node.Node(data='RAND', depth=1)
    instance.children[0].children[0] = node.Node(data=1.2, depth=2)
    instance.children[0].children[1] = node.Node(data='G', depth=2)
    instance.children[1].children[0] = node.Node(data='W', depth=2)
    instance.children[1].children[1] = node.Node(data='P', depth=2)

    output = instance.parse_tree()
    assert output == "*\n|/\n||1.2\n||G\n|RAND\n||W\n||P\n"


def test_total_count():
    random.seed(1)
    instance = node.Node(data='*', depth=0)
    instance.children[0] = node.Node(data='/', depth=1)
    instance.children[1] = node.Node(data='RAND', depth=1)
    instance.children[0].children[0] = node.Node(data=1.2, depth=2)
    instance.children[0].children[1] = node.Node(data='G', depth=2)
    instance.children[1].children[0] = node.Node(data='W', depth=2)
    instance.children[1].children[1] = node.Node(data='P', depth=2)

    count = instance.get_total_nodes()
    assert count == 7


def test_total_count_1():
    random.seed(1)
    instance = node.Node(data='*', depth=0)

    count = instance.get_total_nodes()
    assert count == 1


def test_get_value_from_tree():
    random.seed(1)
    instance = node.Node(data='*', depth=0)
    instance.children[0] = node.Node(data='/', depth=1)
    instance.children[1] = node.Node(data='RAND', depth=1)
    instance.children[0].children[0] = node.Node(data=1.2, depth=2)
    instance.children[0].children[1] = node.Node(data='G', depth=2)
    instance.children[1].children[0] = node.Node(data='W', depth=2)
    instance.children[1].children[1] = node.Node(data='P', depth=2)

    value = instance.calculate(10, 1, 2, 0)
    assert value == 0.13612370929348813


def test_height_bottom():
    instance = node.Node(9)
    instance.grow()
    assert instance.height == 0


def test_height_top():
    random.seed(4)
    instance = node.Node(0)
    instance.grow()
    assert instance.height == 3


def test_to_list():
    instance = node.Node(data='*', depth=0)
    instance.children[0] = node.Node(data='/', depth=1)
    instance.children[1] = node.Node(data='RAND', depth=1)
    instance.children[0].children[0] = node.Node(data=1.2, depth=2)
    instance.children[0].children[1] = node.Node(data='G', depth=2)
    instance.children[1].children[0] = node.Node(data='W', depth=2)
    instance.children[1].children[1] = node.Node(data='P', depth=2)
    instance.children[1].children[1].height = 0
    instance.children[1].children[0].height = 0
    instance.children[1].height = 1
    instance.children[0].height = 1
    instance.children[0].children[0].height = 0
    instance.children[0].children[1].height = 0
    instance.height = 2
    node_list = instance.to_list()
    assert len(node_list) == 3
    assert len(node_list[0]) == 1
    assert len(node_list[1]) == 2
    assert len(node_list[2]) == 4
