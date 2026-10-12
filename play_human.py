import pygame
from environment.game_env import Env

# Movement Constant 
UP = pygame.K_UP
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT

def main():
    env = Env()
    clock = pygame.time.Clock()
    running = True

    while running:
        env.render()
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read keyboard input 
        keys = pygame.key.get_pressed()
        env.step(up=keys[UP], left=keys[LEFT], right=keys[RIGHT])

        # If 'q' gets pressed close game
        if keys[pygame.K_q]:
            running = False

        clock.tick(60)

    env.close()

if __name__ == "__main__":
    main()
