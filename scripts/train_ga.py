import csv
from pathlib import Path

import numpy as np
from tqdm import tqdm

from car_sim.env import CarEnv
from car_sim.network import make_network
from car_sim.ga import to_vector, evaluate, next_generation

SEED = 2
POP_SIZE = 50
N_GENERATIONS = 50
R = 10  
OUT_FILE = Path(f"results/ga_seed{SEED}.csv")

def main():
    rng = np.random.default_rng(SEED)   # one rng, passed down everywhere
    env = CarEnv()                      # headless
    rows = []

    # generation 0, a list of POP_SIZE vectors of shape (110,)
    population = [to_vector(make_network(rng, R)) for _ in range(POP_SIZE)]

    for generation in tqdm(range(N_GENERATIONS)):
        # one score per genome, same order as population
        results = [evaluate(genome, env) for genome in population]
        fitness_scores = [r[0] for r in results]
        infos = [r[1] for r in results]
        #print([type(s) for s in fitness_scores][:5], fitness_scores[:2])

        rows.append({
            "seed": SEED,
            "generation": generation,
            "best_fitness": max(fitness_scores),
            "mean_fitness": float(np.mean(fitness_scores)),
            "worst_fitness": min(fitness_scores),
            "best_gates_passed": max(i["gates_passed"] for i in infos),
            "finished_count": sum(i["finished"] for i in infos),
        })

        # the next generation
        population = next_generation(population, fitness_scores, rng)

    env.close()

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved to {OUT_FILE}")


if __name__ == "__main__":
    main()