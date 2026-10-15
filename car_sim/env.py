import math
import pygame
import gymnasium as gym
import numpy as np
from enum import Enum
from gymnasium import spaces
from .car import PlayerCar
from .track import LOGIC_TRACK, OB_MASK, FINISH_LINE_MASK, FINISH_CENTER, CP_MASKS, cp_gate_points

class Actions(Enum):
    COAST = 0
    ACCELERATE = 1
    ACCELERATE_LEFT = 2
    ACCELERATE_RIGHT = 3
    COAST_LEFT = 4
    COAST_RIGHT = 5

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
# 3px per step for ~3600 px track -> 1200 steps * 2x/3x margin 
MAX_STEPS = 3000

class CarEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode=None):
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # TODO
        # PLACEHOLDER: replace with your ray design
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

        self.action_space = spaces.Discrete(len(Actions))

        # (up, left, right)
        self._action_to_controls = {
            Actions.COAST.value:            (False, False, False),
            Actions.ACCELERATE.value:       (True,  False, False),
            Actions.ACCELERATE_LEFT.value:  (True,  True,  False),
            Actions.ACCELERATE_RIGHT.value: (True,  False, True),
            Actions.COAST_LEFT.value:       (False, True,  False),
            Actions.COAST_RIGHT.value:      (False, False, True),
        }

        # Filled in later, so these exist before reset() runs
        self.window = None
        self.car = None

    def _get_obs(self):
        # TODO
        # PLACEHOLDER until the rays exist
        return np.zeros(self.observation_space.shape, dtype=np.float32)

    def _get_info(self):
        return {"finished": self.finished,"steps": self.steps, "gates_passed": self.next_gate, "distance_to_next_gate": self.distance_to_next_gate}

    def _update_distance_to_gate(self):
        car_x, car_y = self.car.get_center()
        if self.next_gate >= len(CP_MASKS):
            gate_x, gate_y = FINISH_CENTER
        else:
            gate_x, gate_y = cp_gate_points[self.next_gate]
        self.distance_to_next_gate = math.hypot(gate_x - car_x, gate_y - car_y) 

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.car = PlayerCar(3, 3)

        self.finished = False
        self.steps = 0
        # will be used to next gate and gates passed
        self.next_gate = 0
        self._update_distance_to_gate()
       

        if self.render_mode == "human":
            self.render()
        return self._get_obs(), self._get_info()

    def step(self, action):
        up, left, right = self._action_to_controls[int(action)]
        car = self.car
        terminated = False
        truncated = False
        reward = 0.0

        # 1: apply the controls (reuse your old movement block)
        if up:
            car.move_forward()
        else:
            car.reduce_speed()
        car.rotate(left=left, right=right)

        # 2: update steps, gate check, distance update
        self.steps += 1
        if self.next_gate < len(CP_MASKS):
            if car.collison(CP_MASKS[self.next_gate]) is not None:
                self.next_gate += 1
        self._update_distance_to_gate()

        # 3: set terminated
        if car.collison(OB_MASK):
            terminated = True
        if (self.next_gate >= len(CP_MASKS) and car.collison(FINISH_LINE_MASK)):
            terminated = True
            self.finished = True 

        # 4: set truncated (use a step limit)
        if self.steps >= MAX_STEPS:
            truncated = True

        if self.render_mode == "human":
            self.render()
        return self._get_obs(), reward, terminated, truncated, self._get_info()

    def render(self):
        if self.render_mode != "human":
            return
        if self.window is None:
            pygame.init()
            self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window.blit(LOGIC_TRACK, (0, 0))
        self.car.draw(self.window)
        pygame.display.update()

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
            self.window = None