import pygame
import math
import time

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

# Out of Bounds Mask
ob_color = pygame.Color(14,209,69)
threshold_target = (15,15,15,50)

OB_MASK = pygame.mask.from_threshold(TRACK, ob_color, threshold_target)

# Start/Finish Mask
finish_line_color = pygame.Color(0,0,0)
threshold_line_target = (2,2,2,255)

FINISH_LINE_MASK = pygame.mask.from_threshold(TRACK, finish_line_color, threshold_line_target)

# Lap time
lap_started = False
start_time = 0
cooldown_duration = 5000  # 5 seconds in milliseconds
last_trigger_time = 0

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

    def stop(self):
        self.acceleration = 0
        self.vel = 0
        self.rotation_vel = 0

    def collison(self, mask, x=0, y=0):
        rotated_car = pygame.transform.rotate(self.img, self.angle)
        new_rect = rotated_car.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center
            )
        car_mask = pygame.mask.from_surface(rotated_car)
        offset = (int(new_rect.x - x), int(new_rect.y - y))
        intersection_point = mask.overlap(car_mask, offset)
        return intersection_point


class PlayerCar(Car):
    IMG = CAR
    #START_POS = (SCREEN_MIDDLE_X, SCREEN_MIDDLE_Y)
    START_POS = (30, 630)

def draw(screen, player_car):
    screen.blit(TRACK, (0,0))
    player_car.draw(screen)
    pygame.display.update()

my_car = PlayerCar(3,3)
clock = pygame.time.Clock()
running = True

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
        moved = True
        my_car.move_forward()
    if keys[LEFT]:
        my_car.rotate(left=True)
    if keys[RIGHT]:
        my_car.rotate(right=True)

    if not moved:
        my_car.reduce_speed()

    # Start/ Finish
    current_time = pygame.time.get_ticks()  # Get current game time in ms

    if my_car.collison(FINISH_LINE_MASK) is not None:
        # Check if enough time has passed since the last cross to prevent double-triggering
        if current_time - last_trigger_time > cooldown_duration:
            
            if not lap_started:
                # First time crossing: Start the lap
                start_time = current_time
                lap_started = True
                last_trigger_time = current_time
                print('Start', start_time / 1000) # Convert to seconds for readability
                
            else:
                # Second time crossing: Finish the lap
                finish_time = current_time
                lap_time = finish_time - start_time
                lap_started = False # Reset for the next lap
                last_trigger_time = current_time
                
                print('Finish', finish_time / 1000)
                print('Lap Time: ', lap_time / 1000, 'seconds')

    # Track Limits
    if my_car.collison(OB_MASK) is not None:
        #print('Collide')
        my_car.stop()
    #else: 
    #    print("car is safe")

    # Off Screen Boundry Handling
    #if my_car.y > SCREEN_HEIGHT or my_car.x > SCREEN_WIDTH or my_car.y < 0 or my_car.x < 0:
    #    my_car.x, my_car.y = SCREEN_MIDDLE_X, SCREEN_MIDDLE_Y

    # If 'q' gets pressed close game
    if keys[pygame.K_q]:
        running = False

    clock.tick(60)


pygame.quit()