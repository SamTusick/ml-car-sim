# Scratch checks of next_generation in car_sim/ga.py.
# Run: python -m scripts.test_next_generation

import numpy as np

from car_sim import ga
from car_sim.ga import next_generation

# Gene j of genome i is i * 100 + j, so every gene value says which genome and position it came from.
# Fitness scores are handpicked and deliberately out of order.
#   index:   0   1   2   3    4   5   6   7
FITNESS = [30, 5, 80, -10, 55, 12, 90, 41]
N_GENES = 6
# top 25% of 8 = 2 parents: genomes 2 (80) and 6 (90), worst to best. Both are elites.
POOL_IDS = [2, 6]


def make_population(n=8):
    return [np.arange(N_GENES, dtype=float) + i * 100 for i in range(n)]


def ids(genomes):
    return [int(g[0]) // 100 for g in genomes]


# Run next_generation with MUTATION_RATE temporarily set to `rate`.
def run(rate, seed=0, population=None):
    old = ga.MUTATION_RATE
    ga.MUTATION_RATE = rate
    try:
        population = population if population is not None else make_population()
        return next_generation(population, FITNESS, np.random.default_rng(seed))
    finally:
        ga.MUTATION_RATE = old


# Case 1: population size is unchanged.
def test_output_length():
    new = run(ga.MUTATION_RATE)
    assert len(new) == 8, f"got {len(new)} genomes"
    assert all(g.shape == (N_GENES,) for g in new), "a genome changed shape"
    print(f"PASS output_length: {len(new)} genomes of shape {new[0].shape}")


# Case 2: the first two are the two best by value, in pool order (worst to best: 2 then 6),
#   but they are copies, not the original objects.
def test_elites_are_copies_of_best():
    population = make_population()
    new = run(ga.MUTATION_RATE, population=population)
    for slot, src in enumerate(POOL_IDS):
        assert np.array_equal(new[slot], population[src]), f"slot {slot} is not genome {src} by value"
        assert new[slot] is not population[src], f"slot {slot} is the same object as genome {src}"
    print(f"PASS elites_are_copies_of_best: slots 0,1 equal genomes {POOL_IDS} by value, not identical objects")


# Case 2b: changing an elite afterwards must not touch the old population.
def test_elites_share_no_memory():
    population = make_population()
    before = [g.copy() for g in population]
    new = run(ga.MUTATION_RATE, population=population)
    new[0][:] = -999
    new[1][:] = -999
    for i, g in enumerate(population):
        assert np.array_equal(g, before[i]), f"genome {i} changed to {g}"
    print("PASS elites_share_no_memory: old population intact after overwriting the elites")


# Case 3: with MUTATION_RATE = 0 every child gene is the pool parents' gene at the same position.
def test_no_mutation_genes_from_pool():
    pool = [make_population()[i] for i in POOL_IDS]
    new = run(0)
    for c, child in enumerate(new[2:], start=2):
        for j in range(N_GENES):
            allowed = [p[j] for p in pool]
            assert child[j] in allowed, f"child {c} gene {j}: {child[j]} not in {allowed}"
    print(f"PASS no_mutation_genes_from_pool: {len(new) - 2} children, every gene from genomes {POOL_IDS}")
    for c, child in enumerate(new[2:], start=2):
        print(f"     child {c}: {' '.join(f'{v:g}' for v in child)}")


# Case 4: with MUTATION_RATE = 1 every gene is shifted, so no child gene matches a pool parent gene,
#   which means no child can equal a pure crossover result.
def test_full_mutation_differs_from_crossover():
    pool = [make_population()[i] for i in POOL_IDS]
    new = run(1)
    for c, child in enumerate(new[2:], start=2):
        for j in range(N_GENES):
            allowed = [p[j] for p in pool]
            assert child[j] not in allowed, f"child {c} gene {j}: {child[j]} was not mutated"
    print(f"PASS full_mutation_differs_from_crossover: {len(new) - 2} children, no gene left unmutated")
    print(f"     child 2: {' '.join(f'{v:.3f}' for v in new[2])}")


# Case 4b: mutation never touches the elites.
def test_elites_unmutated_at_full_rate():
    population = make_population()
    new = run(1, population=population)
    for slot, src in enumerate(POOL_IDS):
        assert np.array_equal(new[slot], population[src]), f"elite {slot} was mutated"
    print("PASS elites_unmutated_at_full_rate")


# Case 5: same seed gives identical populations, a different seed does not.
def test_seed_reproducible():
    a = run(ga.MUTATION_RATE, seed=5)
    b = run(ga.MUTATION_RATE, seed=5)
    c = run(ga.MUTATION_RATE, seed=6)
    assert all(np.array_equal(x, y) for x, y in zip(a, b)), "same seed gave different populations"
    assert not all(np.array_equal(x, y) for x, y in zip(a, c)), "different seeds gave the same population"
    print("PASS seed_reproducible: seeds 5/5 equal, seeds 5/6 differ")


if __name__ == "__main__":
    test_output_length()
    test_elites_are_copies_of_best()
    test_elites_share_no_memory()
    test_no_mutation_genes_from_pool()
    test_full_mutation_differs_from_crossover()
    test_elites_unmutated_at_full_rate()
    test_seed_reproducible()
