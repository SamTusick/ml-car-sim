import pygame

# pygame setup
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_middle_x = SCREEN_WIDTH / 2
screen_middle_y = SCREEN_HEIGHT / 2

clock = pygame.time.Clock()
running = True
dt = 0      

# Object Setup
rect1 = pygame.Rect(screen_middle_x,screen_middle_y,10,20)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("red")

    # Read keyboard input 
    keys = pygame.key.get_pressed()

    # Arrow Keys Movement   
    if keys[pygame.K_UP]:
        rect1.y -= 300 * dt
    if keys[pygame.K_DOWN]:
        rect1.y += 300 * dt
    if keys[pygame.K_LEFT]:
        rect1.x -= 300 * dt
    if keys[pygame.K_RIGHT]:
        rect1.x += 300 * dt

    if rect1.y > SCREEN_HEIGHT or rect1.x > SCREEN_WIDTH or rect1.y < 0 or rect1.x < 0:
            rect1.x, rect1.y = screen_middle_x, screen_middle_y

    pygame.draw.rect(screen, "white", rect1)

    pygame.display.update()

    # If 'q' gets pressed close game
    if keys[pygame.K_q]:
        running = False

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()