# python -m scripts.sweep
import sys
from pathlib import Path

import car_sim.ga as ga
import scripts.train_ga as tg

SEEDS = "0-9"

# (experiment name, {constant: new value}). One change per entry.
RUNS = [
    ("pool_frac_0.5", {"POOL_FRAC": 0.5}),
    ("pop_100", {"POP_SIZE": 100}),
    ("pop_200", {"POP_SIZE": 200}),
]


def apply(overrides):
    saved = []
    for key, value in overrides.items():
        for module in (ga, tg):
            if hasattr(module, key):
                saved.append((module, key, getattr(module, key)))
                setattr(module, key, value)
    return saved


def restore(saved):
    for module, key, value in saved:
        setattr(module, key, value)


def main():
    for name, overrides in RUNS:
        if (Path("results") / name).exists():
            print(f"skip {name}, folder exists")
            continue
        saved = apply(overrides)
        sys.argv = ["train_ga", "--name", name, "--seeds", SEEDS]
        try:
            tg.main()
        finally:
            restore(saved)
        print(f"done {name}: {overrides}")


if __name__ == "__main__":
    main()