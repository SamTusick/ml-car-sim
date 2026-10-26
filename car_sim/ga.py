# Genetic Algorithm 
import numpy as np
from .network import N_INPUTS, N_HIDDEN, N_OUTPUTS

def to_network(vector):
    # break vector into each parameter 
    # still 1-D arrays
    # using input = 6, hidden= 8, output=6
    w1_end =  N_INPUTS*N_HIDDEN
    b1_end = w1_end + N_HIDDEN
    w2_end = b1_end + (N_HIDDEN * N_OUTPUTS)
    w1 = vector[: w1_end] # [0:48]
    b1 = vector[w1_end: b1_end] # [48:56]
    w2 = vector[b1_end: w2_end] # [56:104]
    b2 = vector[w2_end: w2_end + N_OUTPUTS] # [104:110]

    # reshape each parameter
    w1 = np.reshape(w1, (N_INPUTS, N_HIDDEN))
    b1 = np.reshape(b1, (N_HIDDEN,))
    w2 = np.reshape(w2, (N_HIDDEN, N_OUTPUTS))
    b2 = np.reshape(b2, (N_OUTPUTS))

    return (w1,b1,w2,b2)

def to_vector(network):
    # get all parameter arrays into 1-d arrays
    w1_flat = np.ravel(network[0])
    b1_flat = np.ravel(network[1])
    w2_flat = np.ravel(network[2])
    b2_flat = np.ravel(network[3])

    # combine all arrays into one vector 
    vector = np.concatenate((w1_flat,b1_flat,w2_flat,b2_flat))

    return vector # shape (110,)

def evaluate(genome, env):
    return 

def select_parents(population, fitness_scores):
    return

def crossover(a,b,rng):
    return

def mutate(child, rng):
    return 

def next_generation(populatioin, fitness_scores):
    return

