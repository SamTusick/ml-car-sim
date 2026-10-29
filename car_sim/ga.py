# Genetic Algorithm 
import numpy as np
from .network import N_INPUTS, N_HIDDEN, N_OUTPUTS, forward
import math

MUTATION_RATE = 0.1     # p: chance of each gene mutating
SIGMA = 0.1     # std dev of the Guassian step

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
    done = False
    curr_reward = 0.0
    # convert genome to network
    net = to_network(genome)
    # reset the env
    # gather observations
    obs, _ = env.reset()
    # Loop: feed the observation to forward, pass action to env.step
        # add up the reward
        # stop whem episode ends
    while not done:
        _,action = forward(net, obs)
        obs, reward,terminated,truncated,info = env.step(action)    # returns self._get_obs(), reward, terminated, truncated, self._get_info()
        curr_reward += reward
        if terminated or truncated:
            done = True
    return curr_reward, info

def select_parents(population, fitness_scores):
    # sort fitness scores but keep index using argsort
    order = np.argsort(fitness_scores)

    # select number of desired parents
    top_percent = 0.25
    n_elite = 2

    n_parents = math.ceil(len(population) * top_percent)

    # find index of top n_parents
    parent_pool = order[len(population) - n_parents: len(population)]

    # in reverse rank order
    genome_list = []

    for i in parent_pool:
        genome_list.append(population[i])

    # find elite parent genomes
    elite_parents = genome_list[len(genome_list) - n_elite : len(genome_list)] 

    return genome_list, elite_parents

def crossover(a,b, rng):
    child = np.empty_like(a)
    # traverse every parameter in each parent 
    for i in range(len(a)):
        # flip a coin to decide whos gene to take
        choice = rng.integers(0,2)    # 0 = a , 1 = b
        # add selected gene to child
        if choice == 0:
            child[i] = a[i]
        else:
            child[i] = b[i]
    return child

def mutate(child, rng):
    # generate random floats, size of child shape
    mask = rng.random(child.shape) < MUTATION_RATE  # convert to bool array, ~10% True
    noise = rng.normal(0, SIGMA, child.shape)   # calculate Guassian number
    mutated = child + mask * noise  # build a new array of the mutated genes if chosen 
    return mutated

def next_generation(population, fitness_scores, rng):
    new_population = []
    parent_pool, elites = select_parents(population=population, fitness_scores=fitness_scores)

    for elite in elites:
        new_population.append(elite.copy()) # new generation holds its own memory and shares nothing with the old population

    while len(new_population) < len(population):
        # select parents
        parent_a = parent_pool[rng.integers(0, len(parent_pool))] 
        parent_b = parent_pool[rng.integers(0, len(parent_pool))]

        # get child
        child = crossover(parent_a, parent_b, rng)

        # mutate child
        child = mutate(child, rng)

        # append new child to new population
        new_population.append(child)

    return new_population

