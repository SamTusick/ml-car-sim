import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pygame
from tqdm import tqdm

from car_sim.env import CarEnv
from car_sim.car import CAR
from car_sim.track import LOGIC_TRACK
from car_sim.network import forward
from car_sim.ga import to_network
from car_sim.helper_functs import blit_rotate_center

RESULTS_DIR = Path("results")
FITNESS_TOL = 1e-9
OUTCOMES = ["crash", "finish", "timeout"]   # index stored in the cache
NORMAL_ALPHA = 110
ENDED_ALPHA = 50
CHAMP_ALPHA = 255
CHAMP_ENDED_ALPHA = 120
CHAMP_COLOR = (255, 200, 0)
SPEED_RANGE = (1, 8)   # min and max frames per tick


# List the seed<N>_gen<G>.npz files that exist for one seed, as sorted generation numbers.
def available_gens(pop_dir, seed):
    gens = []
    for path in pop_dir.glob(f"seed{seed}_gen*.npz"):
        m = re.fullmatch(rf"seed{seed}_gen(\d+)\.npz", path.name)
        if m:
            gens.append(int(m.group(1)))
    return sorted(gens)


# Load the saved population and fitness scores, or exit with a message listing what exists.
def load_population(pop_dir, seed, gen):
    gens = available_gens(pop_dir, seed)
    if gen == "last":
        if not gens:
            sys.exit(f"No saved populations for seed {seed} in {pop_dir}.")
        gen = gens[-1]
    else:
        gen = int(gen)
    path = pop_dir / f"seed{seed}_gen{gen}.npz"
    if not path.exists():
        found = ", ".join(f"seed{seed}_gen{g}.npz" for g in gens) or "none"
        sys.exit(f"File not found: {path}\nFiles that exist for seed {seed}: {found}")
    with np.load(path) as data:
        return data["population"], data["fitness_scores"], gen


# Run one genome headless like evaluate() and record poses, reward, info and how it ended.
def record_trajectory(genome, env):
    net = to_network(genome)
    obs, _ = env.reset()
    poses = [(env.car.x, env.car.y, env.car.angle)]
    total = 0.0
    done = False
    while not done:
        _, action = forward(net, obs)
        obs, reward, terminated, truncated, info = env.step(action)
        total += reward
        poses.append((env.car.x, env.car.y, env.car.angle))
        done = terminated or truncated
    if info["finished"]:
        outcome = "finish"
    elif terminated:
        outcome = "crash"
    else:
        outcome = "timeout"
    return {
        "poses": np.array(poses, dtype=np.float64),
        "reward": total,
        "gates_passed": int(info["gates_passed"]),
        "finished": bool(info["finished"]),
        "outcome": outcome,
    }


# Record every genome, showing a progress bar.
def record_all(population, env):
    return [record_trajectory(g, env) for g in tqdm(population, desc="recording")]


# Write trajectories to one npz, padding poses to the longest episode.
def save_cache(path, trajs, fitness_scores):
    path.parent.mkdir(parents=True, exist_ok=True)
    lengths = np.array([len(t["poses"]) for t in trajs], dtype=np.int64)
    poses = np.zeros((len(trajs), lengths.max(), 3), dtype=np.float64)
    for i, t in enumerate(trajs):
        poses[i, : lengths[i]] = t["poses"]
    np.savez_compressed(
        path,
        poses=poses,
        lengths=lengths,
        rewards=np.array([t["reward"] for t in trajs]),
        gates_passed=np.array([t["gates_passed"] for t in trajs]),
        finished=np.array([t["finished"] for t in trajs]),
        outcomes=np.array([OUTCOMES.index(t["outcome"]) for t in trajs]),
        fitness_scores=fitness_scores,
    )


# Load cached trajectories, or return None if missing or not matching the saved fitness.
def load_cache(path, fitness_scores):
    if not path.exists():
        return None
    with np.load(path) as d:
        if d["fitness_scores"].shape != fitness_scores.shape or not np.array_equal(
            d["fitness_scores"], fitness_scores
        ):
            return None
        return [
            {
                "poses": d["poses"][i, : d["lengths"][i]],
                "reward": float(d["rewards"][i]),
                "gates_passed": int(d["gates_passed"][i]),
                "finished": bool(d["finished"][i]),
                "outcome": OUTCOMES[int(d["outcomes"][i])],
            }
            for i in range(len(d["lengths"]))
        ]


