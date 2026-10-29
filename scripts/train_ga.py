import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from tqdm import tqdm

from scripts.plot_ga import plot_experiment
from car_sim.env import CarEnv
from car_sim.network import make_network
from car_sim.ga import (
    to_vector, evaluate, next_generation,
    SIGMA, MUTATION_RATE, POOL_FRAC, N_ELITE,  # POOL_FRAC and N_ELITE need the ga.py change
)

POP_SIZE = 50
N_GENERATIONS = 50
R = 10
RESULTS_DIR = Path("results")


# Parse "0,1,2,5", "0-9", or a mix like "0-3,7" into a sorted list of unique ints.
def parse_seeds(text):
    seeds = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            lo, hi = int(lo), int(hi)
            if lo > hi:
                raise ValueError(f"bad seed range: {part}")
            seeds.update(range(lo, hi + 1))
        else:
            seeds.add(int(part))
    if not seeds:
        raise ValueError("no seeds given")
    return sorted(seeds)


# Collect the tunable settings that go into every CSV row and into config.json.
def get_settings():
    return {
        "sigma": SIGMA,
        "mutation_rate": MUTATION_RATE,
        "pool_frac": POOL_FRAC,
        "n_elite": N_ELITE,
        "r": R,
        "pop_size": POP_SIZE,
        "n_generations": N_GENERATIONS,
    }


# Return the short git commit hash, or None if git is missing or fails.
def get_git_commit():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


# Write config.json once per experiment with settings, seeds, name, time and commit.
def write_config(exp_dir, name, seeds):
    config = {
        "name": name,
        **get_settings(),
        "crossover": "uniform",
        "mutation": "gaussian",
        "seeds": seeds,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": get_git_commit(),
    }
    with (exp_dir / "config.json").open("w") as f:
        json.dump(config, f, indent=2)


# Write one seed's rows to a CSV file, with a header.
def write_rows(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# Run one full GA for a single seed and return the per-generation rows.
def run_one_seed(seed):
    rng = np.random.default_rng(seed)   # one rng, passed down everywhere
    env = CarEnv()                      # headless, fresh per seed
    settings = get_settings()
    rows = []

    # generation 0, a list of POP_SIZE vectors of shape (110,)
    population = [to_vector(make_network(rng, R)) for _ in range(POP_SIZE)]

    for generation in tqdm(range(N_GENERATIONS), desc=f"seed {seed}"):
        # one score per genome, same order as population
        results = [evaluate(genome, env) for genome in population]
        fitness_scores = [r[0] for r in results]
        infos = [r[1] for r in results]

        rows.append({
            "seed": seed,
            "generation": generation,
            "best_fitness": max(fitness_scores),
            "mean_fitness": float(np.mean(fitness_scores)),
            "worst_fitness": min(fitness_scores),
            "best_gates_passed": max(i["gates_passed"] for i in infos),
            "finished_count": sum(i["finished"] for i in infos),
            **settings,
        })

        population = next_generation(population, fitness_scores, rng)

    env.close()
    return rows


# Parse command line arguments.
def parse_args():
    parser = argparse.ArgumentParser(description="Train the GA over several seeds.")
    parser.add_argument("--name", required=True, help='experiment name, e.g. "baseline"')
    parser.add_argument("--seeds", default="0,1,2", help='e.g. "0,1,2,5" or "0-9"')
    parser.add_argument("--hypothesis", default=None, help="optional note saved to hypothesis.txt")
    parser.add_argument("--overwrite", action="store_true",
                        help="allow writing into an experiment that already has results")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        seeds = parse_seeds(args.seeds)
    except ValueError as e:
        sys.exit(f"Invalid --seeds: {e}")

    exp_dir = RESULTS_DIR / args.name
    existing = sorted(exp_dir.glob("ga_seed*.csv")) if exp_dir.exists() else []
    if existing and not args.overwrite:
        sys.exit(
            f"Experiment '{args.name}' already has {len(existing)} result file(s) in {exp_dir}. "
            "Pick a new --name or pass --overwrite to replace them."
        )

    exp_dir.mkdir(parents=True, exist_ok=True)
    write_config(exp_dir, args.name, seeds)
    if args.hypothesis:
        (exp_dir / "hypothesis.txt").write_text(args.hypothesis + "\n")

    for seed in seeds:
        rows = run_one_seed(seed)
        out_file = exp_dir / f"ga_seed{seed}.csv"
        write_rows(out_file, rows)
        print(f"saved to {out_file}")

    # plot all seeds in the folder (headless, no window) and save the PNG beside the CSVs
    plot_experiment(exp_dir, show=False)


if __name__ == "__main__":
    main()
