import pygame
import gymnasium as gym
import numpy as np
from enum import Enum
from gymnasium import spaces
from .car import PlayerCar
from .track import LOGIC_TRACK, OB_MASK, FINISH_LINE_MASK, CP_MASKS

class Actions(Enum):
    COAST = 0
    ACCELERATE = 1
    ACCELERATE_LEFT = 2
    ACCELERATE_RIGHT = 3
    COAST_LEFT = 4
    COAST_RIGHT = 5

COOLDOWN_DURATION = 5000  # replaced when you switch to a step counter

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

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
        return {"steps": self.steps, "distance": self.distance}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.car = PlayerCar(3, 3)

        self.first_lap = True
        self.lap_started = False
        self.start_time = 0
        self.last_trigger_time = 0

        self.steps = 0
        self.distance = 0.0

        if self.render_mode == "human":
            self.render()
        return self._get_obs(), self._get_info()

    def step(self, action):
        up, left, right = self._action_to_controls[int(action)]
        car = self.car

        # TODO 1: apply the controls (reuse your old movement block)
        # TODO 2: update self.steps and self.distance
        # TODO 3: set terminated
        # TODO 4: set truncated (use a step limit, not wall-clock time)
        # TODO 5: set reward (your design)

        if self.render_mode == "human":
            self.render()
        return self._get_obs(), reward, terminated, truncated, self._get_info()

    # _check_finish_line stays exactly as it is for now

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