import math
import pygame
from car_sim.car import PlayerCar, SENSOR_ANGLES, SENSOR_STEP, MAX_SENSOR_DIST
from car_sim.track import OB_MASK, LOGIC_TRACK

def place_center(car, x, y):
    """Move the car so its center is at (x, y)."""
    cx, cy = car.get_center()
    car.x += x - cx
    car.y += y - cy

def synthetic_tests():
    # 200 x 200 empty mask with a solid wall on rows 0 to 62
    mask = pygame.mask.Mask((200, 200))
    for x in range(200):
        for y in range(63):
            mask.set_at((x, y), 1)

    car = PlayerCar(3, 3)
    car.angle = 0
    place_center(car, 100, 100)

    # Ray straight ahead (up): samples at y = 100, 95, ..., first red is y = 60
    got = car.ray_cast(0.0, mask)
    print(f"wall ahead: got {got}, expected 40")
    assert got == 40

    # Ray to the left (+pi/2): no wall, runs off the map at x < 0
    # samples at x = 100 - d, so d = 105 gives x = -5, first outside
    got = car.ray_cast(math.pi / 2, mask)
    print(f"off-map left: got {got}, expected 105")
    assert got == 105

    # Ray straight down (pi): no wall, runs off the map at y >= 200
    # samples at y = 100 + d, so d = 100 gives y = 200, first outside
    got = car.ray_cast(math.pi, mask)
    print(f"off-map down: got {got}, expected 100")
    assert got == 100

    # Clear mask and ray that stays inside: should return max_dist
    empty = pygame.mask.Mask((1000, 1000))
    place_center(car, 500, 500)
    got = car.ray_cast(0.0, empty)
    print(f"no hit: got {got}, expected 200")
    assert got == 200

    print("synthetic tests passed\n")


def track_readings():
    car = PlayerCar(3, 3)
    print(f"spawn center: {car.get_center()}, angle: {car.angle}")
    for offset in SENSOR_ANGLES:
        print(f"{math.degrees(offset):>6.0f} deg: {car.ray_cast(offset, OB_MASK)}")


def visual_test():
    """Drive with arrow keys and watch the rays. Esc/close to quit, R to reset."""
    pygame.init()
    screen = pygame.display.set_mode(LOGIC_TRACK.get_size())
    pygame.display.set_caption("Ray test")
    font = pygame.font.SysFont(None, 20)
    clock = pygame.time.Clock()
    car = PlayerCar(3, 3)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    car = PlayerCar(3, 3)

        keys = pygame.key.get_pressed()
        car.rotate(left=keys[pygame.K_LEFT], right=keys[pygame.K_RIGHT])
        if keys[pygame.K_UP]:
            car.move_forward()
        else:
            car.reduce_speed()

        screen.blit(LOGIC_TRACK, (0, 0))
        car.draw(screen)

        cx, cy = car.get_center()
        for i, offset in enumerate(SENSOR_ANGLES):
            dist = car.ray_cast(offset, OB_MASK)
            heading = math.radians(car.angle) + offset
            end = (cx - math.sin(heading) * dist, cy - math.cos(heading) * dist)
            color = (0, 255, 0) if dist >= MAX_SENSOR_DIST else (255, 255, 0)
            pygame.draw.line(screen, color, (cx, cy), end, 2)
            pygame.draw.circle(screen, (255, 0, 255), end, 4)
            label = font.render(f"{math.degrees(offset):.0f}: {dist}", True, (255, 255, 255), (0, 0, 0))
            screen.blit(label, (10, 10 + 18 * i))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    synthetic_tests()
    track_readings()
    visual_test()