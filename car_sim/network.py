import numpy as np

SEED = 0
N_NETWORKS = 50
N_INPUTS = 6
N_HIDDEN = 8
N_OUTPUTS = 6

def make_network(rng, r):
    w1 = rng.uniform(-r, r, size=(N_INPUTS,N_HIDDEN)) # weight matrix 1 | shape (6,8)
    w2 = rng.uniform(-r, r, size=(N_HIDDEN,N_OUTPUTS)) # weight matrix 2 | shape (8,6)
    b1 = rng.uniform(-r, r, size=(N_HIDDEN,)) # bias matrix 1 | shape (8,)
    b2 = rng.uniform(-r, r, size=(N_OUTPUTS,)) # bias matrix 2 | shape (6,)

    return (w1, b1, w2, b2)

def forward(network, obs):
    # x @ W + b
    w1 = network[0]
    b1 = network[1]
    w2 = network[2]
    b2 = network[3]

    hidden = np.tanh(obs @ w1 + b1) # shape (8,)
    output = hidden @ w2 + b2 # shape (6,)
    action = int(np.argmax(output)) # int deciding highest action 
    return (hidden, action)