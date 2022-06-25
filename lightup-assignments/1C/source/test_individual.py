import individual


def test_init_norm():
    actual = individual.Individual(10, 'test', [1, 2, 2], 20, .5, 2)
    assert actual.fitness == 10
    assert actual.name == 'test'
    assert actual.solution == [1, 2, 2]
    assert actual.iterations == 3
    assert actual.mutation_rate == .5
    assert actual.penalty == 20
    assert actual.penalty_coefficient == 2


def test_init_kwargs():
    kwargs = {'fitness': 10,
              'solution': [1, 2, 2], 'penalty': 20,
              'name': 'test'}

    kwargs['mutation_rate'] = .5
    kwargs['penalty_coefficient'] = 2

    actual = individual.Individual(**kwargs)
    assert actual.fitness == 10
    assert actual.name == 'test'
    assert actual.solution == [1, 2, 2]
    assert actual.iterations == 3
    assert actual.mutation_rate == .5
    assert actual.penalty == 20
    assert actual.penalty_coefficient == 2
