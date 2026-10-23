import csv
import statistics
from collections import Counter
from pathlib import Path

from tqdm import tqdm

from car_sim.env import CarEnv

N_EPISODES = 1000
SEED = 0
OUT_FILE = Path("results/random_baseline.csv")

# Hypothesis (write this BEFORE running):
# I expect 3000 steps, 0 gates, 0 finishes, because this is all random so these episodes are never learning only taking a 
# random action every step.


def main():
    env = CarEnv()                     # no render_mode, so it runs headless
    env.action_space.seed(SEED)        # the only randomness is the action sampler
    rows = []

    for episode in tqdm(range(N_EPISODES)):
        env.reset()
        done = False
        total_reward = 0.0
        while not done:
            action = env.action_space.sample()
            _, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated

        rows.append({
            "episode": episode,
            "total_reward": total_reward,
            "steps": info["steps"],
            "gates_passed": info["gates_passed"],
            "distance_to_next_gate": info["distance_to_next_gate"],
            "finished": info["finished"],
            "terminated": terminated,
            "truncated": truncated,
        })
    env.close()

    # save every episode so runs can be compared later
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # summary
    steps = [r["steps"] for r in rows]
    distances = [r["distance_to_next_gate"] for r in rows]
    gate_counts = Counter(r["gates_passed"] for r in rows)

    rewards = [r["total_reward"] for r in rows]

    print(f"episodes: {N_EPISODES}, seed: {SEED}")
    print(f"total reward: mean={statistics.mean(rewards):.2f}, "
          f"median={statistics.median(rewards):.2f}, stdev={statistics.stdev(rewards):.2f}, "
          f"min={min(rewards):.2f}, max={max(rewards):.2f}")
    print(f"steps: mean={statistics.mean(steps):.1f}, "
          f"median={statistics.median(steps):.1f}, "
          f"min={min(steps)}, max={max(steps)}")
    print("episodes per gates_passed:")
    for gates in sorted(gate_counts):
        print(f"  {gates} gates: {gate_counts[gates]}")
    print(f"finished: {sum(r['finished'] for r in rows)}")
    print(f"truncated: {sum(r['truncated'] for r in rows)}")
    print(f"final distance to next gate: min={min(distances):.1f}, max={max(distances):.1f}")
    print(f"saved to {OUT_FILE}")


if __name__ == "__main__":
    main()