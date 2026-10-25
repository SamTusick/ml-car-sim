# Scratch check of forward() from init_experiment.py using hand-built networks.
# Run: python -m "scripts.test_forward.py"

import numpy as np

from .init_experiment import N_INPUTS, N_HIDDEN, N_OUTPUTS, forward


def zero_network():
    return (
        np.zeros((N_INPUTS, N_HIDDEN)),
        np.zeros(N_HIDDEN),
        np.zeros((N_HIDDEN, N_OUTPUTS)),
        np.zeros(N_OUTPUTS),
    )


def check(name, network, obs, expected_hidden, expected_action):
    hidden, action = forward(network, obs)
    assert hidden.shape == (N_HIDDEN,), f"{name}: hidden shape {hidden.shape}"
    assert isinstance(action, int), f"{name}: action type {type(action)}"
    assert 0 <= action < N_OUTPUTS, f"{name}: action {action} out of range"
    assert np.allclose(hidden, expected_hidden), f"{name}: hidden {hidden}"
    assert action == expected_action, f"{name}: action {action}, expected {expected_action}"
    print(f"PASS {name}: action={action}")


# Case 1: obvious answer.
# All weights and w1/b1 are zero, only b2[3] = 1.
#   hidden = tanh(0) = [0, 0, 0, 0, 0, 0, 0, 0]
#   output = [0, 0, 0, 1, 0, 0]
#   action = 3
def test_bias_only():
    net = zero_network()
    net[3][3] = 1.0
    obs = np.array([0.3, 0.9, 0.1, 0.5, 0.5, 0.2], dtype=np.float32)
    check("bias_only", net, obs, np.zeros(N_HIDDEN), 3)


# Case 2: tanh changes the answer.
# w1[0, 0] = 1, w2[0, 1] = 1, b2[2] = 1, obs[0] = 2, everything else zero.
#   hidden = [tanh(2), 0, 0, 0, 0, 0, 0, 0] = [0.9640, 0, 0, 0, 0, 0, 0, 0]
#   output = [0, 0.9640, 1.0, 0, 0, 0]
#   action = 2   (without tanh, hidden[0] would be 2, output[1] = 2 > 1, action = 1)
def test_tanh_squashes():
    net = zero_network()
    net[0][0, 0] = 1.0
    net[2][0, 1] = 1.0
    net[3][2] = 1.0
    obs = np.array([2, 0, 0, 0, 0, 0], dtype=np.float32)
    expected_hidden = np.zeros(N_HIDDEN)
    expected_hidden[0] = np.tanh(2.0)
    check("tanh_squashes", net, obs, expected_hidden, 2)


if __name__ == "__main__":
    test_bias_only()
    test_tanh_squashes()
