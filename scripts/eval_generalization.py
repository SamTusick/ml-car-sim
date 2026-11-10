# python -m scripts.eval_generalization --name multi_12 --train-tracks 1,2 --test-tracks 3,4
# Evaluates saved final-generation genomes on train and held-out tracks. No training happens here.
# The champion of each seed is chosen from the saved training fitness only, never from test results.

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

from car_sim.env import CarEnv
from car_sim.ga import evaluate, evaluate_on_tracks
from car_sim.track import load_tracks, get_start_pose
from scripts.train_ga import parse_seeds

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


# Champion of a seed = index of the top saved training fitness (first max wins, like argmax).
def champion_index(fitness_scores):
    return int(np.argmax(fitness_scores))


# Sanity check: each champion must reproduce its saved aggregate fitness on the training tracks.
def sanity_check(pop_dir, seeds, gen, train_envs):
    ok = True
    for seed in seeds:
        population, fitness_scores = load_population(pop_dir, seed, gen)
        best = champion_index(fitness_scores)
        total, _, infos = evaluate_on_tracks(population[best], train_envs)
        match = np.isclose(total, fitness_scores[best], rtol=0, atol=1e-6)
        gates = sum(i["gates_passed"] for i in infos)
        print(f"seed {seed}: saved {fitness_scores[best]:.4f}, recomputed {total:.4f}, "
              f"gates {gates}, {'OK' if match else 'MISMATCH'}")
        ok = ok and match
    return ok


# Evaluate every genome of every seed on every track and return one dict per (genome, track).
def evaluate_all(pop_dir, seeds, gen, track_ids, tracks, split):
    rows = []
    for track_id, track in zip(track_ids, tracks):
        env = CarEnv(track=track)
        start_pos, start_angle = track.start_pos, track.start_angle
        for seed in seeds:
            population, fitness_scores = load_population(pop_dir, seed, gen)
            best = champion_index(fitness_scores)
            for i, genome in enumerate(population):
                fitness, info = evaluate(genome, env)
                rows.append({
                    "seed": seed,
                    "genome_index": i,
                    "is_champion": int(i == best),
                    "train_fitness": float(fitness_scores[i]),
                    "split": split,
                    "track": track_id,
                    "fitness": fitness,
                    "gates_passed": info["gates_passed"],
                    "finished": int(info["finished"]),
                    "start_x": start_pos[0],
                    "start_y": start_pos[1],
                    "start_angle": start_angle,
                })
        env.close()
    return rows


def write_rows(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


# Print one line per seed champion per track, then finish counts per track and per split.
def print_summary(seeds, rows, track_ids_by_split):
    champs = [r for r in rows if r["is_champion"]]
    print(f"\n{'seed':>4} {'split':>5} {'track':>5} {'gates':>5} {'finished':>8} {'fitness':>10}")
    for seed in seeds:
        for r in champs:
            if r["seed"] == seed:
                print(f"{seed:>4} {r['split']:>5} {r['track']:>5} {r['gates_passed']:>5} "
                      f"{r['finished']:>8} {r['fitness']:>10.1f}")
    print("\nchampion finishes per track, and finish rate over all final populations:")
    for split, ids in track_ids_by_split.items():
        for track_id in ids:
            c = [r for r in champs if r["split"] == split and r["track"] == track_id]
            p = [r for r in rows if r["split"] == split and r["track"] == track_id]
            c_fin = sum(r["finished"] for r in c)
            p_fin = sum(r["finished"] for r in p)
            print(f"  {split} track {track_id}: champions {c_fin}/{len(c)}, "
                  f"population {p_fin}/{len(p)} = {p_fin / len(p):.1%}")


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate saved GA genomes on train and held-out tracks.")
    parser.add_argument("--name", required=True, help="experiment folder under results/")
    parser.add_argument("--train-tracks", default="1,2", help='tracks used in training, e.g. "1,2"')
    parser.add_argument("--test-tracks", default="3,4", help='held-out tracks, e.g. "3,4"')
    parser.add_argument("--gen", type=int, default=49, help="saved generation to load")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        train_ids = parse_seeds(args.train_tracks)
        test_ids = parse_seeds(args.test_tracks)
    except ValueError as e:
        sys.exit(f"Invalid track list: {e}")
    if set(train_ids) & set(test_ids):
        sys.exit("Train and test tracks overlap; held-out tracks must not be used in training.")

    # fail early with a clear message if a start pose or image is missing
    try:
        for track_id in train_ids + test_ids:
            get_start_pose(track_id)
        train_tracks = load_tracks(train_ids)
        test_tracks = load_tracks(test_ids)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"Track setup failed: {e}")

    pop_dir = RESULTS_DIR / args.name / "populations"
    seeds = find_seeds(pop_dir, args.gen)
    if not seeds:
        sys.exit(f"No seed*_gen{args.gen}.npz files in {pop_dir}")

    print(f"Sanity check on training tracks {train_ids}:")
    train_envs = [CarEnv(track=t) for t in train_tracks]
    ok = sanity_check(pop_dir, seeds, args.gen, train_envs)
    for env in train_envs:
        env.close()
    if not ok:
        sys.exit("Saved fitness was NOT reproduced. Stopping before the held-out tracks.")

    rows = evaluate_all(pop_dir, seeds, args.gen, train_ids, train_tracks, "train")
    rows += evaluate_all(pop_dir, seeds, args.gen, test_ids, test_tracks, "test")

    out_dir = RESULTS_DIR / args.name / "generalization"
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"train{'-'.join(map(str, train_ids))}_test{'-'.join(map(str, test_ids))}"
    write_rows(out_dir / f"{tag}_genomes.csv", rows)
    champs = [r for r in rows if r["is_champion"]]
    write_rows(out_dir / f"{tag}_champions.csv", champs)
    print(f"\nsaved {len(rows)} genome rows and {len(champs)} champion rows to {out_dir}")

    print_summary(seeds, rows, {"train": train_ids, "test": test_ids})


if __name__ == "__main__":
    main()
