# Watch ONE saved genome drive a track live, and print how its episode ended.
#
# python -m scripts.watch_genome --name pop_200 --seed 2 --track assets/tracks/logic_track2.png --start-x 111 --start-y 583
#
# --index picks a genome from the saved population. Default is the best one by saved (training) fitness.
# Controls: R replays the episode, Q or the window X quits.

import argparse

import numpy as np
import pygame

from car_sim.env import CarEnv
from car_sim.ga import to_network
from car_sim.network import forward
from car_sim.track import load_track


def parse_args():
    parser = argparse.ArgumentParser(description="Watch one saved genome drive.")
    parser.add_argument("--name", required=True, help="experiment folder under results/")
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--gen", type=int, default=49)
    parser.add_argument("--index", type=int, default=None, help="genome index, default is the best")
    parser.add_argument("--track", default=None, help="logic track PNG, default is track 1")
    parser.add_argument("--start-x", type=float, default=30)
    parser.add_argument("--start-y", type=float, default=630)
    parser.add_argument("--start-angle", type=float, default=0)
    parser.add_argument("--fps", type=int, default=60)
    return parser.parse_args()


# Drive one episode with the window open. Returns False if the user closed the window.
def run_episode(env, genome, fps, clock):
    net = to_network(genome)
    obs, _ = env.reset()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        _, action = forward(net, obs)
        obs, _, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        clock.tick(fps)

    how = "finished" if info["finished"] else ("timeout" if truncated else "crash")
    x, y = env.car.get_center()
    print(f"{how}: steps={info['steps']}, gates_passed={info['gates_passed']}, "
          f"car center=({x:.0f}, {y:.0f}), angle={env.car.angle:.0f}, speed={env.car.vel:.2f}")
    return True


def main():
    args = parse_args()
    data = np.load(f"results/{args.name}/populations/seed{args.seed}_gen{args.gen}.npz")
    index = int(np.argmax(data["fitness_scores"])) if args.index is None else args.index
    genome = data["population"][index]
    print(f"seed {args.seed}, genome {index}, saved fitness {data['fitness_scores'][index]:.1f}")

    track = None
    if args.track is not None:
        track = load_track(args.track, (args.start_x, args.start_y), args.start_angle)
    env = CarEnv(render_mode="human", track=track)
    clock = pygame.time.Clock()

    running = run_episode(env, genome, args.fps, clock)
    while running:
        # episode is over: wait for R (replay) or Q / close
        event = pygame.event.wait()
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            running = run_episode(env, genome, args.fps, clock)

    env.close()


if __name__ == "__main__":
    main()
