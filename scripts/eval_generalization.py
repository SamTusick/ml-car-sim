# python -m scripts.eval_generalization --name pop_200 --track assets/tracks/logic_track2.png --start-x X --start-y Y
# Evaluates saved final-generation genomes on a new track. No training happens here.

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

from car_sim.env import CarEnv
from car_sim.ga import evaluate
from car_sim.track import load_track

RESULTS_DIR = Path("results")


# Find every seed{N}_gen{gen}.npz in the experiment and return the sorted seed numbers.
def find_seeds(pop_dir, gen):
    seeds = []
    for path in pop_dir.glob(f"seed*_gen{gen}.npz"):
        seeds.append(int(path.name.split("_")[0].replace("seed", "")))
    return sorted(seeds)


# Load one saved generation: population (200, 110) and fitness_scores (200,).
def load_population(pop_dir, seed, gen):
    data = np.load(pop_dir / f"seed{seed}_gen{gen}.npz")
    return data["population"], data["fitness_scores"]


# Sanity check: the best genome must reproduce its saved fitness on the original track.
def sanity_check(pop_dir, seeds, gen):
    env = CarEnv()  # default track = the one used for training
    ok = True
    for seed in seeds:
        population, fitness_scores = load_population(pop_dir, seed, gen)
        best = int(np.argmax(fitness_scores))
        fitness, info = evaluate(population[best], env)
        match = np.isclose(fitness, fitness_scores[best], rtol=0, atol=1e-6)
        print(f"seed {seed}: saved {fitness_scores[best]:.4f}, recomputed {fitness:.4f}, "
              f"gates {info['gates_passed']}, {'OK' if match else 'MISMATCH'}")
        ok = ok and match
    env.close()
    return ok


# Evaluate every genome of every seed on the new track and return one dict per genome.
def evaluate_new_track(pop_dir, seeds, gen, track):
    env = CarEnv(track=track)
    rows = []
    for seed in seeds:
        population, fitness_scores = load_population(pop_dir, seed, gen)
        for i, genome in enumerate(population):
            fitness, info = evaluate(genome, env)
            rows.append({
                "seed": seed,
                "genome_index": i,
                "train_fitness": float(fitness_scores[i]),
                "fitness": fitness,
                "gates_passed": info["gates_passed"],
                "finished": int(info["finished"]),
            })
    env.close()
    return rows


def write_rows(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# Print per-seed and overall results. The best genome is the row with the top train_fitness.
def print_summary(pop_dir, seeds, gen, rows):
    print(f"\n{'seed':>4} {'best gates':>10} {'best finished':>13} {'pop finish rate':>16} {'unique genomes':>15}")
    best_finish = 0
    total_finish = 0
    total_n = 0
    for seed in seeds:
        seed_rows = [r for r in rows if r["seed"] == seed]
        best_row = max(seed_rows, key=lambda r: r["train_fitness"])  # first max wins, like argmax
        n_fin = sum(r["finished"] for r in seed_rows)
        population, _ = load_population(pop_dir, seed, gen)
        n_unique = len(np.unique(population, axis=0))
        print(f"{seed:>4} {best_row['gates_passed']:>10} {best_row['finished']:>13} "
              f"{n_fin:>8}/{len(seed_rows):<7} {n_unique:>15}")
        best_finish += best_row["finished"]
        total_finish += n_fin
        total_n += len(seed_rows)
    print(f"\nbest genomes that finish the new track: {best_finish}/{len(seeds)}")
    print(f"finish rate over all final populations: {total_finish}/{total_n} = {total_finish / total_n:.1%}")


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate saved GA genomes on a new track.")
    parser.add_argument("--name", required=True, help="experiment folder under results/, e.g. pop_200")
    parser.add_argument("--track", required=True, help="path to the new logic track PNG")
    parser.add_argument("--start-x", type=float, required=True, help="car start x on the new track")
    parser.add_argument("--start-y", type=float, required=True, help="car start y on the new track")
    parser.add_argument("--start-angle", type=float, default=0, help="car start angle in degrees (0 = up)")
    parser.add_argument("--gen", type=int, default=49, help="saved generation to load")
    return parser.parse_args()


def main():
    args = parse_args()
    pop_dir = RESULTS_DIR / args.name / "populations"
    seeds = find_seeds(pop_dir, args.gen)
    if not seeds:
        sys.exit(f"No seed*_gen{args.gen}.npz files in {pop_dir}")

    print("Sanity check on the original track:")
    if not sanity_check(pop_dir, seeds, args.gen):
        sys.exit("Saved fitness was NOT reproduced. Stopping before the new track.")

    track = load_track(args.track, (args.start_x, args.start_y), args.start_angle)
    rows = evaluate_new_track(pop_dir, seeds, args.gen, track)

    out_dir = RESULTS_DIR / args.name / "generalization"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{Path(args.track).stem}_genomes.csv"
    write_rows(out_file, rows)
    print(f"\nsaved {len(rows)} rows to {out_file}")

    print_summary(pop_dir, seeds, args.gen, rows)


if __name__ == "__main__":
    main()
