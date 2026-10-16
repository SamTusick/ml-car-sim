import pygame
from car_sim.env import CarEnv

# Movement Constant 
controls_to_actions = {
    (False, False, False): 0,
    (True,  False, False): 1,
    (True,  True,  False): 2,
    (True,  False, True): 3,
    (False, True,  False): 4,
    (False, False, True): 5,
    (False, True, True): 0,
    (True, True, True): 1
}
UP = pygame.K_UP
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT

def main():
    env = CarEnv(render_mode='human')
    clock = pygame.time.Clock()
    running = True

    env.reset()
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read keyboard input 
        keys = pygame.key.get_pressed()
        controls = (keys[UP], keys[LEFT], keys[RIGHT])
        action = controls_to_actions[controls]

        _, _, terminated, truncated, info = env.step(action)

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
