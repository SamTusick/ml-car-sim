# Used to determine the range for generation 0. Generation will most likely stall and will not allow for progression. IN order to fix this we add a randomness to the first
# generation. 

import numpy as np
from car_sim.network import make_network, forward

SEED = 0
N_NETWORKS = 50
N_INPUTS = 6
N_HIDDEN = 8
N_OUTPUTS = 6
K_OBS = 20
R_VALUES = [0.001, 0.1, 1, 5, 7, 10, 100]

# Hypothesis, one row per r. NOTE: the "mean distinct" column was filled in AFTER the first
# run with K_OBS random observations, so it is a post-hoc explanation, not a blind prediction.
# mean distinct = mean over networks of distinct actions picked across K_OBS observations (1 to 6)
#   r        hidden mean |h|    mean distinct
#   0.001    near 0                1.0   Weights are so small that hidden ~ 0, so output ~ b2 and the argmax is the same for every observation.
#   0.1      near 0                1.3   Hidden is still small, but input-dependent output terms are big enough to flip the argmax when b2's top two entries are close.
#   1        mid                   2.0   Hidden is in tanh's linear range, so the input visibly shifts the outputs and a network typically switches between about two actions.
#   100      near 1                3.0   tanh saturates so hidden is nearly +/-1 and only changes where an input flips a unit's sign, giving a few discrete regions rather than all 6.


def run_for_r(r, rng):
    # K random observations in [0, 1], shared by all networks for this r
    observations = rng.uniform(0, 1, size=(K_OBS, N_INPUTS)).astype(np.float32)
    hidden_means = []
    distinct_counts = []
    for _ in range(N_NETWORKS):
        net = make_network(rng, r)
        actions = []
        for obs in observations:
            hidden, action = forward(net, obs)
            hidden_means.append(np.abs(hidden).mean())
            actions.append(action)
        distinct_counts.append(len(set(actions)))
    return float(np.mean(hidden_means)), float(np.mean(distinct_counts)), distinct_counts


def main():
    rng = np.random.default_rng(SEED)
    print(f"{'r':>8} {'mean|h|':>10} {'mean distinct':>14}  networks per distinct count (1-6)")
    for r in R_VALUES:
        mean_h, mean_distinct, distinct_counts = run_for_r(r, rng)
        hist = np.bincount(distinct_counts, minlength=N_OUTPUTS + 1)[1:]
        print(f"{r:>8} {mean_h:>10.4f} {mean_distinct:>14.2f}  {hist.tolist()}")


if __name__ == "__main__":
    main()
