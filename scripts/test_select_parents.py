# Scratch checks of select_parents in car_sim/ga.py.
# Run: python -m scripts.test_select_parents

import numpy as np

from car_sim.ga import select_parents


# Each genome is filled with its own index so it is easy to tell which one came back.
# Fitness scores are handpicked and deliberately out of order, with negatives.
#   index:   0   1   2   3   4  5   6   7   8  9
FITNESS = [5, -20, 40, 12, -3, 90, 0, 33, 61, 7]


def make_population(n):
    return [np.full(4, i, dtype=float) for i in range(n)]


def ids(genomes):
    return [int(g[0]) for g in genomes]


# Case 1: 10 genomes, top 25% rounds up to 3 parents.
def test_parent_count():
    parents, _ = select_parents(make_population(10), FITNESS)
    assert len(parents) == 3, f"got {len(parents)} parents"
    print(f"PASS parent_count: {len(parents)} parents from {len(FITNESS)} genomes")


# Case 2: parents are the three highest scores (90, 61, 40), worst to best.
#   genomes 2, 8, 5
def test_parent_pool_contents_and_order():
    parents, _ = select_parents(make_population(10), FITNESS)
    assert ids(parents) == [2, 8, 5], f"got {ids(parents)}"
    print(f"PASS parent_pool_contents_and_order: fitness {FITNESS}")
    print(f"     parent ids {ids(parents)}, scores {[FITNESS[i] for i in ids(parents)]}")


# Case 3: elites are the two best of the pool (90, 61).
#   genomes 8, 5
def test_elite_parents():
    _, elites = select_parents(make_population(10), FITNESS)
    assert ids(elites) == [8, 5], f"got {ids(elites)}"
    print(f"PASS elite_parents: ids {ids(elites)}, scores {[FITNESS[i] for i in ids(elites)]}")


# Case 4: returned genomes are the original population entries, not copies or reshaped.
def test_returns_population_members():
    population = make_population(10)
    parents, elites = select_parents(population, FITNESS)
    assert parents[2] is population[5], "best parent is not population[5]"
    assert elites[1] is population[5], "best elite is not population[5]"
    print(f"PASS returns_population_members: parents {ids(parents)}, elites {ids(elites)}, same objects as population")


# Case 5: inputs are left untouched (fitness not sorted in place, population not reordered).
def test_inputs_unchanged():
    population = make_population(10)
    fitness = list(FITNESS)
    select_parents(population, fitness)
    assert fitness == FITNESS, f"fitness changed to {fitness}"
    assert ids(population) == list(range(10)), f"population order {ids(population)}"
    print(f"PASS inputs_unchanged: fitness {fitness}, population order {ids(population)}")


# Case 6: accepts a numpy array of scores, same result as a list.
def test_numpy_fitness():
    parents, elites = select_parents(make_population(10), np.array(FITNESS))
    assert ids(parents) == [2, 8, 5], f"parents {ids(parents)}"
    assert ids(elites) == [8, 5], f"elites {ids(elites)}"
    print(f"PASS numpy_fitness: parents {ids(parents)}, elites {ids(elites)}")


# Case 7: parent count uses ceil, not floor.
#   9 * 0.25 = 2.25 -> 3, 5 * 0.25 = 1.25 -> 2
def test_parent_count_rounds_up():
    for size, expected in ((9, 3), (5, 2)):
        parents, _ = select_parents(make_population(size), list(range(size)))
        assert len(parents) == expected, f"size {size}: got {len(parents)}, want {expected}"
        print(f"     size {size}: {len(parents)} parents (want {expected})")
    print("PASS parent_count_rounds_up")


# Case 8: the best genome is always last in the pool and in the elites,
#   wherever it sits in the population.
def test_best_is_last():
    for best in (0, 4, 9):
        fitness = [0.0] * 10
        fitness[best] = 100.0
        parents, elites = select_parents(make_population(10), fitness)
        assert int(parents[-1][0]) == best, f"best={best}: pool ends {ids(parents)}"
        assert int(elites[-1][0]) == best, f"best={best}: elites end {ids(elites)}"
        print(f"     best={best}: parents {ids(parents)}, elites {ids(elites)}")
    print("PASS best_is_last")


if __name__ == "__main__":
    test_parent_count()
    test_parent_pool_contents_and_order()
    test_elite_parents()
    test_returns_population_members()
    test_inputs_unchanged()
    test_numpy_fitness()
    test_parent_count_rounds_up()
    test_best_is_last()
