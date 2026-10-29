# Scratch checks of crossover in car_sim/ga.py.
# Run: python -m scripts.test_crossover

import numpy as np

from car_sim.ga import crossover


# Parent a is all zeros, parent b is all ones, so every child gene shows which parent it came from.
def make_parents(n):
    return np.zeros(n), np.ones(n)


# Print parents then child, one row each, truncated to the first `limit` genes.
def show(a, b, child, limit=20):
    def row(label, g):
        vals = " ".join(f"{v:g}" for v in g[:limit])
        return f"     {label}: {vals}{' ...' if len(g) > limit else ''}"
    print(row("a    ", a))
    print(row("b    ", b))
    print(row("child", child))


# Case 1: child has the same shape and dtype as the parents.
def test_child_shape_and_dtype():
    a, b = make_parents(20)
    child = crossover(a, b, np.random.default_rng(0))
    assert child.shape == a.shape, f"shape {child.shape}, want {a.shape}"
    assert child.dtype == a.dtype, f"dtype {child.dtype}, want {a.dtype}"
    print(f"PASS child_shape_and_dtype: shape {child.shape}, dtype {child.dtype}")
    show(a, b, child)


# Case 2: every gene comes from parent a or parent b at the same position.
def test_genes_come_from_parents():
    rng = np.random.default_rng(1)
    a = rng.integers(0, 100, size=20).astype(float)
    b = rng.integers(-100, 0, size=20).astype(float)
    child = crossover(a, b, np.random.default_rng(2))
    for i in range(len(a)):
        assert child[i] == a[i] or child[i] == b[i], f"gene {i}: {child[i]} not in ({a[i]}, {b[i]})"
    print(f"PASS genes_come_from_parents: {len(a)} genes each match a[i] or b[i]")
    show(a, b, child)


# Case 3: identical parents give a child equal to both.
def test_identical_parents():
    a = np.arange(10, dtype=float)
    b = a.copy()
    child = crossover(a, b, np.random.default_rng(3))
    assert np.array_equal(child, a), f"got {child}"
    print("PASS identical_parents")
    show(a, b, child)


# Case 4: with distinct parents the child mixes both, it is not a copy of one parent.
def test_child_mixes_both_parents():
    a, b = make_parents(20)
    child = crossover(a, b, np.random.default_rng(4))
    n_b = int(child.sum())
    assert 0 < n_b < 20, f"{n_b} genes from b, child is a copy of one parent"
    print(f"PASS child_mixes_both_parents: {20 - n_b} genes from a, {n_b} from b")
    show(a, b, child)


# Case 5: the coin flip is roughly fair (large genome, wide tolerance so the seed is not fragile).
def test_roughly_even_split():
    a, b = make_parents(10000)
    child = crossover(a, b, np.random.default_rng(5))
    frac_b = child.mean()
    assert 0.45 < frac_b < 0.55, f"{frac_b:.3f} of genes from b"
    print(f"PASS roughly_even_split: {frac_b:.3f} of genes from b")
    show(a, b, child)


# Case 6: same seed gives the same child, different seeds give different children.
def test_seed_reproducible():
    a, b = make_parents(20)
    c1 = crossover(a, b, np.random.default_rng(6))
    c2 = crossover(a, b, np.random.default_rng(6))
    c3 = crossover(a, b, np.random.default_rng(7))
    assert np.array_equal(c1, c2), "same seed gave different children"
    assert not np.array_equal(c1, c3), "different seeds gave the same child"
    print("PASS seed_reproducible: seeds 6/6 equal, seeds 6/7 differ")
    show(a, b, c1)
    print(f"     seed 6 again: {' '.join(f'{v:g}' for v in c2)}")
    print(f"     seed 7      : {' '.join(f'{v:g}' for v in c3)}")


# Case 7: the child is a new array and the parents are left untouched.
def test_parents_unchanged():
    a = np.arange(10, dtype=float)
    b = np.arange(10, dtype=float) * -1
    a_before, b_before = a.copy(), b.copy()
    child = crossover(a, b, np.random.default_rng(8))
    show(a, b, child)
    assert child is not a and child is not b, "child is one of the parents"
    child[:] = 999
    assert np.array_equal(a, a_before), f"a changed to {a}"
    assert np.array_equal(b, b_before), f"b changed to {b}"
    print("PASS parents_unchanged: parents intact after overwriting the child with 999")
    show(a, b, child)


# Case 8: swapping the parents with the same seed gives the complementary child.
#   Same coin flips, so a gene taken from a in one call is taken from b in the other.
def test_swapped_parents_complementary():
    a, b = make_parents(20)
    c_ab = crossover(a, b, np.random.default_rng(9))
    c_ba = crossover(b, a, np.random.default_rng(9))
    assert np.array_equal(c_ab + c_ba, np.ones(20)), "children are not complementary"
    print("PASS swapped_parents_complementary")
    show(a, b, c_ab)
    print(f"     swapped (b, a) child: {' '.join(f'{v:g}' for v in c_ba)}")


if __name__ == "__main__":
    test_child_shape_and_dtype()
    test_genes_come_from_parents()
    test_identical_parents()
    test_child_mixes_both_parents()
    test_roughly_even_split()
    test_seed_reproducible()
    test_parents_unchanged()
    test_swapped_parents_complementary()
