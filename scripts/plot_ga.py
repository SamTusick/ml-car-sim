"""Plot GA training curves for any number of seeds.

Run from the repo root:  python -m scripts.plot_ga
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTS_DIR = Path("results")
MANY_SEEDS = 10  # above this, use thinner lines and a compact legend


def load_runs(exp_dir):
    """Return {seed: DataFrame} sorted numerically by seed, or {} if no files."""
    runs = {}
    for path in exp_dir.glob("ga_seed*.csv"):
        df = pd.read_csv(path)
        if df.empty:
            continue
        seed = int(df["seed"].iloc[0])
        runs[seed] = df.sort_values("generation").reset_index(drop=True)
    return dict(sorted(runs.items()))


def make_colors(seeds):
    """Map each seed to a color; the same seed gets the same color everywhere."""
    n = len(seeds)
    if n <= 10:
        cmap = plt.get_cmap("tab10")
        return {s: cmap(i) for i, s in enumerate(seeds)}
    if n <= 20:
        cmap = plt.get_cmap("tab20")
        return {s: cmap(i) for i, s in enumerate(seeds)}
    cmap = plt.get_cmap("viridis")
    return {s: cmap(i / (n - 1)) for i, s in enumerate(seeds)}


def plot_metric(ax, runs, column, colors, median=False):
    """Draw one line per seed for `column`, optionally the median across seeds."""
    many = len(runs) > MANY_SEEDS
    alpha = 0.7
    width = 0.8 if many else 1.5
    for seed, df in runs.items():
        ax.plot(df["generation"], df[column], color=colors[seed],
                alpha=alpha, linewidth=width, label=f"seed {seed}")
    if median:
        # Align runs of different length by generation, then take the median.
        all_rows = pd.concat(runs.values())
        med = all_rows.groupby("generation")[column].median()
        ax.plot(med.index, med.values, color="black", linewidth=3,
                label="median", zorder=10)
    ax.grid(alpha=0.3)


def summarize(runs):
    """Build a per-seed summary table (DataFrame)."""
    rows = []
    for seed, df in runs.items():
        last = df.iloc[-1]
        finished = df[df["finished_count"] > 0]
        first_fin = int(finished["generation"].iloc[0]) if len(finished) else "never"
        rows.append({
            "seed": seed,
            "final_best_fitness": last["best_fitness"],
            "final_mean_fitness": last["mean_fitness"],
            "max_gates_passed": df["best_gates_passed"].max(),
            "first_gen_finished_above_0": first_fin,
            "final_gap": last["best_fitness"] - last["mean_fitness"],
        })
    return pd.DataFrame(rows)


def plot_experiment(exp_dir, show=True):
    """Plot every seed in exp_dir and save the PNG there. Called by train_ga too."""
    out_path = exp_dir / "ga_seeds_comparison.png"

    runs = load_runs(exp_dir)
    if not runs:
        print(f"No files matching {exp_dir}/ga_seed*.csv were found. "
              "Run scripts/train_ga.py first, from the repo root.")
        return

    seeds = list(runs)
    n = len(seeds)
    colors = make_colors(seeds)

    # Figure grows modestly with the number of seeds (capped).
    scale = min(n, 30)
    fig, axes = plt.subplots(2, 2, sharex=True,
                             figsize=(11 + 0.05 * scale, 8 + 0.05 * scale))
    ax_best, ax_mean, ax_gates, ax_fin = axes.ravel()

    # Best fitness per generation, one line per seed, plus median across seeds.
    plot_metric(ax_best, runs, "best_fitness", colors, median=True)
    ax_best.set_title("Best fitness per generation")
    ax_best.set_ylabel("Best fitness (symlog)")

    # Mean fitness per generation, one line per seed, plus median across seeds.
    plot_metric(ax_mean, runs, "mean_fitness", colors, median=True)
    ax_mean.set_title("Mean fitness per generation")
    ax_mean.set_ylabel("Mean fitness (symlog)")

    # Fitness spans about -230 to 6000. Symlog is linear near zero (|y| < 400)
    # so low seeds near 360 stay distinguishable, and logarithmic above it so
    # seeds that reach 6000 fit on the same axis.
    for ax in (ax_best, ax_mean):
        ax.set_yscale("symlog", linthresh=400)

    # Track gates passed by the best car of each generation.
    plot_metric(ax_gates, runs, "best_gates_passed", colors)
    ax_gates.set_title("Best gates passed per generation")
    ax_gates.set_ylabel("Gates passed by best car")

    # Number of cars that completed the lap in each generation.
    plot_metric(ax_fin, runs, "finished_count", colors)
    ax_fin.set_title("Cars finishing the lap per generation")
    ax_fin.set_ylabel("Finished count")

    for ax in (ax_gates, ax_fin):
        ax.set_xlabel("Generation")

    # One shared legend outside the plots, compact when there are many seeds.
    handles, labels = ax_best.get_legend_handles_labels()
    ncol = 1 if n <= MANY_SEEDS else int(np.ceil(n / 12))
    fig.legend(handles, labels, loc="center left", bbox_to_anchor=(1.0, 0.5),
               ncol=ncol, fontsize="small" if n > MANY_SEEDS else "medium",
               title="Run", frameon=False)

    fig.suptitle(f"GA training across {n} seed{'s' if n != 1 else ''}")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved {out_path}")

    table = summarize(runs)
    print()
    print(table.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    k = int((table["first_gen_finished_above_0"] != "never").sum())
    print(f"\n{k} of {n} seeds finished the lap at least once")

    if show:
        plt.show()
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="experiment folder under results/")
    args = parser.parse_args()
    plot_experiment(RESULTS_DIR / args.name)


if __name__ == "__main__":
    main()
