"""Per-seed summary of a GA experiment folder (scaffolding, no algorithm logic).

Usage: python scripts/summarize_baseline.py results/baseline10

Reads ga_seed*.csv, prints one row per seed, writes summary.csv next to them,
and saves per_seed_finishers.png with every seed visible and no median line.
"""
import csv
import sys
from pathlib import Path


# Load one seed's CSV into a list of dicts with numeric fields.
def load_seed(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "generation": int(r["generation"]),
                "best_fitness": float(r["best_fitness"]),
                "best_gates_passed": int(r["best_gates_passed"]),
                "finished_count": int(r["finished_count"]),
            })
    return rows


# Reduce one seed's rows to the metrics we report.
def summarize(seed, rows):
    first = next((r["generation"] for r in rows if r["finished_count"] > 0), None)
    last = rows[-1]
    return {
        "seed": seed,
        "first_finisher_gen": first,                # None means never finished
        "finisher_at_gen0": first == 0,             # init luck, not evolution
        "final_finished_count": last["finished_count"],
        "final_gates": last["best_gates_passed"],
        "final_best_fitness": round(last["best_fitness"], 2),
        "n_generations": len(rows),
    }


def main():
    folder = Path(sys.argv[1])
    paths = sorted(folder.glob("ga_seed*.csv"), key=lambda p: int(p.stem.replace("ga_seed", "")))
    if not paths:
        sys.exit(f"No ga_seed*.csv files in {folder}")

    data = {int(p.stem.replace("ga_seed", "")): load_seed(p) for p in paths}
    summaries = [summarize(s, rows) for s, rows in data.items()]

    header = list(summaries[0].keys())
    print("  ".join(f"{h:>20}" for h in header))
    for s in summaries:
        print("  ".join(f"{str(s[h]):>20}" for h in header))

    n = len(summaries)
    finished = [s for s in summaries if s["first_finisher_gen"] is not None]
    evolved = [s for s in finished if not s["finisher_at_gen0"]]
    print(f"\nseeds with any finisher: {len(finished)}/{n}")
    print(f"seeds where a finisher evolved from a non-finishing gen 0: {len(evolved)}/{n}")

    with open(folder / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(summaries)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed, skipping plot")
        return

    # Small multiples so overlapping stuck seeds are still individually visible.
    fig, axes = plt.subplots(2, 5, figsize=(14, 5), sharex=True, sharey=True)
    for ax, (seed, rows) in zip(axes.flat, sorted(data.items())):
        ax.plot([r["generation"] for r in rows], [r["finished_count"] for r in rows])
        ax.set_title(f"seed {seed}")
    fig.supxlabel("Generation")
    fig.supylabel("Cars finishing")
    fig.tight_layout()
    fig.savefig(folder / "per_seed_finishers.png", dpi=120)
    print(f"saved {folder / 'per_seed_finishers.png'}")


if __name__ == "__main__":
    main()