# Genetic Algorithm 
import numpy as np

def to_vector(network):
    w1_flat = np.ravel(network[0])
    b1_flat = np.ravel(network[1])
    w2_flat = np.ravel(network[2])
    b2_flat = np.ravel(network[3])

    vector = np.concatenate((w1_flat,b1_flat,w2_flat,b2_flat))
    return vector

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

