import pygame
import math
from .helper_functs import blit_rotate_center, scale_image

MAX_SENSOR_DIST = 200
SENSOR_ANGLES = [-math.pi/3, -math.pi/6, 0.0, math.pi/6, math.pi/3] #[-60deg, -30deg, 0deg, 30deg, 60deg]
SENSOR_STEP = 5 # value to change

# ------------- Car -------------
class Car:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.turn_threshold = 0.5
        
    def rotate(self, left=False, right=False):
        if left and self.vel > self.turn_threshold:
            self.angle += self.rotation_vel
        elif right and self.vel > self.turn_threshold:
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
    
    def get_center(self):
        # float center; 
        return (self.x + self.img.get_width() / 2, self.y + self.img.get_height() / 2)

    def ray_cast(self, offset, mask, max_dist=MAX_SENSOR_DIST, step=SENSOR_STEP):
        cx, cy = self.get_center()                     
        heading = math.radians(self.angle) + offset            
        dx, dy = -math.sin(heading), -math.cos(heading)
        w, h = mask.get_size()

        for d in range(0, max_dist, step):
            px = int(cx + dx * d)
            py = int(cy + dy * d)
            if px >= w or px < 0 or py >= h or py < 0:                      
                return d
            if mask.get_at((px,py)) != 0:                       
                return d
        return max_dist

CAR = scale_image(pygame.image.load("assets/car.png"), 0.03)

class PlayerCar(Car):
    IMG = CAR
    #START_POS = (SCREEN_MIDDLE_X, SCREEN_MIDDLE_Y)
    START_POS = (30, 630)