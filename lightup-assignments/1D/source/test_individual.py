import individual
from individual import Individual


def test_init_norm():
    actual = individual.Individual(10, 'test', [1, 2, 2])
    assert actual.lit == 10
    assert actual.name == 'test'
    assert actual.solution == [1, 2, 2]


def test_init_kwargs():
    kwargs = {'lit': 10,
              'solution': [1, 2, 2],
              'name': 'test'}

    actual = individual.Individual(**kwargs)
    assert actual.lit == 10
    assert actual.name == 'test'
    assert actual.solution == [1, 2, 2]


def test_dom():
    a_ind = Individual(100, black_cell_violations=0, bulb_violations=0)
    b_ind = Individual(90, black_cell_violations=0, bulb_violations=0)
    c_ind = Individual(90, black_cell_violations=0, bulb_violations=0)
    d_ind = Individual(90, black_cell_violations=1, bulb_violations=0)

    assert a_ind > b_ind
    assert a_ind > c_ind
    assert a_ind > d_ind

    assert b_ind < a_ind
    assert not b_ind < c_ind
    assert not b_ind > c_ind
    assert b_ind > d_ind

    assert c_ind < a_ind
    assert not c_ind < b_ind
    assert not c_ind > b_ind
    assert c_ind > d_ind


def test_sort():
    a_ind = Individual(100, black_cell_violations=0, bulb_violations=0)
    b_ind = Individual(90, black_cell_violations=0, bulb_violations=0)
    c_ind = Individual(90, black_cell_violations=0, bulb_violations=0)
    d_ind = Individual(90, black_cell_violations=1, bulb_violations=0)

    individuals = sorted([d_ind, b_ind, c_ind, a_ind], reverse=True)

    assert individuals == [a_ind, b_ind, c_ind, d_ind]


def test_eq():
    b_ind = Individual(90, 'test', black_cell_violations=0, bulb_violations=0)
    c_ind = Individual(90, 'test', black_cell_violations=0, bulb_violations=0)
    assert b_ind == c_ind
