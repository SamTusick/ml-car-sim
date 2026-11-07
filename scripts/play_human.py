import argparse
import pygame
from car_sim.env import CarEnv
from car_sim.track import load_track

# Movement Constant 
controls_to_actions = {
    (False, False, False): 0,
    (True,  False, False): 1,
    (True,  True,  False): 2,
    (True,  False, True): 3,
    (False, True,  False): 4,
    (False, False, True): 5,
    # Used for human testing but not need in model 
    (False, True, True): 0,
    (True, True, True): 1
}
UP = pygame.K_UP
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT

def parse_args():
    parser = argparse.ArgumentParser(description="Drive a track by hand.")
    parser.add_argument("--track", default=None, help="logic track PNG, default is track 1")
    parser.add_argument("--start-x", type=float, default=30)
    parser.add_argument("--start-y", type=float, default=630)
    parser.add_argument("--start-angle", type=float, default=0)
    parser.add_argument("--show-reward", action="store_true", help="print the reward every step")
    return parser.parse_args()

def main():
    args = parse_args()
    track = None
    if args.track is not None:
        track = load_track(args.track, (args.start_x, args.start_y), args.start_angle)
    env = CarEnv(render_mode='human', track=track)
    clock = pygame.time.Clock()
    running = True

    env.reset()
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # click on the window to print the pixel, and the matching car top-left (36px car)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                print(f"clicked pixel ({mx}, {my}) -> start_pos for a car centered here: ({mx - 18}, {my - 18})")

        # Read keyboard input
        keys = pygame.key.get_pressed()
        controls = (keys[UP], keys[LEFT], keys[RIGHT])
        action = controls_to_actions[controls]

        _, reward, terminated, truncated, info = env.step(action)
        if args.show_reward:
            print(f"reward: {reward:.4f}")

        if terminated or truncated:
            print(f"episode over: steps={info['steps']}, "
                  f"gates_passed={info['gates_passed']}, "
                  f"finished={info['finished']}, truncated={truncated}")
            env.reset()

        # If 'q' gets pressed close game
        if keys[pygame.K_q]:
            running = False

        clock.tick(60)

    env.close()

if __name__ == "__main__":
    main()
