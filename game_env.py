# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

rect1 = pygame.Rect(screen.get_width() / 2,screen.get_height() / 2 ,10,20)
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("red")

    pygame.draw.rect(screen, "white", rect1)

    # Read keyboard input 
    keys = pygame.key.get_pressed()

    # WASD
    if keys[pygame.K_w]:
        rect1.y -= 300 * dt
    if keys[pygame.K_s]:
        rect1.y += 300 * dt
    if keys[pygame.K_a]:
        rect1.x -= 300 * dt
    if keys[pygame.K_d]:
        rect1.x += 300 * dt

    # Arrow Keys    
    if keys[pygame.K_UP]:
        rect1.y -= 300 * dt
    if keys[pygame.K_DOWN]:
        rect1.y += 300 * dt
    if keys[pygame.K_LEFT]:
        rect1.x -= 300 * dt
    if keys[pygame.K_RIGHT]:
        rect1.x += 300 * dt

    # If 'q' gets pressed close game
    if keys[pygame.K_q]:
        running = False

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()