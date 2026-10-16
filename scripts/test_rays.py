import math
import pygame
from car_sim.car import PlayerCar
from car_sim.track import OB_MASK
import car_sim.car as car_module
print(car_module.__file__)
print(PlayerCar.__mro__)
print("ray_cast" in dir(PlayerCar))

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
    for name, offset in [("left 60", math.pi / 3),
                         ("left 30", math.pi / 6),
                         ("ahead", 0.0),
                         ("right 30", -math.pi / 6),
                         ("right 60", -math.pi / 3)]:
        print(f"{name:>9}: {car.ray_cast(offset, OB_MASK)}")


if __name__ == "__main__":
    synthetic_tests()
    track_readings()