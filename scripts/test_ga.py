# Scratch checks of the genetic algorithm helpers in car_sim/ga.py.
# Run: python -m scripts.test_ga

import numpy as np

from car_sim.ga import to_vector
from car_sim.network import make_network


# Case 1: flattened vector has one entry per weight and bias.
#   6*8 (w1) + 8 (b1) + 8*6 (w2) + 6 (b2) = 110
def test_to_vector_shape():
    rng = np.random.default_rng(0)
    vector = to_vector(make_network(rng, 5))
    assert vector.shape == (110,), f"shape {vector.shape}"
    print("PASS to_vector_shape")


# Case 2: entries are laid out in order w1, b1, w2, b2.
#   vector starts with the first row of w1 and ends with b2.
def test_to_vector_order():
    rng = np.random.default_rng(0)
    w1, b1, w2, b2 = make_network(rng, 5)
    vector = to_vector((w1, b1, w2, b2))
    assert np.array_equal(vector[:3], w1[0, :3]), f"first entries {vector[:3]}"
    assert np.array_equal(vector[-6:], b2), f"last entries {vector[-6:]}"
    print("PASS to_vector_order")


# Case 3: the vector is a copy, so mutating it must not touch the network.
def test_to_vector_is_copy():
    rng = np.random.default_rng(0)
    network = make_network(rng, 5)
    original = network[0][0, 0]
    vector = to_vector(network)
    vector[0] = 999
    assert network[0][0, 0] == original, f"w1[0, 0] changed to {network[0][0, 0]}"
    print("PASS to_vector_is_copy")


if __name__ == "__main__":
    test_to_vector_shape()
    test_to_vector_order()
    test_to_vector_is_copy()
