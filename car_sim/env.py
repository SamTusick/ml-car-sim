import pygame
from car import PlayerCar
from track import LOGIC_TRACK, OB_MASK, FINISH_LINE_MASK
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


# Lap time
COOLDOWN_DURATION = 5000  # 5 seconds in milliseconds

# Scren Constants 
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_MIDDLE_X = SCREEN_WIDTH / 2
SCREEN_MIDDLE_Y = SCREEN_HEIGHT / 2


# ------------- Environment -------------

class Env:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.reset()

    def reset(self):
        self.car = PlayerCar(3, 3)
        # Lap time
        self.first_lap = True
        self.lap_started = False
        self.start_time = 0
        self.last_trigger_time = 0

    def step(self, up=False, left=False, right=False):
        """Advance one frame. Returns an info dict: crashed, lap_time (seconds or None)."""
        car = self.car

        if up:
            car.move_forward()
        else:
            car.reduce_speed()
        if left:
            car.rotate(left=True)
        if right:
            car.rotate(right=True)

        lap_time = self._check_finish_line()

        # Track Limits
        crashed = car.collison(OB_MASK) is not None
        if crashed:
            car.stop()

        return {"crashed": crashed, "lap_time": lap_time}

    def _check_finish_line(self):
        current_time = pygame.time.get_ticks()  # Get current game time in ms
        lap_time = None

        if self.car.collison(FINISH_LINE_MASK) is not None:
            # Check if enough time has passed since the last cross to prevent double-triggering
            if current_time - self.last_trigger_time > COOLDOWN_DURATION or self.first_lap:

                if not self.lap_started:
                    # First time crossing: Start the lap
                    self.first_lap = False
                    self.start_time = current_time
                    self.lap_started = True
                    self.last_trigger_time = current_time
                    print('Start', self.start_time / 1000) # Convert to seconds for readability

                else:
                    # Second time crossing: Finish the lap
                    lap_time = (current_time - self.start_time) / 1000
                    self.lap_started = False # Reset for the next lap
                    self.last_trigger_time = current_time

                    print('Finish', current_time / 1000)
                    print('Lap Time: ', lap_time, 'seconds')

        return lap_time

    def render(self):
        self.screen.blit(LOGIC_TRACK, (0,0))
        self.car.draw(self.screen)
        pygame.display.update()

    def close(self):
        pygame.quit()