# Print a warning if any recorded reward differs from the saved fitness.
def check_determinism(trajs, fitness_scores):
    rewards = np.array([t["reward"] for t in trajs])
    bad = np.flatnonzero(np.abs(rewards - fitness_scores) > FITNESS_TOL)
    if len(bad):
        print(f"WARNING: {len(bad)} genome(s) differ from saved fitness by more than {FITNESS_TOL}: "
              f"indices {bad.tolist()}")
    else:
        print(f"Determinism check passed: all {len(rewards)} rewards match saved fitness.")


# Return a copy of the image, optionally tinted to a solid color, with a given alpha.
def tint_image(img, color=None, alpha=255):
    out = img.copy()
    if color is not None:
        out.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
        out.fill((*color, 0), special_flags=pygame.BLEND_RGB_ADD)
    out.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return out


# Draw the track, all cars at the given step, and the HUD. Returns the number still driving.
def draw_frame(screen, font, trajs, step, champ, images, seed, gen, best_fit, n_finished):
    screen.blit(LOGIC_TRACK, (0, 0))
    driving = 0
    order = [i for i in range(len(trajs)) if i != champ] + [champ]   # champion on top
    for i in order:
        poses = trajs[i]["poses"]
        last = len(poses) - 1
        ended = step >= last
        if not ended:
            driving += 1
        x, y, angle = poses[min(step, last)]
        key = ("champ" if i == champ else "normal", ended)
        blit_rotate_center(screen, images[key], (x, y), angle)

    lines = [
        f"seed {seed}   generation {gen}",
        f"step {step}",
        f"driving {driving} / {len(trajs)}",
        f"best fitness {best_fit:.1f}",
        f"finished lap {n_finished}",
    ]
    for n, text in enumerate(lines):
        surf = font.render(text, True, (255, 255, 255), (0, 0, 0))
        screen.blit(surf, (8, 8 + n * 22))
    if driving == 0:
        msg = font.render("all episodes ended, press R to replay", True, (255, 255, 255), (0, 0, 0))
        screen.blit(msg, (8, 8 + len(lines) * 22 + 8))
    return driving


# Parse command line arguments.
def parse_args():
    parser = argparse.ArgumentParser(description="Play back every genome of one generation at once.")
    parser.add_argument("--name", required=True, help='experiment name, e.g. "baseline"')
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--gen", required=True, help='generation number or "last"')
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--no-cache", action="store_true", help="ignore and do not write the trajectory cache")
    return parser.parse_args()


def main():
    args = parse_args()
    exp_dir = RESULTS_DIR / args.name
    population, fitness_scores, gen = load_population(exp_dir / "populations", args.seed, args.gen)

    cache_path = exp_dir / "trajectories" / f"seed{args.seed}_gen{gen}.npz"
    trajs = None if args.no_cache else load_cache(cache_path, fitness_scores)
    if trajs is None:
        env = CarEnv()
        trajs = record_all(population, env)
        env.close()
        check_determinism(trajs, fitness_scores)
        if not args.no_cache:
            save_cache(cache_path, trajs, fitness_scores)
            print(f"cached to {cache_path}")
    else:
        print(f"loaded cached trajectories from {cache_path}")

    champ = int(np.argmax(fitness_scores))
    best_fit = float(fitness_scores[champ])
    n_finished = sum(t["finished"] for t in trajs)
    max_steps = max(len(t["poses"]) for t in trajs) - 1

    pygame.init()
    screen = pygame.display.set_mode(LOGIC_TRACK.get_size())
    pygame.display.set_caption(f"{args.name} seed {args.seed} gen {gen}")
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    images = {
        ("normal", False): tint_image(CAR, None, NORMAL_ALPHA),
        ("normal", True): tint_image(CAR, None, ENDED_ALPHA),
        ("champ", False): tint_image(CAR, CHAMP_COLOR, CHAMP_ALPHA),
        ("champ", True): tint_image(CAR, CHAMP_COLOR, CHAMP_ENDED_ALPHA),
    }

    step, speed, paused, running = 0, 1, False, True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    step = 0
                elif event.key == pygame.K_UP:
                    speed = min(speed + 1, SPEED_RANGE[1])
                elif event.key == pygame.K_DOWN:
                    speed = max(speed - 1, SPEED_RANGE[0])

        driving = draw_frame(screen, font, trajs, step, champ, images,
                             args.seed, gen, best_fit, n_finished)
        pygame.display.flip()
        if not paused and step < max_steps:
            step = min(step + speed, max_steps)
        clock.tick(args.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
