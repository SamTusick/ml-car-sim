import pygame
import math

# ------------- Functions -------------

def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(screen, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    screen.blit(rotated_image, new_rect.topleft)

# ------------- Constants -------------
# Assests
CAR = scale_image(pygame.image.load("assests/car.png"), 0.03)
TRACK = scale_image(pygame.image.load("assests/track1.png"), 1)

# Scren Constants 
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_MIDDLE_X = SCREEN_WIDTH / 2
SCREEN_MIDDLE_Y = SCREEN_HEIGHT / 2

# Movement Constant 
UP = pygame.K_UP
DOWN = pygame.K_DOWN
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT

# ------------- Pygame Setup -------------
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

class Car:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, screen):
        blit_rotate_center(screen, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()


class PlayerCar(Car):
    IMG = CAR
    START_POS = (SCREEN_MIDDLE_X, SCREEN_MIDDLE_Y)

def draw(screen, player_car):
    screen.blit(TRACK, (0,0))
    player_car.draw(screen)
    pygame.display.update()

my_car = PlayerCar(3,3)
clock = pygame.time.Clock()
running = True
dt = 0      

while running:
    draw(screen, my_car)
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read keyboard input 
    keys = pygame.key.get_pressed()
    moved = False

    # Arrow Keys Movement   
    if keys[UP]:
        #rect1.y -= VELOCITY * dt
        moved = True
        my_car.move_forward()
    if keys[LEFT]:
        #rect1.x -= VELOCITY * dt
        my_car.rotate(left=True)
    if keys[RIGHT]:
        #rect1.x += VELOCITY * dt
        my_car.rotate(right=True)

    if not moved:
        my_car.reduce_speed()

    # Boundry Handling
    if my_car.y > SCREEN_HEIGHT or my_car.x > SCREEN_WIDTH or my_car.y < 0 or my_car.x < 0:
        my_car.x, my_car.y = SCREEN_MIDDLE_X, SCREEN_MIDDLE_Y
    

    # If 'q' gets pressed close game
    if keys[pygame.K_q]:
        running = False

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()